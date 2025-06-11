from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from rest.routes import router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.options("/{path:path}")
async def options_handler(path: str):
    return JSONResponse(content={}, status_code=204)

@app.get("/")
async def exec():
    return JSONResponse(content={"message": "Hello, World!"}, status_code=200)