from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .config import settings

def add_cors(app: FastAPI) -> None:
    # For development: Allow all origins
    # TODO: Restrict this in production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for debugging
        allow_credentials=False,  # Must be False when allow_origins is ["*"]
        allow_methods=["*"],  # Allow all methods including OPTIONS
        allow_headers=["*"],  # Allow all headers
        expose_headers=["*"],
        max_age=3600,
    )