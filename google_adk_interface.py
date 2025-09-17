#!/usr/bin/env python3
"""
Google ADK Interface for PDF Validator Agent
Simple interface for running PDF validation without CLI
"""

import os
import sys
import json
from pathlib import Path
from pdf_validator_agent import PDFValidatorAgent
from config import settings

class GoogleADKInterface:
    """Simple interface for Google ADK environment"""
    
    def __init__(self):
        self.agent = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the PDF Validator Agent"""
        try:
            self.agent = PDFValidatorAgent()
            print("✓ PDF Validator Agent initialized successfully")
            print(f"✓ Using Gemini 2.0 model")
            print(f"✓ App: {settings.app_name}")
            return True
        except Exception as e:
            print(f"✗ Error initializing agent: {e}")
            return False
    
    def validate_pdf_file(self, pdf_path: str) -> dict:
        """Validate a single PDF file"""
        if not self.agent:
            return {"error": "Agent not initialized"}
        
        if not os.path.exists(pdf_path):
            return {"error": f"File not found: {pdf_path}"}
        
        if not pdf_path.lower().endswith('.pdf'):
            return {"error": "File must be a PDF"}
        
        try:
            print(f"\n=== VALIDATING PDF ===")
            print(f"File: {os.path.basename(pdf_path)}")
            print("Processing...")
            
            result = self.agent.validate_pdf_file(pdf_path)
            
            # Display results
            self.display_result(result)
            
            return result
            
        except Exception as e:
            error_result = {
                "error": f"Validation failed: {str(e)}",
                "file_path": pdf_path,
                "final_result": {
                    "is_valid": False,
                    "status": "error",
                    "message": str(e)
                }
            }
            print(f"✗ Error: {str(e)}")
            return error_result
    
    def display_result(self, result: dict):
        """Display validation result in a simple format"""
        final_result = result.get("final_result", {})
        
        print(f"\n=== VALIDATION RESULT ===")
        print(f"File: {os.path.basename(result.get('file_path', 'Unknown'))}")
        print(f"Processing Time: {result.get('processing_time_seconds', 0):.2f} seconds")
        
        # Status
        status = final_result.get("status", "unknown")
        is_valid = final_result.get("is_valid", False)
        
        if status == "approved_for_processing":
            print("✓ STATUS: APPROVED")
        elif status == "rejected_with_reason":
            print("✗ STATUS: REJECTED")
        else:
            print(f"⚠ STATUS: {status.upper()}")
        
        print(f"Valid: {'YES' if is_valid else 'NO'}")
        print(f"Confidence: {final_result.get('confidence', 0.0):.2f}")
        print(f"Document Type: {final_result.get('document_type', 'unknown')}")
        print(f"Signatures: {final_result.get('signature_count', 0)}/3")
        
        # Message
        message = final_result.get("message", "")
        if message:
            print(f"Message: {message}")
        
        # Issues
        issues = final_result.get("issues", [])
        if issues:
            print("\nIssues Found:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        # Recommendations
        recommendations = final_result.get("recommendations", [])
        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
    
    def save_result(self, result: dict, output_path: str = None):
        """Save result to JSON file"""
        if not output_path:
            input_file = result.get("file_path", "unknown")
            base_name = os.path.splitext(os.path.basename(input_file))[0]
            output_path = f"{base_name}_validation_result.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"✓ Result saved to: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error saving result: {e}")
            return False
    
    def get_file_from_input(self) -> str:
        """Get PDF file path from user input"""
        while True:
            print("\n=== PDF VALIDATOR - GOOGLE ADK ===")
            print("Enter the path to your PDF file:")
            print("(or type 'quit' to exit)")
            
            file_path = input("PDF file path: ").strip()
            
            if file_path.lower() in ['quit', 'exit', 'q']:
                return None
            
            if not file_path:
                print("Please enter a file path")
                continue
            
            # Handle relative paths
            if not os.path.isabs(file_path):
                file_path = os.path.abspath(file_path)
            
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            if not file_path.lower().endswith('.pdf'):
                print("File must be a PDF")
                continue
            
            return file_path
    
    def run_interactive(self):
        """Run interactive mode"""
        print("=== PDF VALIDATOR AGENT - GOOGLE ADK ===")
        print("Validates VPN application PDF documents using Gemini 2.0")
        print("=" * 50)
        
        # Check configuration
        self.check_configuration()
        
        while True:
            file_path = self.get_file_from_input()
            
            if file_path is None:
                print("Goodbye!")
                break
            
            # Validate PDF
            result = self.validate_pdf_file(file_path)
            
            # Ask to save result
            save_choice = input("\nSave result to file? (y/n): ").strip().lower()
            if save_choice in ['y', 'yes']:
                self.save_result(result)
            
            # Ask to continue
            continue_choice = input("\nValidate another PDF? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("Goodbye!")
                break
    
    def check_configuration(self):
        """Check and display current configuration"""
        print("\n=== CONFIGURATION ===")
        print(f"App Name: {settings.app_name}")
        print(f"Min Signatures: {settings.min_signatures}")
        print(f"Max File Size: {settings.max_file_size_mb}MB")
        print(f"Google API Key: {'✓ Set' if settings.google_api_key else '✗ Not set'}")
        print(f"Langfuse: {'✓ Enabled' if settings.langfuse_public_key else '✗ Disabled'}")
        
        if not settings.google_api_key:
            print("\n⚠ WARNING: GOOGLE_API_KEY not set!")
            print("Please set your Google API key in environment variables")
            return False
        
        return True

def main():
    """Main function for Google ADK interface"""
    try:
        interface = GoogleADKInterface()
        interface.run_interactive()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
