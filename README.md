# Image Extractor & Archiver Web App

This project is a Dockerized web application that automates the extraction and archiving of images from a given URL. It uses a headless browser (via Selenium and Chrome) to render pages, waits for key elements to load, and then parses the HTML with BeautifulSoup to extract image URLs. The application downloads these images to a temporary folder, compresses them into a ZIP file, and serves both the individual images and the ZIP archive through a RESTful API.

## Key Features

- **Dynamic Image Extraction:**  
  Automatically processes user-provided URLs to load pages dynamically and extract target images.

- **Headless Browser Rendering:**  
  Uses Selenium with a headless Chrome browser to handle JavaScript-heavy pages, ensuring that all images load properly.

- **HTML Parsing & Data Cleanup:**  
  Utilizes BeautifulSoup to parse HTML and identify the correct elements for image extraction.  
  Implements cleanup logic to keep the temporary storage within defined limits.

- **File Download & Archiving:**  
  Downloads images to a temporary folder and creates a ZIP archive for easy downloading of all images at once.

- **Docker & Docker Compose:**  
  Fully containerized using Docker. Multi-service orchestration (frontend and backend) is managed via Docker Compose for easy deployment across development, LAN, and external environments.

- **Reverse Proxy Integration:**  
  Uses Nginx as a reverse proxy to serve the frontend and route API requests to the backend seamlessly.

## Technologies Used

- **Backend:** Python, Flask, Selenium, BeautifulSoup, Requests, zipfile
- **Frontend:** *(Your choice of frontend framework, served via Docker/Nginx)*
- **Containerization:** Docker & Docker Compose
- **Reverse Proxy:** Nginx
- **External Exposure:** Cloudflare Tunnel (for exposing the app to external networks)

## Build and Run

```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
docker compose up --build
```
