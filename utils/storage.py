"""
Storage utility for saving/loading JSON data
"""
import json
import os
from datetime import datetime
from config import DATA_DIR


def ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def save_json(data, filename):
    """
    Save data to JSON file in the data directory
    
    Args:
        data: Dictionary to save
        filename: Name of the file (without path)
    
    Returns:
        str: Full path to saved file
    """
    ensure_data_dir()
    filepath = os.path.join(DATA_DIR, filename)

    # Add metadata
    data['_metadata'] = {
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filepath


def load_json(filename):
    """
    Load data from JSON file
    
    Args:
        filename: Name of the file (without path)
    
    Returns:
        dict: Loaded data or None if file doesn't exist
    """
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_data_files():
    """List all JSON files in data directory"""
    ensure_data_dir()
    return [f for f in os.listdir(DATA_DIR) if f.endswith('.json')]
