"use client";
import React, { useState } from 'react';
import axios from 'axios';
import { 
  Container, 
  TextField, 
  Button, 
  Typography, 
  Grid, 
  Card, 
  CardMedia, 
  IconButton, 
  Box, 
  CircularProgress, 
  LinearProgress 
} from '@mui/material';
import { Download, Search } from '@mui/icons-material';

function App() {
  const [url, setUrl] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [images, setImages] = useState([]);
  const [zipFile, setZipFile] = useState('');
  const [loading, setLoading] = useState(false); // 🔹 Track loading state
  
  // Determine backend IP dynamically
  const host = window.location.hostname;

  const backendURL = `http://${host}/api`;
  
  const handleSubmit = async () => {
    setLoading(true); // 🔹 Start loading
    setResponseMessage(''); // Clear previous messages
    setImages([]); // Reset images

    try {
      const result = await axios.post(`${backendURL}/process_url`, {
        url, 
        locale: navigator.language 
      });
    
      setResponseMessage(result.data.message);
      
      setImages(result.data.images.map(img => 
        `${backendURL}/images/${encodeURIComponent(img)}`
      ));
      
      setZipFile(`${backendURL}/zip/${encodeURIComponent(result.data.zip_file)}`);
    } catch (error) {
      setResponseMessage(error.response?.data?.error || 'An error occurred');
    }

    setLoading(false); // 🔹 Stop loading
  };

  return (
    <Box 
      sx={{ 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center', 
        justifyContent: 'flex-start', 
        minHeight: '100vh', 
        width: '96vw',  
        paddingTop: 4,
        px: 2  
      }}
    >
      <Typography variant="h4" gutterBottom align="center">
        AliExpress Image Downloader
      </Typography>

      {/* Search Bar */}
      <Box 
        sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          width: '100%', 
          maxWidth: '900px', 
          gap: '10px' 
        }}
      >
        <TextField
          fullWidth
          label="Enter the URL"
          variant="outlined"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleSubmit} 
          sx={{ height: '56px', minWidth: '56px' }}
          disabled={loading} // 🔹 Disable button when loading
        >
          {loading ? <CircularProgress size={24} color="inherit" /> : <Search />}
        </Button>
      </Box>

      {/* 🔹 Linear Progress Bar when loading */}
      {loading && <LinearProgress sx={{ width: '100%', maxWidth: '900px', mt: 2 }} />}

      <Typography variant="body1" sx={{ mt: 2, textAlign: 'center' }}>
        {responseMessage}
      </Typography>

      {/* Display Images if available */}
      {images.length > 0 && !loading && (
        <Box sx={{ textAlign: 'center', width: '100%', maxWidth: '1200px' }}>
          <Typography variant="h5" sx={{ mt: 3 }}>
            Downloaded Images:
          </Typography>
          <Grid container spacing={2} sx={{ mt: 2, justifyContent: 'center' }}>
            {images.map((image, index) => (
              <Grid item xs={6} sm={4} md={3} key={index}>
                <Card sx={{ position: 'relative' }}>
                  <CardMedia
                    component="img"
                    image={image}
                    alt={`img-${index}`}
                    sx={{ height: 140 }}
                  />
                  <IconButton 
                    component="a" 
                    href={image} 
                    download 
                    sx={{ 
                      position: 'absolute', 
                      bottom: 8, 
                      right: 8, 
                      bgcolor: 'primary.main',  
                      color: 'white',  
                      transition: 'all 0.3s ease-in-out', 

                      '&:hover': { 
                        color: 'white',  
                        bgcolor: 'primary.main', 
                        transform: 'scale(1.2)', 
                      }
                    }}
                  >
                    <Download />
                  </IconButton>
                </Card>
              </Grid>
            ))}
          </Grid>
          <Button 
            variant="contained" 
            color="primary" 
            sx={{ mt: 3 }} 
            href={zipFile} 
            download
          >
            Download All
          </Button>
        </Box>
      )}
    </Box>
  );
}

export default App;
