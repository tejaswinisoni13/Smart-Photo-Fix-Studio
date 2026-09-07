from flask import Flask, request, send_file, render_template_string
from rembg import remove
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import cv2
import numpy as np
import zipfile
import os
from io import BytesIO

app = Flask(__name__)

HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Photo Fix Studio</title>
    <style>
    :root {
        --bg: #f4f5fa; --panel: #ffffff; --border: #e6e8f0;
        --ink: #1c1e26; --ink-dim: #7a7f8c; --accent: #6c5ce7;
        --accent-soft: #efeaff; --ok: #2fae66; --err: #e0533d;
        --radius: 14px;
        font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    [data-theme="dark"] {
        --bg: #14151c; --panel: #1c1e29; --border: #2b2d3a;
        --ink: #eef0f6; --ink-dim: #9297a8; --accent: #8b7cf6; --accent-soft: #2a2645;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--ink); transition: background 0.2s, color 0.2s; }
    .app { display: grid; grid-template-columns: 250px 1fr; min-height: 100vh; }

    .sidebar { background: var(--panel); border-right: 1px solid var(--border); padding: 22px 16px; display: flex; flex-direction: column; }
    .logo { display: flex; align-items: center; gap: 10px; padding: 0 8px 20px; }
    .logo-icon { width: 34px; height: 34px; border-radius: 10px; background: var(--accent); color: white; display: flex; align-items: center; justify-content: center; font-size: 16px; }
    .logo h1 { margin: 0; font-size: 16px; }
    .logo span { font-size: 11px; color: var(--ink-dim); }
    .menu-title { font-size: 11px; letter-spacing: 0.06em; color: var(--ink-dim); padding: 10px 10px 6px; }
    .tools { display: flex; flex-direction: column; gap: 3px; flex: 1; }
    .tool-btn {
        display: flex; align-items: center; gap: 10px; text-align: left; width: 100%;
        background: transparent; border: none; color: var(--ink-dim); padding: 10px 12px;
        border-radius: 10px; font-size: 13.5px; cursor: pointer;
    }
    .tool-btn:hover { background: var(--accent-soft); color: var(--ink); }
    .tool-btn.active { background: var(--accent-soft); color: var(--accent); font-weight: 600; }
    .sidebar-bottom { padding-top: 14px; }
    .secure-box { display: flex; gap: 10px; align-items: center; background: var(--accent-soft); border-radius: 12px; padding: 12px; font-size: 12px; }
    .secure-box b { display: block; font-size: 12.5px; }
    .secure-box small { color: var(--ink-dim); }

    .main { padding: 26px 34px; }
    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 22px; }
    .small-heading { color: var(--accent); font-size: 11px; letter-spacing: 0.08em; margin: 0 0 6px; }
    .header h2 { margin: 0 0 8px; font-size: 24px; }
    .subtitle { color: var(--ink-dim); font-size: 13.5px; margin: 0; max-width: 480px; }
    .theme-button { display: flex; align-items: center; gap: 6px; background: var(--panel); border: 1px solid var(--border); color: var(--ink); padding: 8px 14px; border-radius: 10px; cursor: pointer; font-size: 13px; }

    .upload-area {
        border: 1.5px dashed var(--border); border-radius: var(--radius); background: var(--panel);
        padding: 30px; text-align: center; cursor: pointer; margin-bottom: 20px;
    }
    .upload-area.drag { border-color: var(--accent); background: var(--accent-soft); }
    .upload-icon { font-size: 22px; color: var(--accent); margin-bottom: 8px; }
    .upload-text h3 { margin: 0 0 4px; font-size: 15px; }
    .upload-text p { margin: 4px 0; color: var(--ink-dim); font-size: 13px; }
    #browseBtn { background: none; border: none; color: var(--accent); font-weight: 600; cursor: pointer; text-decoration: underline; font-size: 13px; }
    .upload-text small { color: var(--ink-dim); font-size: 11px; }
    .selected-badge { margin-top: 12px; font-size: 12px; color: var(--ink-dim); }

    .workspace { display: grid; grid-template-columns: 320px 1fr; gap: 20px; }
    .control-panel, .preview-panel { background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; }
    .panel-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
    .panel-header p { margin: 0; font-size: 10.5px; letter-spacing: 0.06em; color: var(--ink-dim); }
    .panel-header h3 { margin: 2px 0 0; font-size: 16px; }
    .ready { font-size: 10px; background: var(--accent-soft); color: var(--accent); padding: 3px 8px; border-radius: 20px; font-weight: 700; height: fit-content; }
    .tool-description { color: var(--ink-dim); font-size: 12.5px; margin: 8px 0 16px; }
    .tool-fields { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }
    .field { display: flex; flex-direction: column; gap: 5px; }
    .field label { font-size: 11.5px; color: var(--ink-dim); display: flex; justify-content: space-between; }
    .field input, .field select {
        background: var(--bg); border: 1px solid var(--border); color: var(--ink);
        padding: 7px 10px; border-radius: 8px; font-size: 13px;
    }
    .process-button {
        width: 100%; background: var(--accent); color: white; border: none; padding: 11px;
        border-radius: 10px; font-weight: 600; font-size: 13.5px; cursor: pointer;
        display: flex; align-items: center; justify-content: center; gap: 6px;
    }
    .process-button:disabled { opacity: 0.5; cursor: default; }
    .status { display: flex; align-items: center; gap: 8px; margin-top: 14px; font-size: 12px; color: var(--ink-dim); }
    .status-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--ink-dim); }
    .status-dot.ok { background: var(--ok); }
    .status-dot.err { background: var(--err); }

    .preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
    .preview-header p { margin: 0; font-size: 10.5px; letter-spacing: 0.06em; color: var(--ink-dim); }
    .preview-header h3 { margin: 2px 0 0; font-size: 16px; }
    .download-button { background: var(--accent); color: white; border: none; padding: 9px 16px; border-radius: 10px; font-weight: 600; font-size: 12.5px; cursor: pointer; }
    .download-button:disabled { opacity: 0.4; cursor: default; }
    .preview-container { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .preview-box { background: var(--bg); border: 1px solid var(--border); border-radius: 12px; padding: 12px; }
    .preview-title { display: flex; justify-content: space-between; font-size: 10.5px; color: var(--ink-dim); margin-bottom: 8px; letter-spacing: 0.05em; }
    .image-stage { position: relative; min-height: 220px; display: flex; align-items: center; justify-content: center; }
    .empty-state { text-align: center; color: var(--ink-dim); font-size: 12px; }
    .empty-state div { font-size: 26px; margin-bottom: 6px; }
    .image-stage img { max-width: 100%; max-height: 260px; border-radius: 8px; display: none; }
    .loader { position: absolute; inset: 0; display: none; flex-direction: column; align-items: center; justify-content: center; gap: 8px; background: rgba(0,0,0,0.03); border-radius: 8px; font-size: 12px; color: var(--ink-dim); }
    .spinner { width: 24px; height: 24px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }

    .info-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 20px; }
    .info-card { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 14px; display: flex; gap: 10px; align-items: center; }
    .info-card b { display: block; font-size: 13px; }
    .info-card small { color: var(--ink-dim); font-size: 11.5px; }

    footer { text-align: center; color: var(--ink-dim); font-size: 12px; margin-top: 24px; padding: 16px 0; }

    @media (max-width: 900px) {
        .app { grid-template-columns: 1fr; }
        .sidebar { flex-direction: row; overflow-x: auto; }
        .workspace { grid-template-columns: 1fr; }
        .preview-container { grid-template-columns: 1fr; }
        .info-row { grid-template-columns: 1fr; }
    }
    </style>
