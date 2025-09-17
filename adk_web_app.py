#!/usr/bin/env python3
"""
Google ADK Web Application for PDF Validator Agent
Compatible with Google ADK web interface
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from pdf_validator_agent import PDFValidatorAgent
from config import settings

class ADKWebApp:
    """Google ADK Web Application for PDF Validator"""
    
    def __init__(self):
        self.agent = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the PDF Validator Agent"""
        try:
            self.agent = PDFValidatorAgent()
            print("✓ PDF Validator Agent initialized for Google ADK")
            return True
        except Exception as e:
            print(f"✗ Error initializing agent: {e}")
            return False
    
    def validate_pdf_from_path(self, pdf_path: str) -> Dict[str, Any]:
        """Validate PDF from file path"""
        if not self.agent:
            return {"error": "Agent not initialized"}
        
        if not os.path.exists(pdf_path):
            return {"error": f"File not found: {pdf_path}"}
        
        if not pdf_path.lower().endswith('.pdf'):
            return {"error": "File must be a PDF"}
        
        try:
            print(f"Validating PDF: {os.path.basename(pdf_path)}")
            result = self.agent.validate_pdf_file(pdf_path)
            
            # Format result for ADK web
            return self.format_result_for_adk(result)
            
        except Exception as e:
            return {
                "error": f"Validation failed: {str(e)}",
                "file_path": pdf_path,
                "success": False
            }
    
    def validate_pdf_from_bytes(self, pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
        """Validate PDF from bytes data"""
        if not self.agent:
            return {"error": "Agent not initialized"}
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_bytes)
                temp_file_path = temp_file.name
            
            print(f"Validating PDF from bytes: {filename}")
            result = self.agent.validate_pdf_file(temp_file_path)
            
            # Add file info
            result["file_info"] = {
                "filename": filename,
                "file_size_bytes": len(pdf_bytes),
                "file_size_mb": round(len(pdf_bytes) / (1024 * 1024), 2)
            }
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            return self.format_result_for_adk(result)
            
        except Exception as e:
            return {
                "error": f"Validation failed: {str(e)}",
                "filename": filename,
                "success": False
            }
    
    def format_result_for_adk(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format result for Google ADK web interface"""
        final_result = result.get("final_result", {})
        
        # Create ADK-compatible response
        adk_result = {
            "success": True,
            "file_path": result.get("file_path", ""),
            "filename": os.path.basename(result.get("file_path", "")),
            "processing_time_seconds": result.get("processing_time_seconds", 0),
            "timestamp": result.get("timestamp", ""),
            
            # Validation results
            "is_valid": final_result.get("is_valid", False),
            "status": final_result.get("status", "unknown"),
            "message": final_result.get("message", ""),
            "confidence": final_result.get("confidence", 0.0),
            "document_type": final_result.get("document_type", "unknown"),
            "signature_count": final_result.get("signature_count", 0),
            "signature_valid": final_result.get("signature_valid", False),
            
            # Issues and recommendations
            "issues": final_result.get("issues", []),
            "recommendations": final_result.get("recommendations", []),
            "reasoning": final_result.get("reasoning", ""),
            
            # File info if available
            "file_info": result.get("file_info", {}),
            
            # Raw result for debugging
            "raw_result": result
        }
        
        return adk_result
    
    def batch_validate_pdfs(self, pdf_paths: List[str]) -> Dict[str, Any]:
        """Validate multiple PDF files"""
        if not self.agent:
            return {"error": "Agent not initialized"}
        
        results = []
        for i, pdf_path in enumerate(pdf_paths, 1):
            print(f"Processing {i}/{len(pdf_paths)}: {os.path.basename(pdf_path)}")
            result = self.validate_pdf_from_path(pdf_path)
            results.append(result)
        
        # Generate summary
        successful_results = [r for r in results if r.get("success", False)]
        summary = {
            "total_files": len(pdf_paths),
            "successful_validations": len(successful_results),
            "failed_validations": len(results) - len(successful_results),
            "approved_count": sum(1 for r in successful_results if r.get("is_valid", False)),
            "rejected_count": sum(1 for r in successful_results if not r.get("is_valid", False))
        }
        
        return {
            "success": True,
            "summary": summary,
            "results": results
        }
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""
        return {
            "app_name": settings.app_name,
            "min_signatures": settings.min_signatures,
            "max_file_size_mb": settings.max_file_size_mb,
            "log_level": settings.log_level,
            "google_api_configured": bool(settings.google_api_key),
            "langfuse_configured": bool(settings.langfuse_public_key),
            "gemini_model": "gemini-2.0-flash-exp"
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for ADK"""
        try:
            if self.agent:
                return {
                    "status": "healthy",
                    "app_name": settings.app_name,
                    "gemini_model": "gemini-2.0-flash-exp",
                    "google_api_configured": bool(settings.google_api_key),
                    "langfuse_configured": bool(settings.langfuse_public_key),
                    "agent_initialized": True
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Agent not initialized",
                    "agent_initialized": False
                }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "agent_initialized": False
            }

# Global app instance for ADK
adk_app = None

def get_adk_app():
    """Get or create ADK app instance"""
    global adk_app
    if adk_app is None:
        adk_app = ADKWebApp()
    return adk_app

# ADK Web Interface Functions
def validate_pdf(pdf_path: str) -> Dict[str, Any]:
    """ADK web function to validate PDF"""
    app = get_adk_app()
    return app.validate_pdf_from_path(pdf_path)

def validate_pdf_bytes(pdf_bytes: bytes, filename: str = "document.pdf") -> Dict[str, Any]:
    """ADK web function to validate PDF from bytes"""
    app = get_adk_app()
    return app.validate_pdf_from_bytes(pdf_bytes, filename)

def batch_validate(pdf_paths: List[str]) -> Dict[str, Any]:
    """ADK web function to validate multiple PDFs"""
    app = get_adk_app()
    return app.batch_validate_pdfs(pdf_paths)

def get_config() -> Dict[str, Any]:
    """ADK web function to get configuration"""
    app = get_adk_app()
    return app.get_configuration()

def health() -> Dict[str, Any]:
    """ADK web function for health check"""
    app = get_adk_app()
    return app.health_check()

# Main function for testing
def main():
    """Main function for testing ADK app"""
    print("=== PDF VALIDATOR AGENT - GOOGLE ADK WEB ===")
    print("Initializing for Google ADK web interface...")
    
    app = get_adk_app()
    
    # Check configuration
    config = app.get_configuration()
    print(f"\nConfiguration:")
    print(f"App: {config['app_name']}")
    print(f"Google API: {'✓ Configured' if config['google_api_configured'] else '✗ Not configured'}")
    print(f"Langfuse: {'✓ Configured' if config['langfuse_configured'] else '✗ Not configured'}")
    print(f"Gemini Model: {config['gemini_model']}")
    
    # Health check
    health_status = app.health_check()
    print(f"\nHealth Status: {health_status['status']}")
    
    if health_status['status'] == 'healthy':
        print("✓ Ready for Google ADK web interface!")
        print("\nAvailable functions:")
        print("- validate_pdf(pdf_path)")
        print("- validate_pdf_bytes(pdf_bytes, filename)")
        print("- batch_validate(pdf_paths)")
        print("- get_config()")
        print("- health()")
    else:
        print("✗ Not ready. Check configuration.")
    
    return app

if __name__ == "__main__":
    main()
