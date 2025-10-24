#!/usr/bin/env python3
"""
Script to download models from Hugging Face Hub.

This script provides a Python-based alternative to download models,
with more control and better error handling.

Usage:
    python download_model.py <model_id> [--output-dir DIR] [--token TOKEN]

Examples:
    python download_model.py unsloth/mistral-7b-instruct-v0.3-bnb-4bit
    python download_model.py TinyLlama/TinyLlama-1.1B-Chat-v1.0 --output-dir ./models
    python download_model.py meta-llama/Llama-2-7b-chat-hf --token hf_xxx
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

def print_colored(message: str, color: str = "green"):
    """Print colored messages to the terminal."""
    colors = {
        "green": "\033[0;32m",
        "yellow": "\033[1;33m",
        "red": "\033[0;31m",
        "blue": "\033[0;34m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['green'])}{message}{colors['reset']}")


def check_huggingface_hub():
    """Check if huggingface_hub is installed."""
    try:
        import huggingface_hub
        return True
    except ImportError:
        return False


def download_model(model_id: str, output_dir: str, token: str = None):
    """
    Download a model from Hugging Face Hub.
    
    Args:
        model_id: The model ID on Hugging Face (e.g., 'gpt2', 'meta-llama/Llama-2-7b')
        output_dir: Directory where the model will be saved
        token: Hugging Face API token (optional)
    """
    from huggingface_hub import snapshot_download
    
    # Convert model_id to directory name
    model_dir_name = model_id.replace("/", "--")
    full_output_path = Path(output_dir) / model_dir_name
    
    print_colored(f"📦 Downloading model: {model_id}", "blue")
    print_colored(f"📁 Output directory: {full_output_path}", "blue")
    print()
    
    # Check if directory already exists
    if full_output_path.exists():
        print_colored(f"⚠️  Model directory already exists: {full_output_path}", "yellow")
        response = input("Do you want to continue and overwrite? (y/N): ")
        if response.lower() != 'y':
            print_colored("Download cancelled.", "yellow")
            return False
    
    # Create output directory
    full_output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download the model
        print_colored("🔄 Starting download...", "blue")
        print()
        
        snapshot_download(
            repo_id=model_id,
            local_dir=str(full_output_path),
            local_dir_use_symlinks=False,
            token=token,
            resume_download=True
        )
        
        print()
        print_colored("✅ Model downloaded successfully!", "green")
        print_colored(f"📍 Location: {full_output_path}", "green")
        print()
        print_colored("To use this model in docker-compose.yml, set:", "blue")
        print(f"  MODEL_PATH=/models/{model_dir_name}")
        print()
        
        return True
        
    except Exception as e:
        print()
        print_colored(f"❌ Download failed: {str(e)}", "red")
        return False


def main():
    """Main function to parse arguments and download model."""
    parser = argparse.ArgumentParser(
        description="Download models from Hugging Face Hub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s unsloth/mistral-7b-instruct-v0.3-bnb-4bit
  %(prog)s TinyLlama/TinyLlama-1.1B-Chat-v1.0 --output-dir ./models
  %(prog)s meta-llama/Llama-2-7b-chat-hf --token hf_xxxxx
        """
    )
    
    parser.add_argument(
        "model_id",
        help="Model ID on Hugging Face (e.g., 'gpt2', 'meta-llama/Llama-2-7b')"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./models",
        help="Output directory for the model (default: ../models relative to script)"
    )
    
    parser.add_argument(
        "--token",
        default=HF_TOKEN,
        help="Hugging Face API token (or set HF_TOKEN env variable)"
    )
    
    args = parser.parse_args()
    
    # Check if huggingface_hub is installed
    if not check_huggingface_hub():
        print_colored("❌ huggingface_hub is not installed!", "red")
        print()
        print("Install it with:")
        print("  pip install huggingface_hub")
        print()
        print("Or install project dependencies (declared in pyproject.toml):")
        print("  pip install ./")
        sys.exit(1)
    
    # Determine output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Default to models directory relative to script location
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / "models"
    
    # Get token from environment if not provided
    token = args.token or os.getenv("HF_TOKEN")
    
    if not token:
        print_colored("⚠️  No Hugging Face token provided.", "yellow")
        print_colored("   Some models require authentication.", "yellow")
        print()
        print("To set your token:")
        print("  export HF_TOKEN=your_token_here")
        print("Or pass it with --token flag")
        print()
        response = input("Continue without token? (y/N): ")
        if response.lower() != 'y':
            print_colored("Download cancelled.", "yellow")
            sys.exit(0)
    
    # Download the model
    success = download_model(args.model_id, output_dir, token)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
