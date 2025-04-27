import os
from pathlib import Path

def create_output_directory():
    """Create output directory for debate files if it doesn't exist"""
    # Get the root project directory (parent of ui-interface)
    project_dir = Path(__file__).parent.parent
    output_dir = project_dir / "debate-agent" / "output"
    
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    else:
        print(f"Output directory already exists: {output_dir}")

if __name__ == "__main__":
    create_output_directory()
