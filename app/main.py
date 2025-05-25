from fastapi import FastAPI

app = FastAPI(title="Lu Estilo API")

@app.get("/")
def read_root():
    return {"message": "API da Lu Estilo está no ar!"}
