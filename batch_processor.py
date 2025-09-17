#!/usr/bin/env python3
"""
Batch PDF Processor for Google ADK
Process multiple PDF files in a folder
"""

import os
import json
from pathlib import Path
from pdf_validator_agent import PDFValidatorAgent
from config import settings

class BatchProcessor:
    """Batch processor for multiple PDF files"""
    
    def __init__(self):
        self.agent = None
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the PDF Validator Agent"""
        try:
            self.agent = PDFValidatorAgent()
            print("✓ PDF Validator Agent initialized for batch processing")
            return True
        except Exception as e:
            print(f"✗ Error initializing agent: {e}")
            return False
    
    def process_folder(self, folder_path: str, output_file: str = None) -> dict:
        """Process all PDF files in a folder"""
        if not self.agent:
            return {"error": "Agent not initialized"}
        
        folder = Path(folder_path)
        if not folder.exists():
            return {"error": f"Folder not found: {folder_path}"}
        
        if not folder.is_dir():
            return {"error": f"Path is not a directory: {folder_path}"}
        
        # Find all PDF files
        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            return {"error": f"No PDF files found in: {folder_path}"}
        
        print(f"\n=== BATCH PROCESSING ===")
        print(f"Folder: {folder_path}")
        print(f"Found {len(pdf_files)} PDF files")
        print("=" * 50)
        
        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\nProcessing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            try:
                result = self.agent.validate_pdf_file(str(pdf_file))
                results.append(result)
                
                # Quick status display
                final_result = result.get("final_result", {})
                status = final_result.get("status", "unknown")
                is_valid = final_result.get("is_valid", False)
                
                if status == "approved_for_processing":
                    print(f"  ✓ APPROVED")
                elif status == "rejected_with_reason":
                    print(f"  ✗ REJECTED")
                else:
                    print(f"  ⚠ {status.upper()}")
                
            except Exception as e:
                error_result = {
                    "file_path": str(pdf_file),
                    "error": str(e),
                    "final_result": {
                        "is_valid": False,
                        "status": "error",
                        "message": str(e)
                    }
                }
                results.append(error_result)
                print(f"  ✗ ERROR: {e}")
        
        # Generate summary
        summary = self.generate_summary(results)
        self.display_summary(summary)
        
        # Save results if requested
        if output_file:
            self.save_batch_results(results, output_file)
        
        return {
            "summary": summary,
            "results": results
        }
    
    def generate_summary(self, results: list) -> dict:
        """Generate summary of batch processing"""
        total = len(results)
        approved = sum(1 for r in results if r.get("final_result", {}).get("is_valid", False))
        rejected = sum(1 for r in results if r.get("final_result", {}).get("status") == "rejected_with_reason")
        errors = sum(1 for r in results if r.get("final_result", {}).get("status") == "error")
        
        processing_times = [r.get("processing_time_seconds", 0) for r in results]
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            "total_files": total,
            "approved_count": approved,
            "rejected_count": rejected,
            "error_count": errors,
            "approval_rate": (approved / total * 100) if total > 0 else 0,
            "average_processing_time": avg_time
        }
    
    def display_summary(self, summary: dict):
        """Display batch processing summary"""
        print(f"\n=== BATCH SUMMARY ===")
        print(f"Total Files: {summary['total_files']}")
        print(f"✓ Approved: {summary['approved_count']}")
        print(f"✗ Rejected: {summary['rejected_count']}")
        print(f"⚠ Errors: {summary['error_count']}")
        print(f"Approval Rate: {summary['approval_rate']:.1f}%")
        print(f"Average Processing Time: {summary['average_processing_time']:.2f}s")
    
    def save_batch_results(self, results: list, output_file: str):
        """Save batch results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"✓ Batch results saved to: {output_file}")
        except Exception as e:
            print(f"✗ Error saving batch results: {e}")
    
    def get_folder_from_input(self) -> str:
        """Get folder path from user input"""
        while True:
            print("\n=== BATCH PDF PROCESSOR ===")
            print("Enter the path to folder containing PDF files:")
            print("(or type 'quit' to exit)")
            
            folder_path = input("Folder path: ").strip()
            
            if folder_path.lower() in ['quit', 'exit', 'q']:
                return None
            
            if not folder_path:
                print("Please enter a folder path")
                continue
            
            # Handle relative paths
            if not os.path.isabs(folder_path):
                folder_path = os.path.abspath(folder_path)
            
            if not os.path.exists(folder_path):
                print(f"Folder not found: {folder_path}")
                continue
            
            if not os.path.isdir(folder_path):
                print("Path is not a directory")
                continue
            
            return folder_path
    
    def run_interactive(self):
        """Run interactive batch processing"""
        print("=== BATCH PDF PROCESSOR - GOOGLE ADK ===")
        print("Process multiple PDF files in a folder")
        print("=" * 50)
        
        # Check configuration
        if not settings.google_api_key:
            print("⚠ WARNING: GOOGLE_API_KEY not set!")
            print("Please set your Google API key in environment variables")
            return
        
        while True:
            folder_path = self.get_folder_from_input()
            
            if folder_path is None:
                print("Goodbye!")
                break
            
            # Ask for output file
            save_choice = input("Save results to file? (y/n): ").strip().lower()
            output_file = None
            if save_choice in ['y', 'yes']:
                output_file = input("Output file name (or press Enter for default): ").strip()
                if not output_file:
                    output_file = "batch_validation_results.json"
            
            # Process folder
            result = self.process_folder(folder_path, output_file)
            
            # Ask to continue
            continue_choice = input("\nProcess another folder? (y/n): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("Goodbye!")
                break

def main():
    """Main function for batch processor"""
    try:
        processor = BatchProcessor()
        processor.run_interactive()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
