from fastapi import FastAPI

app = FastAPI(title="Academic RAG System")

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "healthy",
        "service": "academic-backend",
        "version": "0.1.0"
    }