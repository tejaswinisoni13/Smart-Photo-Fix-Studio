# Smart Photo Fix Studio

### AI-Based Image Enhancement & Editing Tool

Smart Photo Fix Studio is a web-based image processing application that provides multiple photo enhancement and editing operations through a simple interface.

The application combines Python, Flask, OpenCV, Pillow, and rembg to perform image processing directly through the web application.

## Live Demo

**[Open Smart Photo Fix Studio](https://smart-photo-fix-studio.onrender.com)**

> Note: The application is deployed on Render's free tier, so the first request after inactivity may take some time to load.

---

## Overview

Smart Photo Fix Studio is designed to simplify common photo editing and enhancement tasks without requiring complex desktop editing software.

Users can upload an image, select an operation, process the image, and download the resulting file.

### Key Features

- Background Removal
- Image Enhancement
- Image Denoising
- Image Resizing
- ID Photo Mode
- Batch Image Processing
- Image Filters
- Image Compression
- Background Color Replacement
- Background Blur
- Glare Reduction

---

## How It Works

```text
Upload Image
      
Select Editing Operation
      
Flask Backend
      
Image Processing
      
OpenCV / Pillow / rembg
      
Processed Image
      
Download Result
```

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core application logic |
| Flask | Web application backend |
| OpenCV | Image processing and computer vision |
| Pillow | Image manipulation |
| rembg | AI-based background removal |
| NumPy | Numerical image processing |
| ONNX Runtime | Runtime for AI-based processing |
| HTML / CSS / JavaScript | Frontend interface |
| Docker | Application containerization |
| Render | Cloud deployment |

---

## Project Architecture

```text
Smart-Photo-Fix-Studio/
app.py
requirements.txt
Dockerfil
.gitignore
README.md
```

### Backend

The Flask backend handles:

- Image upload requests
- Image processing operations
- Background removal
- Image transformation
- Result generation
- File downloads

### Frontend

The frontend provides:

- Image upload interface
- Editing tool selection
- Processing controls
- Result preview
- Download functionality

---

## Supported Operations

### 1. Background Removal
Automatically removes the background from an uploaded image using `rembg`.

### 2. Image Enhancement
Improves image appearance using image enhancement techniques.

### 3. Denoising
Reduces unwanted noise from images.

### 4. Resize
Allows images to be resized according to the selected dimensions.

### 5. ID Photo Mode
Creates an ID-photo style image with a standard white background.

### 6. Batch Processing
Processes multiple uploaded images and provides the processed files together.

### 7. Filters
Applies different image filters for visual enhancement.

### 8. Compression
Reduces image file size while maintaining useful image quality.

### 9. Background Color
Removes the existing background and replaces it with a selected color.

### 10. Background Blur
Separates the foreground from the background and applies background blur.

### 11. Glare Reduction
Reduces excessive brightness or glare in images.

---

## Privacy

The application is designed to process uploaded images in memory rather than maintaining an application database for storing user images.

No user account or permanent image storage is required for using the core editing features.

---

## Deployment

The application is containerized using Docker and deployed as a web service on Render.

**Live Application:**  
https://smart-photo-fix-studio.onrender.com

---



## Project Purpose

The objective of Smart Photo Fix Studio is to provide an accessible and easy-to-use platform for performing common image enhancement and editing operations through a single web interface.

The project demonstrates the practical use of:

- Web application development
- Image processing
- Computer vision
- AI-based background removal
- Backend API endpoints
- Docker containerization
- Cloud deployment

---

## Future Improvements

- User authentication
- More advanced image enhancement models
- Additional editing tools
- Improved batch processing
- Image quality comparison
- Mobile-responsive improvements
- Cloud-based scalable processing
- Processing history

---



## Team
Tejaswini Soni (AI / Python — background removal, enhancement, filters, compression, denoising)


Nidhi Panchaya (Web Development — frontend UI/UX, live filter previews, integration)


## License

This project was developed as an academic/project work.
