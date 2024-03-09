from fastapi import FastAPI, Request, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from urllib.parse import urljoin
from file_stream import range_requests_response

video_folder_path = "assets/video/"
fastapi_base_url = "http://127.0.0.1:8000/"

app = FastAPI()

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

@app.get("/")
def greet():
    return {"message": "Welcome to FastAPI video exmaple."} 

@app.post("/video")
async def create_upload_file(file: UploadFile):
    f = open(f'{video_folder_path+file.filename}', 'wb')
    content = await file.read()
    f.write(content)
    # return the url to the uploaded file relative to the root of the domain
    video_url=fastapi_base_url+"get_video_by_name/"
    return {"video_url": urljoin(video_url, file.filename)}


@app.get("/get_video_by_name/{video_name}")
def get_video(video_name:str, request: Request):
    if video_name is not None:
        video_url=video_folder_path+video_name
        return range_requests_response(
            request, file_path=video_url, content_type="video/mp4"
        )
    else:
        raise HTTPException(status_code=404, detail="No videos found!")

