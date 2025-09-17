#!/usr/bin/env python3
"""
Main Launcher for PDF Validator Agent - Google ADK Version
Simple interface for running PDF validation
"""

import os
import sys
from config import settings

def show_menu():
    """Display main menu"""
    print("\n" + "="*60)
    print("           PDF VALIDATOR AGENT - GOOGLE ADK")
    print("="*60)
    print("Validates VPN application PDF documents using Gemini 2.0")
    print()
    print("Options:")
    print("1. Validate Single PDF File")
    print("2. Batch Process PDF Files in Folder")
    print("3. Check Configuration")
    print("4. Exit")
    print("="*60)

def check_configuration():
    """Check and display configuration"""
    print("\n=== CONFIGURATION CHECK ===")
    print(f"App Name: {settings.app_name}")
    print(f"Min Signatures: {settings.min_signatures}")
    print(f"Max File Size: {settings.max_file_size_mb}MB")
    print(f"Log Level: {settings.log_level}")
    print()
    print("API Keys:")
    print(f"Google API Key: {'✓ Set' if settings.google_api_key else '✗ Not set'}")
    print(f"Langfuse Public Key: {'✓ Set' if settings.langfuse_public_key else '✗ Not set'}")
    print(f"Langfuse Secret Key: {'✓ Set' if settings.langfuse_secret_key else '✗ Not set'}")
    print(f"Langfuse Host: {settings.langfuse_host}")
    
    if not settings.google_api_key:
        print("\n⚠ WARNING: GOOGLE_API_KEY not set!")
        print("Please set your Google API key in environment variables")
        print("Example: set GOOGLE_API_KEY=your_api_key_here")
        return False
    
    print("\n✓ Configuration looks good!")
    return True

def run_single_file_validation():
    """Run single file validation"""
    try:
        from google_adk_interface import GoogleADKInterface
        interface = GoogleADKInterface()
        interface.run_interactive()
    except ImportError as e:
        print(f"Error importing interface: {e}")
    except Exception as e:
        print(f"Error running validation: {e}")

def run_batch_processing():
    """Run batch processing"""
    try:
        from batch_processor import BatchProcessor
        processor = BatchProcessor()
        processor.run_interactive()
    except ImportError as e:
        print(f"Error importing batch processor: {e}")
    except Exception as e:
        print(f"Error running batch processing: {e}")

def main():
    """Main function"""
    print("Starting PDF Validator Agent...")
    
    # Check if we have required dependencies
    try:
        import google.generativeai as genai
        import fastapi
        import uvicorn
        print("✓ Dependencies loaded successfully")
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return
    
    while True:
        show_menu()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                print("\nStarting single file validation...")
                if check_configuration():
                    run_single_file_validation()
                else:
                    input("Press Enter to continue...")
            
            elif choice == "2":
                print("\nStarting batch processing...")
                if check_configuration():
                    run_batch_processing()
                else:
                    input("Press Enter to continue...")
            
            elif choice == "3":
                check_configuration()
                input("Press Enter to continue...")
            
            elif choice == "4":
                print("Goodbye!")
                break
            
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            break
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
