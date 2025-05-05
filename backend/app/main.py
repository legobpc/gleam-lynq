from fastapi import FastAPI
from app.selenium_runner import run_selenium

app = FastAPI()

@app.get("/")
def root():
    return {"message": "SEO backend is running 🚀"}

@app.get("/test-selenium")
def test_selenium():
    title = run_selenium()
    return {"page_title": title}