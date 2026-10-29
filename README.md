# Smart Image Enhancement Studio — ClarityLab

A complete, runnable Digital Image Processing website using Flask + OpenCV + NumPy + Pillow + HTML/CSS/JavaScript.

## Included features
- Image upload and drag-and-drop
- Real backend processing (not simulated)
- Smart enhancement: CLAHE + mild denoising + sharpening
- CLAHE adaptive contrast
- Histogram equalization
- Gamma correction
- Noise reduction
- Image sharpening (unsharp masking)
- Brightness adjustment
- Original / enhanced side-by-side and single-image views
- Download enhanced image as PNG
- PSNR, MSE, contrast and processing time metrics
- Responsive design and upload validation

## Run on Windows (VS Code)
1. Extract this ZIP and open the folder in VS Code.
2. Open Terminal > New Terminal.
3. Run:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks venv activation, use a Command Prompt terminal and run `.venv\Scripts\activate.bat`.

4. Open `http://127.0.0.1:5000` in Chrome/Edge.

## Run on Ubuntu/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```
Then open `http://127.0.0.1:5000`.

## Project layout
```text
Smart_Image_Enhancement_Studio/
├── app.py
├── requirements.txt
├── README.md
├── templates/index.html
├── static/style.css
├── static/app.js
├── uploads/
├── outputs/
└── tests/test_app.py
```

## DIP concepts demonstrated
- CLAHE / adaptive histogram enhancement
- Histogram equalization
- Gamma correction and intensity transformation
- Non-local means denoising
- Unsharp-mask sharpening
- MSE and PSNR image comparison
- Contrast and sharpness statistics

## Metrics note
MSE and PSNR compare processed pixels with original pixels. Since enhancement deliberately changes pixel values, a lower PSNR does not necessarily indicate worse visual quality. Contrast is grayscale intensity standard deviation.

## Optional moderate ML addition
If the instructor permits ML, a small classifier could be added later to categorize input images as low-light, low-contrast, noisy or blurry using engineered image features. The core project intentionally focuses on DIP and does not depend on AI.

## Troubleshooting
- `ModuleNotFoundError`: activate `.venv`, then `pip install -r requirements.txt`.
- Port 5000 busy: change port in `app.py` to 5001 and open `http://127.0.0.1:5001`.
- Unsupported image: use JPG, PNG, WEBP or BMP, below 12 MB.
- Do not open the HTML directly. Run `python app.py` so the backend is available.
