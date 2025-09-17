#!/usr/bin/env python3
"""
Google ADK Launcher for PDF Validator Agent
Simple launcher for Google ADK web interface
"""

import os
import sys
from adk_web_app import get_adk_app, validate_pdf, validate_pdf_bytes, batch_validate, get_config, health
from adk_config import get_final_config, is_adk_web_enabled
from config import settings

def show_adk_info():
    """Show ADK information"""
    print("=" * 60)
    print("           PDF VALIDATOR AGENT - GOOGLE ADK")
    print("=" * 60)
    print("Validates VPN application PDF documents using Gemini 2.0")
    print("Compatible with Google ADK web interface")
    print("=" * 60)

def check_requirements():
    """Check if all requirements are met"""
    print("\n=== CHECKING REQUIREMENTS ===")
    
    # Check Google API Key
    if not settings.google_api_key:
        print("✗ GOOGLE_API_KEY not set!")
        print("Please set your Google API key in environment variables")
        return False
    else:
        print("✓ Google API Key configured")
    
    # Check dependencies
    try:
        import google.generativeai as genai
        print("✓ Google Generative AI library available")
    except ImportError:
        print("✗ Google Generative AI library not found")
        print("Please install: pip install google-generativeai")
        return False
    
    try:
        import fastapi
        print("✓ FastAPI available")
    except ImportError:
        print("✗ FastAPI not found")
        print("Please install: pip install fastapi uvicorn")
        return False
    
    return True

def initialize_adk_app():
    """Initialize ADK application"""
    print("\n=== INITIALIZING ADK APP ===")
    
    try:
        app = get_adk_app()
        
        # Health check
        health_status = health()
        if health_status["status"] == "healthy":
            print("✓ ADK App initialized successfully")
            return app
        else:
            print(f"✗ ADK App initialization failed: {health_status.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"✗ Error initializing ADK app: {e}")
        return None

def show_available_functions():
    """Show available ADK functions"""
    print("\n=== AVAILABLE ADK FUNCTIONS ===")
    print("1. validate_pdf(pdf_path) - Validate single PDF file")
    print("2. validate_pdf_bytes(pdf_bytes, filename) - Validate PDF from bytes")
    print("3. batch_validate(pdf_paths) - Validate multiple PDFs")
    print("4. get_config() - Get current configuration")
    print("5. health() - Health check")
    print("\nExample usage:")
    print("  result = validate_pdf('document.pdf')")
    print("  result = validate_pdf_bytes(pdf_data, 'document.pdf')")
    print("  results = batch_validate(['doc1.pdf', 'doc2.pdf'])")

def test_adk_functions():
    """Test ADK functions"""
    print("\n=== TESTING ADK FUNCTIONS ===")
    
    # Test health check
    print("Testing health check...")
    health_result = health()
    print(f"Health: {health_result['status']}")
    
    # Test config
    print("Testing configuration...")
    config_result = get_config()
    print(f"App: {config_result['app_name']}")
    print(f"Gemini Model: {config_result['gemini_model']}")
    
    print("✓ ADK functions working correctly")

def run_adk_web_interface():
    """Run ADK web interface"""
    print("\n=== STARTING ADK WEB INTERFACE ===")
    
    if not is_adk_web_enabled():
        print("ADK web interface is disabled in configuration")
        return
    
    try:
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse
        import uvicorn
        
        # Create FastAPI app
        app = FastAPI(
            title="PDF Validator Agent - Google ADK",
            description="Google ADK web interface for PDF validation",
            version="2.0.0"
        )
        
        # Add ADK endpoints
        @app.get("/")
        async def root():
            return {
                "message": "PDF Validator Agent - Google ADK",
                "version": "2.0.0",
                "status": "running",
                "endpoints": {
                    "validate_pdf": "/validate-pdf",
                    "validate_batch": "/validate-batch",
                    "health": "/health",
                    "config": "/config"
                }
            }
        
        @app.post("/validate-pdf")
        async def validate_pdf_endpoint(pdf_path: str):
            result = validate_pdf(pdf_path)
            return JSONResponse(content=result)
        
        @app.post("/validate-batch")
        async def validate_batch_endpoint(pdf_paths: list):
            result = batch_validate(pdf_paths)
            return JSONResponse(content=result)
        
        @app.get("/health")
        async def health_endpoint():
            result = health()
            return JSONResponse(content=result)
        
        @app.get("/config")
        async def config_endpoint():
            result = get_config()
            return JSONResponse(content=result)
        
        # Get ADK config
        adk_config = get_final_config()
        port = adk_config["adk_web"]["port"]
        host = adk_config["adk_web"]["host"]
        
        print(f"Starting ADK web interface on {host}:{port}")
        print(f"Access at: http://localhost:{port}")
        print(f"API docs at: http://localhost:{port}/docs")
        
        # Run server
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please install: pip install fastapi uvicorn")
    except Exception as e:
        print(f"Error starting ADK web interface: {e}")

def main():
    """Main function"""
    show_adk_info()
    
    # Check requirements
    if not check_requirements():
        print("\n✗ Requirements not met. Please fix the issues above.")
        return
    
    # Initialize ADK app
    app = initialize_adk_app()
    if not app:
        print("\n✗ Failed to initialize ADK app.")
        return
    
    # Show available functions
    show_available_functions()
    
    # Test functions
    test_adk_functions()
    
    print("\n✓ PDF Validator Agent is ready for Google ADK!")
    print("\nOptions:")
    print("1. Use functions directly in your ADK code")
    print("2. Start web interface (press Enter)")
    print("3. Exit (type 'quit')")
    
    choice = input("\nEnter your choice: ").strip().lower()
    
    if choice in ['', '1', 'web', 'start']:
        run_adk_web_interface()
    elif choice in ['quit', 'exit', 'q']:
        print("Goodbye!")
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