</head>

<body>

<div class="app">

    <aside class="sidebar">
        <div class="logo">
            <div class="logo-icon">✦</div>
            <div><h1>PhotoFix</h1><span>AI Studio</span></div>
        </div>

        <div class="menu-title">IMAGE TOOLS</div>

        <div class="tools" id="toolsList">
            <button class="tool-btn active" data-tool="remove-bg"><span>✂</span>Remove Background</button>
            <button class="tool-btn" data-tool="enhance"><span>✨</span>Auto Enhance</button>
            <button class="tool-btn" data-tool="denoise"><span>◌</span>Noise Reduction</button>
            <button class="tool-btn" data-tool="resize"><span>↔</span>Resize Image</button>
            <button class="tool-btn" data-tool="id-photo"><span>▣</span>ID Photo Mode</button>
            <button class="tool-btn" data-tool="batch-process"><span>▦</span>Batch Processing</button>
            <button class="tool-btn" data-tool="apply-filter"><span>◐</span>Filters</button>
            <button class="tool-btn" data-tool="compress"><span>⇩</span>Compress Image</button>
            <button class="tool-btn" data-tool="change-bg-color"><span>●</span>Background Color</button>
            <button class="tool-btn" data-tool="blur-background"><span>◒</span>Blur Background</button>
            <button class="tool-btn" data-tool="reduce-glare"><span>☼</span>Reduce Glare</button>
        </div>

        <div class="sidebar-bottom">
            <div class="secure-box">
                <span class="secure-icon">🔒</span>
                <div><b>Private Processing</b><small>Your images stay secure</small></div>
            </div>
        </div>
    </aside>

    <main class="main">
        <header class="header">
            <div>
                <p class="small-heading">AI POWERED IMAGE EDITOR</p>
                <h2>Make every photo <strong>look better.</strong></h2>
                <p class="subtitle">Enhance, edit, resize and transform your images in one simple workspace.</p>
            </div>
            <button id="themeToggle" class="theme-button">
                <span id="themeIcon">☾</span>
                <span id="themeText">Dark</span>
            </button>
        </header>

        <section class="upload-area" id="dropzone">
            <input type="file" id="fileInput" accept="image/*" multiple hidden>
            <div class="upload-icon">↑</div>
            <div class="upload-text">
                <h3>Drop your image here</h3>
                <p>or <button id="browseBtn">browse files</button></p>
                <small>PNG • JPG • JPEG • WEBP</small>
            </div>
            <div class="selected-badge" id="selectedBadge">No image selected</div>
        </section>

        <section class="workspace">
            <div class="control-panel">
                <div class="panel-header">
                    <div><p>SELECTED TOOL</p><h3 id="toolTitle">Remove Background</h3></div>
                    <span class="ready">READY</span>
                </div>
                <p class="tool-description" id="toolDescription">Remove the background from your image using AI.</p>
                <div class="tool-fields" id="toolFields"></div>
                <button class="process-button" id="processBtn" disabled>
                    <span>✦</span><span id="processText">Process Image</span>
                </button>
                <div class="status" id="statusBox">
                    <span class="status-dot" id="statusDot"></span>
                    <span id="statusText">Upload an image to get started.</span>
                </div>
            </div>

            <div class="preview-panel">
                <div class="preview-header">
                    <div><p>LIVE PREVIEW</p><h3>Before & After</h3></div>
                    <button class="download-button" id="downloadBtn" disabled>↓ Download</button>
                </div>
                <div class="preview-container">
                    <div class="preview-box">
                        <div class="preview-title"><span>ORIGINAL</span><span id="originalSize">—</span></div>
                        <div class="image-stage">
                            <div class="empty-state" id="originalEmpty"><div>◫</div><span>Your original image<br>will appear here</span></div>
                            <img id="originalPreview" alt="Original Image">
                        </div>
                    </div>
                    <div class="preview-box">
                        <div class="preview-title"><span>PROCESSED</span><span id="resultSize">—</span></div>
                        <div class="image-stage">
                            <div class="empty-state" id="resultEmpty"><div>✦</div><span>Your processed image<br>will appear here</span></div>
                            <img id="resultPreview" alt="Processed Image">
                            <div class="loader" id="loader"><div class="spinner"></div><span>AI processing...</span></div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="info-row">
            <div class="info-card"><span>⚡</span><div><b>Fast Processing</b><small>Quick image transformation</small></div></div>
            <div class="info-card"><span>🎨</span><div><b>11 Powerful Tools</b><small>Edit images your way</small></div></div>
            <div class="info-card"><span>⬇</span><div><b>Easy Download</b><small>Save your processed image</small></div></div>
        </section>

        <footer>
            <span>AI Photo Fix Studio</span> • <span>11 Image Tools</span> • <span>Smart & Simple</span>
        </footer>
    </main>
