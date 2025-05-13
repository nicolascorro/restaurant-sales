# File: backend/main.py
"""
Main FastAPI application entry point.
Configures and runs the API server.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes import router

app = FastAPI(title="Restaurant Sales Prediction API")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://restaurant-sales.vercel.app/", "http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router with correct prefix
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)