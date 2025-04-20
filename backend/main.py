# File: backend/main.py
"""
Main FastAPI application entry point.
Configures and runs the API server.
"""
from fastapi import FastAPI
import uvicorn
# TODO: Import routes

app = FastAPI(title="Restaurant Sales Prediction API")

# TODO: Configure routes
# TODO: Add CORS middleware
# TODO: Add exception handlers

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)