</div>

<script>
    const tools = {
        'remove-bg':      { title: 'Remove Background', desc: 'Remove the background from your image using AI.', multi: false, fields: [] },
        'enhance':        { title: 'Auto Enhance', desc: 'Adjust brightness, contrast and sharpness.', multi: false,
                             fields: [
                                { name: 'brightness', label: 'Brightness', type: 'range', min: 0.5, max: 2, step: 0.1, value: 1.2 },
                                { name: 'contrast', label: 'Contrast', type: 'range', min: 0.5, max: 2, step: 0.1, value: 1.2 },
                                { name: 'sharpness', label: 'Sharpness', type: 'range', min: 0.5, max: 2, step: 0.1, value: 1.5 }
                             ] },
        'denoise':        { title: 'Noise Reduction', desc: 'Reduce noise in blurry or grainy photos.', multi: false, fields: [] },
        'resize':         { title: 'Resize Image', desc: 'Resize the image to a specific width and height.', multi: false,
                             fields: [
                                { name: 'width', label: 'Width (px)', type: 'number', value: 600 },
                                { name: 'height', label: 'Height (px)', type: 'number', value: 600 }
                             ] },
        'id-photo':       { title: 'ID Photo Mode', desc: 'White background + standard 600x600 crop.', multi: false, fields: [] },
        'batch-process':  { title: 'Batch Processing', desc: 'Select multiple images to process at once, get a ZIP.', multi: true, fields: [] },
        'apply-filter':   { title: 'Filters', desc: 'Apply a quick style filter to your photo.', multi: false,
                             fields: [ { name: 'type', label: 'Filter', type: 'select', value: 'bw', options: ['bw','sepia','vintage','cool','warm'] } ] },
        'compress':       { title: 'Compress Image', desc: 'Shrink the image to a target file size (KB).', multi: false,
                             fields: [ { name: 'target_kb', label: 'Target size (KB)', type: 'number', value: 200 } ] },
        'change-bg-color':{ title: 'Background Color', desc: 'Replace the background with a solid color.', multi: false,
                             fields: [ { name: 'color', label: 'Color', type: 'select', value: 'white', options: ['white','black','grey'] } ] },
        'blur-background':{ title: 'Blur Background', desc: 'Keep the subject sharp, blur everything behind it.', multi: false,
                             fields: [ { name: 'blur_strength', label: 'Blur strength', type: 'range', min: 5, max: 45, step: 2, value: 25 } ] },
        'reduce-glare':   { title: 'Reduce Glare', desc: 'Reduce bright flash/glare spots (best-effort).', multi: false, fields: [] }
    };

    let currentTool = 'remove-bg';
    let selectedFiles = [];
    let currentResultURL = null;

    const fileInput = document.getElementById('fileInput');
    const dropzone = document.getElementById('dropzone');
    const browseBtn = document.getElementById('browseBtn');
    const selectedBadge = document.getElementById('selectedBadge');
    const toolTitle = document.getElementById('toolTitle');
    const toolDescription = document.getElementById('toolDescription');
    const toolFields = document.getElementById('toolFields');
    const processBtn = document.getElementById('processBtn');
    const processText = document.getElementById('processText');
    const statusText = document.getElementById('statusText');
    const statusDot = document.getElementById('statusDot');
    const downloadBtn = document.getElementById('downloadBtn');
    const originalPreview = document.getElementById('originalPreview');
    const originalEmpty = document.getElementById('originalEmpty');
    const originalSize = document.getElementById('originalSize');
    const resultPreview = document.getElementById('resultPreview');
    const resultEmpty = document.getElementById('resultEmpty');
    const resultSize = document.getElementById('resultSize');
    const loader = document.getElementById('loader');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const themeText = document.getElementById('themeText');

    browseBtn.addEventListener('click', (e) => { e.preventDefault(); fileInput.click(); });
    dropzone.addEventListener('click', () => fileInput.click());

    ['dragover', 'dragleave', 'drop'].forEach(evt => {
        dropzone.addEventListener(evt, e => {
            e.preventDefault();
            e.stopPropagation();
            if (evt === 'dragover') dropzone.classList.add('drag');
            else dropzone.classList.remove('drag');
        });
    });
    dropzone.addEventListener('drop', e => handleFiles(e.dataTransfer.files));
    fileInput.addEventListener('change', () => handleFiles(fileInput.files));

    function handleFiles(fileList) {
        selectedFiles = Array.from(fileList);
        if (selectedFiles.length === 0) return;

        selectedBadge.textContent = selectedFiles.length === 1
            ? selectedFiles[0].name
            : `${selectedFiles.length} images selected`;

        processBtn.disabled = false;

        if (!tools[currentTool].multi) {
            const reader = new FileReader();
            reader.onload = e => {
                originalPreview.src = e.target.result;
                originalPreview.style.display = 'block';
                originalEmpty.style.display = 'none';
                originalSize.textContent = (selectedFiles[0].size / 1024).toFixed(0) + ' KB';
            };
            reader.readAsDataURL(selectedFiles[0]);
        }

        resultPreview.style.display = 'none';
        resultEmpty.style.display = 'block';
        resultSize.textContent = '—';
        downloadBtn.disabled = true;
        currentResultURL = null;
    }

    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTool = btn.dataset.tool;
            const t = tools[currentTool];

            toolTitle.textContent = t.title;
            toolDescription.textContent = t.desc;
            fileInput.multiple = t.multi;

            toolFields.innerHTML = '';
            t.fields.forEach(f => {
                const wrap = document.createElement('div');
                wrap.className = 'field';
                const label = document.createElement('label');
                label.textContent = f.label;
                wrap.appendChild(label);

                let input;
                if (f.type === 'select') {
                    input = document.createElement('select');
                    f.options.forEach(opt => {
                        const o = document.createElement('option');
                        o.value = opt; o.textContent = opt;
                        if (opt === f.value) o.selected = true;
                        input.appendChild(o);
                    });
                } else {
                    input = document.createElement('input');
                    input.type = f.type;
                    input.value = f.value;
                    if (f.type === 'range') { input.min = f.min; input.max = f.max; input.step = f.step; }
                }
                input.id = 'field_' + f.name;
                wrap.appendChild(input);
                toolFields.appendChild(wrap);
            });

            processBtn.disabled = selectedFiles.length === 0;
        });
    });

    processBtn.addEventListener('click', async () => {
        if (selectedFiles.length === 0) return;

        const t = tools[currentTool];
        const formData = new FormData();

        if (t.multi) {
            selectedFiles.forEach(f => formData.append('images', f));
        } else {
            formData.append('image', selectedFiles[0]);
        }
        t.fields.forEach(f => formData.append(f.name, document.getElementById('field_' + f.name).value));

        processBtn.disabled = true;
        processText.textContent = 'Processing...';
        loader.style.display = 'flex';
        statusText.textContent = 'AI is processing your image...';
        statusDot.className = 'status-dot';

        try {
            const res = await fetch('/' + currentTool, { method: 'POST', body: formData });
            if (!res.ok) throw new Error('Server returned ' + res.status);

            const blob = await res.blob();
            currentResultURL = URL.createObjectURL(blob);

            if (currentTool === 'batch-process') {
                statusText.textContent = 'Batch processed! Downloading ZIP...';
                statusDot.className = 'status-dot ok';
                const a = document.createElement('a');
                a.href = currentResultURL;
                a.download = 'processed_images.zip';
                document.body.appendChild(a);
                a.click();
                a.remove();
            } else {
                resultPreview.src = currentResultURL;
                resultPreview.style.display = 'block';
                resultEmpty.style.display = 'none';
                resultSize.textContent = (blob.size / 1024).toFixed(0) + ' KB';
                downloadBtn.disabled = false;
                statusText.textContent = 'Done! Ready to download.';
                statusDot.className = 'status-dot ok';
            }
        } catch (err) {
            statusText.textContent = 'Something went wrong: ' + err.message;
            statusDot.className = 'status-dot err';
        } finally {
            processBtn.disabled = false;
            processText.textContent = 'Process Image';
            loader.style.display = 'none';
        }
    });

    downloadBtn.addEventListener('click', () => {
        if (!currentResultURL) return;
        const a = document.createElement('a');
        a.href = currentResultURL;
        a.download = 'processed_image.png';
        document.body.appendChild(a);
        a.click();
        a.remove();
    });

    let isDark = false;
    themeToggle.addEventListener('click', () => {
        isDark = !isDark;
        document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
        themeIcon.textContent = isDark ? '☀' : '☾';
        themeText.textContent = isDark ? 'Light' : 'Dark';
    });
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)


