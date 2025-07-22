import os
import uuid
from typing import Annotated

from fastapi import UploadFile, File


async def upload_file(file: Annotated[UploadFile, File(...)]):
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"

    # 📌 최상위 static/uploads 경로
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    upload_dir = os.path.join(root_dir, "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    save_path = os.path.join(upload_dir, filename)
    with open(save_path, "wb") as f:
        f.write(await file.read())

    # 클라이언트에서 접근할 URL 반환
    return {"url": f"/static/uploads/{filename}"}