from fastapi import FastAPI

from api import user, post, comment

app = FastAPI()

app.include_router(user.router)
app.include_router(post.router)
app.include_router(comment.router)