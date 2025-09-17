import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file from example"""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if env_example.exists():
        with open(env_example, 'r') as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✓ .env file created from example")
        print("⚠ Please edit .env file and add your API keys")
    else:
        print("⚠ env_example.txt not found, creating basic .env file")
        with open(env_file, 'w') as f:
            f.write("""# PDF Validator Agent Configuration
GOOGLE_API_KEY=your_google_api_key_here
LF_PUBLIC_KEY=your_langfuse_public_key
LF_SECRET_KEY=your_langfuse_secret_key
LF_HOST=https://api.langfuse.com
APP_NAME=PDF_Validator_Agent
LOG_LEVEL=INFO
""")

def test_installation():
    """Test if installation is working"""
    print("Testing installation...")
    try:
        # Test imports
        from config import settings
        from pdf_processor import PDFProcessor
        from gemini_judge import GeminiJudge
        from pdf_validator_agent import PDFValidatorAgent
        
        print("✓ All modules imported successfully")
        
        # Test configuration
        print(f"✓ App name: {settings.app_name}")
        print(f"✓ Min signatures: {settings.min_signatures}")
        print(f"✓ Max file size: {settings.max_file_size_mb}MB")
        
        # Check API keys
        if settings.google_api_key and settings.google_api_key != "your_google_api_key_here":
            print("✓ Google API key configured")
        else:
            print("⚠ Google API key not configured")
        
        if settings.langfuse_public_key and settings.langfuse_public_key != "your_langfuse_public_key":
            print("✓ Langfuse keys configured")
        else:
            print("⚠ Langfuse keys not configured (optional)")
        
    except ImportError as e:
        print(f"Error importing modules: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error testing installation: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["logs", "temp", "output"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory created: {directory}")

def show_next_steps():
    """Show next steps to user"""
    print("\n" + "="*50)
    print("SETUP COMPLETED SUCCESSFULLY!")
    print("="*50)
    
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys:")
    print("   - Get Google API key from: https://makersuite.google.com/app/apikey")
    print("   - Get Langfuse keys from: https://cloud.langfuse.com/ (optional)")
    
    print("\n2. Test the installation:")
    print("   python test_validator.py")
    
    print("\n3. Run example usage:")
    print("   python example_usage.py")
    
    print("\n4. Start the API server:")
    print("   python api_server.py")
    
    print("\n5. Use CLI for validation:")
    print("   python cli_validator.py --help")
    
    print("\n6. Read the documentation:")
    print("   cat README.md")

def main():
    """Main setup function"""
    print("PDF Validator Agent Setup")
    print("="*30)
    
    try:
        check_python_version()
        install_requirements()
        create_env_file()
        create_directories()
        test_installation()
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
