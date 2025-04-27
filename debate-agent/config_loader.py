import os
import json
from typing import Dict, List, Any, Optional
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_input_dir() -> None:
    """Create input directory if it doesn't exist"""
    input_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input')
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
        logger.info(f"Created input directory: {input_dir}")
    return input_dir

def load_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from the specified JSON file or use default path.
    
    Args:
        config_file: Path to configuration file, or None to use default
        
    Returns:
        Dict containing the configuration
    """
    # If no config file provided, use default path
    if not config_file:
        input_dir = ensure_input_dir()
        config_file = os.path.join(input_dir, 'input.json')
    
    # Check if file exists
    if not os.path.exists(config_file):
        logger.warning(f"Config file not found: {config_file}")
        logger.info("Creating default configuration file...")
        create_default_config(config_file)
    
    # Load configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        logger.info(f"Configuration loaded successfully from {config_file}")
        validate_config(config)
        return config
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file: {config_file}")
        raise
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate that the configuration has the required fields
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises exception otherwise
    """
    # Required top-level keys
    required_keys = ["topic", "position_x", "position_y"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")
    
    # Position X should have name and role_description
    if not isinstance(config["position_x"], dict):
        raise ValueError("position_x should be an object with name and role_description")
    if "name" not in config["position_x"] or "role_description" not in config["position_x"]:
        raise ValueError("position_x requires name and role_description")
    
    # Position Y should be a list with at least 4 entries
    if not isinstance(config["position_y"], list):
        raise ValueError("position_y should be a list of objects")
    if len(config["position_y"]) < 4:
        raise ValueError("position_y requires at least 4 entries")
    
    # Each position Y entry should have name and role_description
    for i, pos_y in enumerate(config["position_y"]):
        if not isinstance(pos_y, dict):
            raise ValueError(f"position_y[{i}] should be an object")
        if "name" not in pos_y or "role_description" not in pos_y:
            raise ValueError(f"position_y[{i}] requires name and role_description")
    
    return True

def create_default_config(config_file: str) -> None:
    """
    Create a default configuration file
    
    Args:
        config_file: Path to save the default configuration
    """
    default_config = {
        "topic": "Does God exist?",
        "position_x": {
            "name": "Atheist Advocate",
            "role_description": "You are representing the Atheist position in a debate on God's existence.\nYour core values include: empirical evidence, scientific method, and rational thinking.\nFocus on lack of evidence, scientific explanations, and logical arguments.\nWhen responding, maintain a respectful tone while firmly defending your position.",
            "model": "llama3:latest"
        },
        "position_y": [
            {
                "name": "Theist Expert 1",
                "role_description": "You are representing the Theist position in a debate on God's existence.\nYour core values include: faith, spiritual experience, and religious tradition.\nFocus on cosmological arguments, personal experience, and moral foundations.\nWhen responding, maintain a respectful tone while firmly defending your position.",
                "model": "llama3:latest"
            },
            {
                "name": "Theist Expert 2",
                "role_description": "You are representing the Theist position in a debate on God's existence.\nYour core values include: faith, spiritual experience, and religious tradition.\nFocus on cosmological arguments, personal experience, and moral foundations.\nWhen responding, maintain a respectful tone while firmly defending your position.",
                "model": "llama3:latest"
            },
            {
                "name": "Theist Expert 3",
                "role_description": "You are representing the Theist position in a debate on God's existence.\nYour core values include: faith, spiritual experience, and religious tradition.\nFocus on cosmological arguments, personal experience, and moral foundations.\nWhen responding, maintain a respectful tone while firmly defending your position.",
                "model": "llama3:latest"
            },
            {
                "name": "Theist Expert 4",
                "role_description": "You are representing the Theist position in a debate on God's existence.\nYour core values include: faith, spiritual experience, and religious tradition.\nFocus on cosmological arguments, personal experience, and moral foundations.\nWhen responding, maintain a respectful tone while firmly defending your position.",
                "model": "llama3:latest"
            }
        ],
        "debate_settings": {
            "rounds": 6,
            "starting_position": "X",
            "verbose": True,
            "rotation_limit": 3
        }
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    
    try:
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        logger.info(f"Default configuration saved to {config_file}")
    except Exception as e:
        logger.error(f"Error creating default config: {e}")
        raise
