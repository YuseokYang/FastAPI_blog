import os
import cloudinary
import cloudinary.uploader
from typing import Annotated
from fastapi import UploadFile, File, HTTPException
from dotenv import load_dotenv

load_dotenv()

# Cloudinary 설정: 환경변수에서 가져오기
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

async def upload_file(file: Annotated[UploadFile, File(...)]):
    try:
        result = cloudinary.uploader.upload(file.file)
        return {"url": result["secure_url"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Cloudinary 업로드 실패")




















# async def upload_file(file: Annotated[UploadFile, File(...)]):
#     ext = file.filename.split(".")[-1]
#     filename = f"{uuid.uuid4().hex}.{ext}"
#
#     # 📌 최상위 static/uploads 경로
#     root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#     upload_dir = os.path.join(root_dir, "static", "uploads")
#     os.makedirs(upload_dir, exist_ok=True)
#
#     save_path = os.path.join(upload_dir, filename)
#     with open(save_path, "wb") as f:
#         f.write(await file.read())
#
#     # 클라이언트에서 접근할 URL 반환
#     return {"url": f"/static/uploads/{filename}"}