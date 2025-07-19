from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from api import user, post, comment

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://chuteol.netlify.app/",
    # "https://fastapi-blog-j1cs.onrender.com",   # 필요하다면 백엔드 자신을 적어도 무방
    # "https://your-frontend.vercel.app",         # 추후 프론트 배포 주소
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # 개발 중엔 ["*"] 로 풀어도 OK
    allow_credentials=True,       # JWT를 헤더로만 쓰면 False 여도 무방
    allow_methods=["*"],          # 필요한 경우 ["GET", "POST", ...] 로 좁힐 수 있음
    allow_headers=["*"],
)


app.include_router(user.router)
app.include_router(post.router)
app.include_router(comment.router)