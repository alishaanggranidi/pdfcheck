#!/usr/bin/env python3
"""
Command Line Interface for PDF Validator Agent
"""

import argparse
import sys
import os
from pathlib import Path
from pdf_validator_agent import PDFValidatorAgent
from config import settings

def main():
    parser = argparse.ArgumentParser(
        description="PDF Validator Agent - Validasi dokumen PDF permohonan VPN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python cli_validator.py document.pdf
  python cli_validator.py --batch folder_with_pdfs/
  python cli_validator.py --output report.json document.pdf
  python cli_validator.py --verbose --detailed document.pdf
        """
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Path ke file PDF atau folder berisi PDF files"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Proses semua file PDF dalam folder"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Path untuk menyimpan hasil validasi (JSON format)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Tampilkan output verbose"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Tampilkan laporan detail"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Tampilkan konfigurasi saat ini"
    )
    
    args = parser.parse_args()
    
    # Show configuration if requested
    if args.config:
        show_configuration()
        return
    
    # Check if input is provided
    if not args.input:
        print("Error: Input path is required (use --help for usage)")
        sys.exit(1)
    
    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Path '{args.input}' tidak ditemukan")
        sys.exit(1)
    
    # Initialize agent
    try:
        agent = PDFValidatorAgent()
        if args.verbose:
            print("✓ PDF Validator Agent initialized successfully")
    except Exception as e:
        print(f"Error: Gagal menginisialisasi agent: {e}")
        sys.exit(1)
    
    # Process files
    if args.batch or input_path.is_dir():
        process_batch(agent, input_path, args)
    else:
        process_single_file(agent, input_path, args)

def show_configuration():
    """Display current configuration"""
    print("=== KONFIGURASI PDF VALIDATOR AGENT ===")
    print(f"App Name: {settings.app_name}")
    print(f"Min Signatures: {settings.min_signatures}")
    print(f"Max File Size: {settings.max_file_size_mb}MB")
    print(f"Log Level: {settings.log_level}")
    print(f"Google API Key: {'✓ Set' if settings.google_api_key else '✗ Not set'}")
    print(f"Langfuse Public Key: {'✓ Set' if settings.langfuse_public_key else '✗ Not set'}")
    print(f"Langfuse Secret Key: {'✓ Set' if settings.langfuse_secret_key else '✗ Not set'}")
    print(f"Langfuse Host: {settings.langfuse_host}")

def process_single_file(agent, file_path, args):
    """Process a single PDF file"""
    if not file_path.suffix.lower() == '.pdf':
        print(f"Error: File '{file_path}' bukan file PDF")
        sys.exit(1)
    
    if args.verbose:
        print(f"Memproses file: {file_path}")
        print("=" * 50)
    
    try:
        result = agent.validate_pdf_file(str(file_path))
        
        if args.verbose:
            print(f"✓ Processing completed in {result['processing_time_seconds']:.2f} seconds")
        
        # Display results
        display_result(result, args.detailed)
        
        # Save to file if requested
        if args.output:
            save_result_to_file(result, args.output)
            print(f"✓ Hasil disimpan ke: {args.output}")
        
    except Exception as e:
        print(f"Error: Gagal memproses file: {e}")
        sys.exit(1)

def process_batch(agent, folder_path, args):
    """Process multiple PDF files in a folder"""
    pdf_files = list(folder_path.glob("*.pdf"))
    
    if not pdf_files:
        print(f"Error: Tidak ada file PDF ditemukan di '{folder_path}'")
        sys.exit(1)
    
    if args.verbose:
        print(f"Menemukan {len(pdf_files)} file PDF")
        print("=" * 50)
    
    try:
        results = agent.validate_multiple_pdfs([str(f) for f in pdf_files])
        
        # Display summary
        display_batch_summary(results)
        
        # Display individual results if verbose
        if args.verbose:
            for i, result in enumerate(results, 1):
                print(f"\n--- File {i}/{len(results)}: {Path(result['file_path']).name} ---")
                display_result(result, args.detailed)
        
        # Save to file if requested
        if args.output:
            save_batch_results_to_file(results, args.output)
            print(f"✓ Hasil batch disimpan ke: {args.output}")
        
    except Exception as e:
        print(f"Error: Gagal memproses batch: {e}")
        sys.exit(1)

def display_result(result, detailed=False):
    """Display validation result"""
    final_result = result["final_result"]
    
    # Status with color coding
    status = final_result["status"]
    if status == "approved_for_processing":
        status_display = "✓ APPROVED"
    elif status == "rejected_with_reason":
        status_display = "✗ REJECTED"
    else:
        status_display = f"⚠ {status.upper()}"
    
    print(f"Status: {status_display}")
    print(f"Valid: {'YES' if final_result['is_valid'] else 'NO'}")
    print(f"Confidence: {final_result.get('confidence', 0.0):.2f}")
    print(f"Document Type: {final_result.get('document_type', 'unknown')}")
    print(f"Signatures: {final_result.get('signature_count', 0)}/3")
    print(f"Processing Time: {result['processing_time_seconds']:.2f}s")
    
    if detailed:
        print(f"\nReasoning: {final_result.get('reasoning', 'N/A')}")
        
        issues = final_result.get('issues', [])
        if issues:
            print("\nIssues Found:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        recommendations = final_result.get('recommendations', [])
        if recommendations:
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")

def display_batch_summary(results):
    """Display batch processing summary"""
    total = len(results)
    approved = sum(1 for r in results if r["final_result"].get("is_valid", False))
    rejected = sum(1 for r in results if r["final_result"].get("status") == "rejected_with_reason")
    errors = sum(1 for r in results if r["final_result"].get("status") == "error")
    
    processing_times = [r.get("processing_time_seconds", 0) for r in results]
    avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    print("\n=== BATCH SUMMARY ===")
    print(f"Total Files: {total}")
    print(f"✓ Approved: {approved}")
    print(f"✗ Rejected: {rejected}")
    print(f"⚠ Errors: {errors}")
    print(f"Approval Rate: {approved/total*100:.1f}%")
    print(f"Average Processing Time: {avg_time:.2f}s")

def save_result_to_file(result, output_path):
    """Save single result to JSON file"""
    import json
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

def save_batch_results_to_file(results, output_path):
    """Save batch results to JSON file"""
    import json
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
