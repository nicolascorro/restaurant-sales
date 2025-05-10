# File: backend/utils/helpers.py
"""
Helper functions for the application.
"""
import os
import uuid
from datetime import datetime
import shutil
from pathlib import Path
import json
from fastapi import UploadFile

def generate_file_id() -> str:
    """Generates unique file identifier."""
    return str(uuid.uuid4())

async def save_uploaded_file(file: UploadFile, filename: str) -> str:
    """Saves uploaded file to disk and returns the saved file path."""
    try:
        # Create the data directory if it doesn't exist
        data_dir = get_data_directory()
        
        # Generate a unique filename to prevent collisions
        file_id = generate_file_id()
        file_extension = Path(filename).suffix
        saved_filename = f"{file_id}{file_extension}"
        
        # Full path for saving
        save_path = os.path.join(data_dir, saved_filename)
        
        # Save the file
        contents = await file.read()
        with open(save_path, 'wb') as buffer:
            buffer.write(contents)
        
        return save_path
    except Exception as e:
        raise Exception(f"Error saving file: {str(e)}")

def get_data_directory() -> str:
    """Returns path to data directory, creating it if it doesn't exist."""
    base_dir = Path(__file__).parent.parent.parent  # Get project root
    data_dir = base_dir / 'data' / 'uploads'
    
    # Create the directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return str(data_dir)

def get_processed_data_directory() -> str:
    """Returns path to processed data directory."""
    base_dir = Path(__file__).parent.parent.parent  # Get project root
    processed_dir = base_dir / 'data' / 'processed'
    
    # Create the directory if it doesn't exist
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    return str(processed_dir)

def save_processing_metadata(file_id: str, metadata: dict) -> str:
    """Saves metadata about processed files."""
    metadata_dir = Path(get_processed_data_directory()) / 'metadata'
    metadata_dir.mkdir(exist_ok=True, parents=True)
    
    metadata_file = metadata_dir / f"{file_id}_metadata.json"
    
    # Add timestamp to metadata
    metadata['processing_timestamp'] = datetime.now().isoformat()
    
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return str(metadata_file)

def load_processing_metadata(file_id: str) -> dict:
    """Loads metadata for a processed file."""
    metadata_dir = Path(get_processed_data_directory()) / 'metadata'
    metadata_file = metadata_dir / f"{file_id}_metadata.json"
    
    if not metadata_file.exists():
        raise FileNotFoundError(f"Metadata file not found for {file_id}")
    
    with open(metadata_file, 'r') as f:
        return json.load(f)

def cleanup_old_files(days_old: int = 7):
    """Removes files older than specified days."""
    data_dir = Path(get_data_directory())
    processed_dir = Path(get_processed_data_directory())
    
    cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
    
    # Clean up both uploaded and processed files
    for directory in [data_dir, processed_dir]:
        for file_path in directory.glob('*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()