# ---------- 1. Background Removal ----------
@app.route('/remove-bg', methods=['POST'])
def remove_bg_endpoint():
    file = request.files['image']
    img = Image.open(file)
    result = remove(img)
    img_io = BytesIO()
    result.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 2. Enhance ----------
@app.route('/enhance', methods=['POST'])
def enhance_endpoint():
    file = request.files['image']
    img = Image.open(file)

    brightness = float(request.form.get('brightness', 1.2))
    contrast = float(request.form.get('contrast', 1.2))
    sharpness = float(request.form.get('sharpness', 1.5))

    if img.mode == "RGBA":
        img = img.convert("RGB")

    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)

    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 3. Denoise ----------
@app.route('/denoise', methods=['POST'])
def denoise_endpoint():
    file = request.files['image']
    img = Image.open(file).convert("RGB")
    img_array = np.array(img)
    denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 10, 10, 7, 21)
    result = Image.fromarray(denoised)

    img_io = BytesIO()
    result.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 4. Resize ----------
@app.route('/resize', methods=['POST'])
def resize_endpoint():
    file = request.files['image']
    width = int(request.form.get('width', 600))
    height = int(request.form.get('height', 600))

    img = Image.open(file)
    resized = img.resize((width, height))

    img_io = BytesIO()
    resized.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 5. ID Photo Mode ----------
