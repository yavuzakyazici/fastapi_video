An example streaming file/video for FastAPI.
This example demonstrates how to add a streaming file support to FastAPI with some extra capabilities.
This mini example shows how to declare static files directory for the app,
how to upload file to that directory,
how to stream from that directory and
how to send out 304 unmodified header once the file is cached.

To get it working on your machine you can clone the repository.
You can use the included requirements.txt to install dependencies with pip.

Here is our main.py with "/video" route for uploading video to assets/video directory
main.py has also a route for getting the video.
Here is what it looks like.
```py
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
```

Here is our file_stream.py
Thanks to angel-langdon for the original reusable video streamer code.
I added streaming with partial 206 header and eTag support.
eTag was generated from from last_modified and file_size with md5_hexdigest function.
This way, if file size or last_modified changes, so does the eTag.

```py
import os
from typing import BinaryIO
from starlette._compat import md5_hexdigest
from fastapi import HTTPException, Request, status
from fastapi.responses import StreamingResponse, Response
from datetime import datetime

def send_bytes_range_requests(
    file_obj: BinaryIO, start: int, end: int, chunk_size: int = 8*1024
):
    """Send a file in chunks using Range Requests specification RFC7233

    `start` and `end` parameters are inclusive due to specification
    """
    with file_obj as f:
        f.seek(start)
        while (pos := f.tell()) <= end:
            read_size = min(chunk_size, end + 1 - pos)
            yield f.read(read_size)


def _get_range_header(range_header: str, file_size: int) -> tuple[int, int]:
    def _invalid_range():
        return HTTPException(
            status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail=f"Invalid request range (Range:{range_header!r})",
        )

    try:
        h = range_header.replace("bytes=", "").split("-")
        start = int(h[0]) if h[0] != "" else 0
        end = int(h[1]) if h[1] != "" else file_size - 1
    except ValueError:
        raise _invalid_range()

    if start > end or start < 0 or end > file_size - 1:
        raise _invalid_range()
    return start, end


def range_requests_response(
    request: Request, file_path: str, content_type: str
):
    """Returns StreamingResponse using Range Requests of a given file"""

    file_size = os.stat(file_path).st_size
    range_header = request.headers.get("range")

    """Compose etag from last_modified and file_size"""
    last_modified = datetime.fromtimestamp(os.stat(file_path).st_mtime).strftime("%a, %d %b %Y %H:%M:%S")
    etag_base = str(last_modified) + "-" + str(file_size)
    etag = f'"{md5_hexdigest(etag_base.encode(), usedforsecurity=False)}"'

    """Check if the browser sent etag matches the videos etag"""
    request_if_non_match_etag = request.headers.get("if-none-match")

    """if there is a match return 304 unmodified instead of 206 response without video file"""
    if request_if_non_match_etag == etag:
        headers = {
            "cache-control": "public, max-age=86400, stale-while-revalidate=2592000",
            "etag" : etag,
            "last-modified":str(last_modified),
        }
        status_code = status.HTTP_304_NOT_MODIFIED
        return Response(None, status_code=status_code, headers=headers)

    headers = {
        "etag" : etag,
        "content-type": content_type,
        "accept-ranges": "bytes",
        "content-encoding": "identity",
        "content-length": str(file_size),
        "access-control-expose-headers": (
        "content-type, accept-ranges, content-length, "
        "content-range, content-encoding"
        ),
    }
    start = 0
    end = file_size - 1
    status_code = status.HTTP_200_OK


    if range_header is not None:
        start, end = _get_range_header(range_header, file_size)
        size = end - start + 1
        headers["content-length"] = str(size)
        headers["content-range"] = f"bytes {start}-{end}/{file_size}"
        status_code = status.HTTP_206_PARTIAL_CONTENT

    return StreamingResponse(
        send_bytes_range_requests(open(file_path, mode="rb"), start, end),
        headers=headers,
        status_code=status_code,
    )
```
First request gets 200 response fpr the file..
<img width="774" alt="1" src="https://github.com/yavuzakyazici/fastapi_video/assets/148442912/dd97add5-7bed-4fad-976b-984e9c58cb91">

First time you download the video file clearly shows 206 partial header meaning streaming with smaller chunks.
<img width="777" alt="2" src="https://github.com/yavuzakyazici/fastapi_video/assets/148442912/6e2e76ab-7dc7-4036-a92a-3ad6c5f55c6a">

Server also sends an eTag along with 206 header..
<img width="774" alt="3" src="https://github.com/yavuzakyazici/fastapi_video/assets/148442912/83ebc6cc-8c84-4f2e-bbde-70d3cdb143c8">


Second time, if the browser finds a matching eTag, server sends back 304 unmodified header.
this is done via the if-none-match header
<img width="774" alt="4" src="https://github.com/yavuzakyazici/fastapi_video/assets/148442912/2cdef557-65bf-4968-9e33-8efe40b40e62">
<img width="774" alt="5" src="https://github.com/yavuzakyazici/fastapi_video/assets/148442912/1ac47a38-7230-4402-973a-cf8019bcb71a">

You can see it in the code clearly here:
```py
 """Check if the browser sent etag matches the videos etag"""
    request_if_non_match_etag = request.headers.get("if-none-match")

    """if there is a match return 304 unmodified instead of 206 response without video file"""
    if request_if_non_match_etag == etag:
        headers = {
            "cache-control": "public, max-age=86400, stale-while-revalidate=2592000",
            "etag" : etag,
            "last-modified":str(last_modified),
        }
        status_code = status.HTTP_304_NOT_MODIFIED
        return Response(None, status_code=status_code, headers=headers)
```
If there is no matching eTag found this means file is modified since eTag was and MD5 based on last-modified and the file size.
Which you can also see clearly in the code here:
```py
   """Compose etag from last_modified and file_size"""
    last_modified = datetime.fromtimestamp(os.stat(file_path).st_mtime).strftime("%a, %d %b %Y %H:%M:%S")
    etag_base = str(last_modified) + "-" + str(file_size)
    etag = f'"{md5_hexdigest(etag_base.encode(), usedforsecurity=False)}"'
```

However, if the eTag is the same ( look at the code above ) 304 unmodified header is sent and cached video is used.

Unfortunately does not work on Safari meaning Safari does not send if-none-match header.
However, I tested on Chrome, Opera and Mozilla Developer edition and it works :)

I hope this helps someone :)

