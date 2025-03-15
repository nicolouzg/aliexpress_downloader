from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import os
import requests
import zipfile
import re
import time

app = Flask(__name__)
CORS(app)

TEMP_FOLDER = os.path.join(os.getcwd(), "temp")
os.makedirs(TEMP_FOLDER, exist_ok=True)

MAX_FOLDER_SIZE_MB = 100

def format_folder_name(name, max_length=64):
    """Convert folder names to a URL-safe format."""
    name = re.sub(r'[^\w\s-]', '', name)  # Remove special characters
    name = re.sub(r'\s+', '_', name).strip()  # Replace spaces with underscores
    return name[:max_length]  # Trim to max_length

def get_folder_size(folder):
    """Calculate the total size of the folder in MB."""
    total_size = 0
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # Convert bytes to MB

def cleanup_temp_folder():
    """Remove the oldest files from the temp folder if size exceeds MAX_FOLDER_SIZE_MB."""
    while get_folder_size(TEMP_FOLDER) > MAX_FOLDER_SIZE_MB:
        files = []
        for dirpath, _, filenames in os.walk(TEMP_FOLDER):
            for f in filenames:
                file_path = os.path.join(dirpath, f)
                files.append((file_path, os.path.getctime(file_path)))

        if files:
            files.sort(key=lambda x: x[1])  # Sort by creation time (oldest first)
            oldest_file = files[0][0]
            os.remove(oldest_file)
            print(f"Deleted old file: {oldest_file}")

@app.route('/api/process_url', methods=['POST'])
def process_url():
    data = request.get_json()
    url = data.get('url')
    user_locale = data.get('locale', 'en-US')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Set up Selenium WebDriver with headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument(f"--lang={user_locale}")
    chrome_options.add_argument("--no-sandbox")  # Required for Docker
    chrome_options.add_argument("--disable-dev-shm-usage")  # Prevent crashes in Docker
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get(url)

        # Ensure the page is fully loaded
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

        # Wait until the target element is visible and has text
        folder_name_xpath = "/html/body/div[2]/div/div[8]/div[2]/div[1]/div/div/div[2]/h1"
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, folder_name_xpath))
        )
        WebDriverWait(driver, 15).until(
            lambda d: d.find_element(By.XPATH, folder_name_xpath).text.strip() != ""
        )

        # Extract and format folder name
        folder_name_element = driver.find_element(By.XPATH, folder_name_xpath)
        raw_folder_name = folder_name_element.text.strip()
        folder_name = format_folder_name(raw_folder_name)

        if not folder_name:
            return jsonify({'error': 'Extracted folder name is empty'}), 400

        # Ensure the folder structure
        output_folder = os.path.join(TEMP_FOLDER, folder_name)
        os.makedirs(output_folder, exist_ok=True)

        # Scroll down to trigger lazy loading
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Allow images to load

        # Wait until at least one image is loaded
        image_xpath = "/html/body/div[2]/div/div[8]/div[2]/div[2]/div/div/div/div[1]//img"
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, image_xpath))
        )

        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, 'html.parser')
        target_div = soup.select_one('div:nth-of-type(2) > div > div:nth-of-type(8) > div:nth-of-type(2) > div:nth-of-type(2) > div > div > div > div:nth-of-type(1)')

        if not target_div:
            return jsonify({'error': 'No target div found'}), 400

        # Extract image URLs
        image_urls = list(set(img['src'] for img in target_div.find_all('img', src=True)))

        if not image_urls:
            return jsonify({'error': 'No images found inside the target div'}), 400

        # Download images
        downloaded_images = []
        for img_url in image_urls:
            if not img_url.startswith("http"):
                img_url = "https:" + img_url

            img_name = os.path.basename(img_url.split("?")[0])  # Extract filename
            img_path = os.path.join(output_folder, img_name)

            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(img_url, stream=True, timeout=10, headers=headers)

                if response.status_code == 200:
                    with open(img_path, 'wb') as file:
                        for chunk in response.iter_content(1024):
                            file.write(chunk)
                    downloaded_images.append(f"{folder_name}/{img_name}")  # Store relative path
                else:
                    downloaded_images.append(f'Failed: {img_url}')
            except requests.exceptions.RequestException as e:
                downloaded_images.append(f'Error: {img_url} - {e}')

        # Create ZIP file inside /temp/
        zip_filename = f"{folder_name}.zip"
        zip_path = os.path.join(TEMP_FOLDER, zip_filename)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img in downloaded_images:
                img_full_path = os.path.join(TEMP_FOLDER, img)
                if os.path.exists(img_full_path):  # Ensure the file exists
                    zipf.write(img_full_path, os.path.relpath(img_full_path, TEMP_FOLDER))

        # Clean up temp folder if needed
        cleanup_temp_folder()

        return jsonify({
            'message': 'Download and archiving completed',
            'images': downloaded_images,
            'zip_file': zip_filename,  # Return just the filename, not full path
        })
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    finally:
        driver.quit()

@app.route('/api/images/<path:folder>/<path:filename>')
def serve_image(folder, filename):
    return send_from_directory(os.path.join(TEMP_FOLDER, folder), filename, mimetype='image/jpeg', as_attachment=True)

@app.route('/api/zip/<path:filename>')
def serve_zip(filename):
    return send_from_directory(TEMP_FOLDER, filename, as_attachment=True)

@app.route('/')
def home():
    return jsonify({"server_ip": request.host.split(":")[0]})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
