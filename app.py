from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image, ImageOps
import numpy as np, cv2, os, uuid, time, math
from werkzeug.utils import secure_filename

ROOT=os.path.dirname(os.path.abspath(__file__))
UPLOAD=os.path.join(ROOT,"uploads"); OUTPUT=os.path.join(ROOT,"outputs")
os.makedirs(UPLOAD,exist_ok=True); os.makedirs(OUTPUT,exist_ok=True)
ALLOWED={"png","jpg","jpeg","webp","bmp"}
app=Flask(__name__); app.config["MAX_CONTENT_LENGTH"]=12*1024*1024

def open_image(path):
    with Image.open(path) as im:
        im=ImageOps.exif_transpose(im)
        return im.convert("RGB").copy()

def pil_bgr(im): return cv2.cvtColor(np.array(im.convert("RGB")),cv2.COLOR_RGB2BGR)
def bgr_pil(a): return Image.fromarray(cv2.cvtColor(np.clip(a,0,255).astype("uint8"),cv2.COLOR_BGR2RGB))

def enhance(im,method,p):
    bgr=pil_bgr(im)
    strength=float(np.clip(float(p.get("strength",1)),.2,2))
    gamma=float(np.clip(float(p.get("gamma",.8)),.3,2))
    clip=float(np.clip(float(p.get("clipLimit",2)),1,5))
    sharp=float(np.clip(float(p.get("sharpness",1)),0,3))
    if method in ("auto","clahe"):
        lab=cv2.cvtColor(bgr,cv2.COLOR_BGR2LAB); l,a,b=cv2.split(lab)
        l=cv2.createCLAHE(clipLimit=clip,tileGridSize=(8,8)).apply(l)
        out=cv2.cvtColor(cv2.merge([l,a,b]),cv2.COLOR_LAB2BGR)
        if method=="auto":
            out=cv2.fastNlMeansDenoisingColored(out,None,3,3,7,21)
            blur=cv2.GaussianBlur(out,(0,0),1.2)
            out=cv2.addWeighted(out,1+.35*sharp,blur,-.35*sharp,0)
    elif method=="histogram":
        ycc=cv2.cvtColor(bgr,cv2.COLOR_BGR2YCrCb); y,cr,cb=cv2.split(ycc)
        out=cv2.cvtColor(cv2.merge([cv2.equalizeHist(y),cr,cb]),cv2.COLOR_YCrCb2BGR)
    elif method=="gamma":
        table=np.array([min(255,max(0,((i/255)**gamma)*255)) for i in range(256)],dtype=np.uint8)
        out=cv2.LUT(bgr,table)
    elif method=="denoise":
        amount=3+int(5*strength)
        out=cv2.fastNlMeansDenoisingColored(bgr,None,amount,amount,7,21)
    elif method=="sharpen":
        blur=cv2.GaussianBlur(bgr,(0,0),1.2)
        out=cv2.addWeighted(bgr,1+.8*sharp,blur,-.8*sharp,0)
    elif method=="brightness":
        out=cv2.convertScaleAbs(bgr,alpha=1,beta=round((strength-1)*80))
    else: raise ValueError("Unknown method")
    return bgr_pil(out)

def metrics(orig,processed,original_bytes,output_bytes):
    a=np.array(orig.convert("RGB"),dtype=np.float32); b=np.array(processed.convert("RGB"),dtype=np.float32)
    mse=float(np.mean((a-b)**2)); psnr=100 if mse==0 else 20*math.log10(255/math.sqrt(mse))
    gray=cv2.cvtColor(np.array(processed),cv2.COLOR_RGB2GRAY)
    return {"mse":round(mse,2),"psnr":round(psnr,2),"contrast":round(float(gray.std()),2),
            "sharpness":round(float(cv2.Laplacian(gray,cv2.CV_64F).var()),2),
            "originalBytes":original_bytes,"processedBytes":output_bytes}

@app.get("/")
def home(): return render_template("index.html")

@app.post("/api/enhance")
def api_enhance():
    start=time.perf_counter()
    if "image" not in request.files: return jsonify(error="Please choose an image first."),400
    f=request.files["image"]
    if not f.filename: return jsonify(error="Please choose an image first."),400
    ext=f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else ""
    if ext not in ALLOWED: return jsonify(error="Use PNG, JPG, JPEG, WEBP or BMP images."),400
    raw=f.read()
    if not raw: return jsonify(error="The selected file is empty."),400
    if len(raw)>12*1024*1024: return jsonify(error="Maximum image size is 12 MB."),413
    token=uuid.uuid4().hex[:12]; filename=secure_filename(f.filename) or "image"
    original_path=os.path.join(UPLOAD,f"{token}_{filename}")
    with open(original_path,"wb") as out: out.write(raw)
    try:
        original=open_image(original_path)
        if original.width*original.height>25_000_000:
            os.remove(original_path); return jsonify(error="Image is too large in dimensions. Use an image under 25 megapixels."),413
        method=request.form.get("method","auto").lower()
        processed=enhance(original,method,request.form)
        outname=f"{token}_enhanced.png"; outpath=os.path.join(OUTPUT,outname)
        processed.save(outpath,"PNG",optimize=True)
        m=metrics(original,processed,len(raw),os.path.getsize(outpath))
        return jsonify(success=True,originalUrl=f"/uploads/{os.path.basename(original_path)}",
          processedUrl=f"/outputs/{outname}",downloadUrl=f"/outputs/{outname}",filename=filename,
          width=original.width,height=original.height,method=method,
          processingMs=round((time.perf_counter()-start)*1000),metrics=m)
    except Exception:
        app.logger.exception("Image processing failed")
        try: os.remove(original_path)
        except OSError: pass
        return jsonify(error="Could not process this image. Try another valid image."),400

@app.get("/uploads/<path:name>")
def serve_upload(name): return send_from_directory(UPLOAD,name)
@app.get("/outputs/<path:name>")
def serve_output(name): return send_from_directory(OUTPUT,name)
@app.errorhandler(413)
def too_large(_): return jsonify(error="File too large. Maximum size is 12 MB."),413

if __name__=="__main__": app.run(host="127.0.0.1",port=5000,debug=False)
