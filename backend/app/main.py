from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.selenium_runner import run_selenium
from app.endpoint import domain

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(domain.router, prefix="/domain")

@app.get("/")
def root():
    return {"message": "SEO backend is running 🚀"}

@app.get("/test-selenium")
def test_selenium():
    title = run_selenium()
    return {"page_title": title}