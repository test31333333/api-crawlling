
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import json
import shutil

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

html_file_path = Path(__file__).parent / 'index.html'

json_file_path = Path(__file__).parent / 'test.json'

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(html_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

@app.get("/news/", response_class=JSONResponse)
async def read_news():
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_location = f"static/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"info": f"Image {file.filename} uploaded successfully!"}
@app.get("/download/{filename}")
async def download_image(filename: str):
    file_location = f"static/{filename}"
    return FileResponse(file_location, media_type='image/jpeg', filename=filename)