@app.route('/id-photo', methods=['POST'])
def id_photo_endpoint():
    file = request.files['image']
    img = Image.open(file)

    no_bg = remove(img)
    white_bg = Image.new("RGBA", no_bg.size, "WHITE")
    white_bg.paste(no_bg, (0, 0), no_bg)
    id_photo = white_bg.convert("RGB").resize((600, 600))

    img_io = BytesIO()
    id_photo.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 6. Batch Process ----------
@app.route('/batch-process', methods=['POST'])
def batch_process_endpoint():
    files = request.files.getlist('images')
    zip_io = BytesIO()

    with zipfile.ZipFile(zip_io, 'w') as zipf:
        for f in files:
            img = Image.open(f)
            processed = remove(img)
            img_bytes = BytesIO()
            processed.save(img_bytes, format='PNG')
            base_name = os.path.splitext(f.filename)[0]
            zipf.writestr(f"processed_{base_name}.png", img_bytes.getvalue())

    zip_io.seek(0)
    return send_file(zip_io, mimetype='application/zip', as_attachment=True, download_name='processed_images.zip')


# ---------- 7. Filters ----------
@app.route('/apply-filter', methods=['POST'])
def apply_filter_endpoint():
    file = request.files['image']
    filter_type = request.form.get('type', 'bw')

    img = Image.open(file).convert("RGB")

    if filter_type == 'bw':
        result = ImageOps.grayscale(img).convert("RGB")
    elif filter_type == 'sepia':
        img_array = np.array(img).astype(np.float64)
        sepia_matrix = np.array([[0.393, 0.769, 0.189],
                                  [0.349, 0.686, 0.168],
                                  [0.272, 0.534, 0.131]])
        sepia_img = img_array @ sepia_matrix.T
        sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
        result = Image.fromarray(sepia_img)
    elif filter_type == 'vintage':
        result = ImageEnhance.Color(img).enhance(0.6)
        result = ImageEnhance.Contrast(result).enhance(0.9)
        result = ImageEnhance.Brightness(result).enhance(1.1)
    elif filter_type == 'cool':
        r, g, b = img.split()
        b = ImageEnhance.Brightness(b).enhance(1.2)
        r = ImageEnhance.Brightness(r).enhance(0.9)
        result = Image.merge("RGB", (r, g, b))
    elif filter_type == 'warm':
        r, g, b = img.split()
        r = ImageEnhance.Brightness(r).enhance(1.2)
        b = ImageEnhance.Brightness(b).enhance(0.85)
        result = Image.merge("RGB", (r, g, b))
    else:
        result = img

    img_io = BytesIO()
    result.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 8. Compress to target KB ----------
