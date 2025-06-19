# 🎥 FastAPI Video Streaming Example

A minimal FastAPI project that demonstrates **video streaming** capabilities using Python.  
Shows how to serve large media files efficiently — great for building media apps, e-learning platforms, or secure video APIs.

---

## 🔧 Tech Stack

- **FastAPI** – Modern web framework
- **Starlette** – ASGI middleware and response utilities
- **Uvicorn** – ASGI server
- **Range Requests** – Partial content serving (seek support)

---

## 📂 Features

- Serve video files with **byte-range support**
- Use `StreamingResponse` for large file efficiency
- Works with MP4 and other media formats
- Designed for future expansion (e.g. auth, analytics)

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yavuzakyazici/fastapi_video.git
cd fastapi_video
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Add sample video
Put an .mp4 file into the /videos folder (e.g., demo.mp4)

5. Run the app
```
uvicorn main:app --reload
```
Go to: http://localhost:8000/video/demo.mp4

🧪 Endpoints
GET /video/{filename}
Streams a video file with byte-range support (seekable in browser).

Example:

```bash
curl -i -H "Range: bytes=0-" http://localhost:8000/video/demo.mp4
```

📎 Notes
- Range header is used to enable partial downloads (streaming)
- StreamingResponse sends chunks of the file on the fly
- Easily extensible for:
- User-based video access control
- Watermarking
- Streaming logs / analytics

👤 Author
Yavuz Akyazıcı – Full-stack developer & creator of [Jazz-A-Minute (JAM)](https://jazzaminute.com/)

This project is a simplified demo of the secure video delivery backend used in JAM.
