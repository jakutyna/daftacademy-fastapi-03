from fastapi import FastAPI

from .routers import shop

app = FastAPI()
app.include_router(shop.router)


@app.get("/")
def index():
    return {"message": "Hello!"}