@app.route('/compress', methods=['POST'])
def compress_endpoint():
    file = request.files['image']
    target_kb = int(request.form.get('target_kb', 200))

    img = Image.open(file).convert("RGB")
    quality = 95
    img_io = BytesIO()

    while quality > 5:
        img_io.seek(0)
        img_io.truncate(0)
        img.save(img_io, format='JPEG', quality=quality)
        size_kb = img_io.tell() / 1024
        if size_kb <= target_kb:
            break
        quality -= 5

    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg', download_name='compressed.jpg')


# ---------- 9. Background color choice ----------
@app.route('/change-bg-color', methods=['POST'])
def change_bg_color_endpoint():
    file = request.files['image']
    color = request.form.get('color', 'white')

    color_map = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'grey': (200, 200, 200),
        'gray': (200, 200, 200),
    }
    bg_color = color_map.get(color, color)

    img = Image.open(file)
    no_bg = remove(img)

    solid_bg = Image.new("RGBA", no_bg.size, bg_color)
    solid_bg.paste(no_bg, (0, 0), no_bg)
    result = solid_bg.convert("RGB")

    img_io = BytesIO()
    result.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 10. Background blur ----------
@app.route('/blur-background', methods=['POST'])
def blur_background_endpoint():
    file = request.files['image']
    blur_strength = int(request.form.get('blur_strength', 25))

    img = Image.open(file).convert("RGB")

    no_bg = remove(img)
    alpha_mask = no_bg.split()[3]

    blurred = img.filter(ImageFilter.GaussianBlur(blur_strength))
    result = Image.composite(img, blurred, alpha_mask)

    img_io = BytesIO()
    result.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


# ---------- 11. Glasses glare reduction (best-effort) ----------
@app.route('/reduce-glare', methods=['POST'])
def reduce_glare_endpoint():
    file = request.files['image']
    img = Image.open(file).convert("RGB")
    img_array = np.array(img)

    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    _, glare_mask = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    glare_mask = cv2.dilate(glare_mask, np.ones((5, 5), np.uint8), iterations=1)

    result_array = cv2.inpaint(img_array, glare_mask, 5, cv2.INPAINT_TELEA)
    result = Image.fromarray(result_array)

    img_io = BytesIO()
    result.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7860))
    app.run(host='0.0.0.0', port=port)
