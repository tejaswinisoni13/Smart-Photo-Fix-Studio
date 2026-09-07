---
title: Smart Photo Fix Studio
emoji: 🖼️
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Smart Photo Fix Studio
## 🚀 Live Demo

🔗 [Smart Photo Fix Studio](https://smart-photo-fix-studio.onrender.com)

An AI-based image enhancement and editing tool built with Flask, rembg, OpenCV, and Pillow.

## Features
- Background removal (AI)
- Background color replacement (white / black / grey)
- Background blur (keep subject sharp)
- Filters (B&W, Sepia, Vintage, Cool, Warm)
- Brightness / contrast / sharpness enhancement
- Noise reduction (denoise)
- Best-effort glasses glare reduction
- Compress to a target file size (KB)
- Resize
- ID Photo Mode (600x600, white background)
- Batch processing (multiple images -> ZIP)

## Privacy
All processing happens in memory. No uploaded or processed image is ever saved to disk on the server.

## Tech Stack
Flask, rembg (U2-Net / BRIA background removal model), OpenCV, Pillow, NumPy.

## Team
Tejaswini (AI / Python — background removal, enhancement, filters, compression, denoising)
Nidhi (Web Development — frontend UI/UX, live filter previews, integration)
