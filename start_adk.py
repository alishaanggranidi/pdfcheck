#!/usr/bin/env python3
"""
Simple Google ADK Launcher for PDF Validator Agent
Minimal launcher for Google ADK web interface
"""

import os
import sys

def main():
    """Simple launcher for Google ADK"""
    print("=" * 50)
    print("PDF VALIDATOR AGENT - GOOGLE ADK")
    print("=" * 50)
    print("Validates VPN PDF documents using Gemini 2.0")
    print("Compatible with Google ADK web interface")
    print("=" * 50)
    
    # Check if Google API key is set
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("\n⚠ WARNING: GOOGLE_API_KEY not set!")
        print("Please set your Google API key:")
        print("  set GOOGLE_API_KEY=your_api_key_here")
        print("\nOr run: python setup_env.py")
        return
    
    print(f"\n✓ Google API Key configured")
    print(f"✓ Ready for Google ADK web interface")
    
    # Import and run ADK app
    try:
        from adk_web_app import get_adk_app, health
        
        # Initialize app
        app = get_adk_app()
        
        # Health check
        health_status = health()
        if health_status["status"] == "healthy":
            print(f"✓ ADK App initialized successfully")
            print(f"✓ Gemini Model: {health_status.get('gemini_model', 'Unknown')}")
            
            print("\n" + "=" * 50)
            print("AVAILABLE ADK FUNCTIONS:")
            print("=" * 50)
            print("from adk_web_app import validate_pdf, validate_pdf_bytes, batch_validate")
            print()
            print("# Validate single PDF")
            print("result = validate_pdf('document.pdf')")
            print()
            print("# Validate PDF from bytes")
            print("result = validate_pdf_bytes(pdf_data, 'document.pdf')")
            print()
            print("# Batch validate")
            print("results = batch_validate(['doc1.pdf', 'doc2.pdf'])")
            print()
            print("=" * 50)
            print("✓ Ready to use in Google ADK!")
            print("=" * 50)
            
        else:
            print(f"✗ ADK App initialization failed: {health_status.get('error', 'Unknown error')}")
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()
