#!/usr/bin/env python3
"""
Contoh penggunaan PDF Validator Agent
"""

import os
import json
from pdf_validator_agent import PDFValidatorAgent

def example_single_validation():
    """Contoh validasi file PDF tunggal"""
    print("=== CONTOH VALIDASI FILE TUNGGAL ===")
    
    # Initialize agent
    agent = PDFValidatorAgent()
    
    # Path ke file PDF (ganti dengan path file Anda)
    pdf_path = "sample_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"File {pdf_path} tidak ditemukan. Silakan ganti dengan path file PDF yang valid.")
        return
    
    try:
        # Validasi PDF
        result = agent.validate_pdf_file(pdf_path)
        
        # Tampilkan hasil
        print(f"File: {os.path.basename(pdf_path)}")
        print(f"Status: {result['final_result']['status']}")
        print(f"Valid: {'YES' if result['final_result']['is_valid'] else 'NO'}")
        print(f"Confidence: {result['final_result'].get('confidence', 0.0):.2f}")
        print(f"Document Type: {result['final_result'].get('document_type', 'unknown')}")
        print(f"Signatures: {result['final_result'].get('signature_count', 0)}/3")
        print(f"Processing Time: {result['processing_time_seconds']:.2f}s")
        
        # Tampilkan reasoning jika ada
        reasoning = result['final_result'].get('reasoning', '')
        if reasoning:
            print(f"\nReasoning: {reasoning}")
        
        # Tampilkan issues jika ada
        issues = result['final_result'].get('issues', [])
        if issues:
            print("\nIssues Found:")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        # Simpan hasil ke file
        with open("validation_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Hasil disimpan ke: validation_result.json")
        
    except Exception as e:
        print(f"Error: {e}")

def example_batch_validation():
    """Contoh validasi multiple PDF files"""
    print("\n=== CONTOH VALIDASI BATCH ===")
    
    # Initialize agent
    agent = PDFValidatorAgent()
    
    # List file PDF (ganti dengan path file yang valid)
    pdf_files = [
        "document1.pdf",
        "document2.pdf", 
        "document3.pdf"
    ]
    
    # Filter file yang ada
    existing_files = [f for f in pdf_files if os.path.exists(f)]
    
    if not existing_files:
        print("Tidak ada file PDF yang ditemukan. Silakan ganti dengan path file yang valid.")
        return
    
    try:
        # Validasi batch
        results = agent.validate_multiple_pdfs(existing_files)
        
        # Tampilkan summary
        total = len(results)
        approved = sum(1 for r in results if r["final_result"].get("is_valid", False))
        rejected = sum(1 for r in results if r["final_result"].get("status") == "rejected_with_reason")
        
        print(f"Total Files: {total}")
        print(f"Approved: {approved}")
        print(f"Rejected: {rejected}")
        print(f"Approval Rate: {approved/total*100:.1f}%")
        
        # Tampilkan detail setiap file
        for i, result in enumerate(results, 1):
            filename = os.path.basename(result['file_path'])
            status = result['final_result']['status']
            is_valid = result['final_result']['is_valid']
            
            print(f"\n{i}. {filename}")
            print(f"   Status: {status}")
            print(f"   Valid: {'YES' if is_valid else 'NO'}")
            print(f"   Time: {result['processing_time_seconds']:.2f}s")
        
        # Simpan hasil batch
        with open("batch_validation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Hasil batch disimpan ke: batch_validation_results.json")
        
    except Exception as e:
        print(f"Error: {e}")

def example_api_usage():
    """Contoh penggunaan API"""
    print("\n=== CONTOH PENGGUNAAN API ===")
    
    print("""
Untuk menggunakan API, jalankan server terlebih dahulu:

    python api_server.py

Kemudian gunakan curl atau tool HTTP lainnya:

1. Health Check:
   curl http://localhost:8000/health

2. Validasi file tunggal:
   curl -X POST "http://localhost:8000/validate-pdf" \\
        -H "Content-Type: multipart/form-data" \\
        -F "file=@document.pdf"

3. Validasi multiple files:
   curl -X POST "http://localhost:8000/validate-multiple-pdfs" \\
        -H "Content-Type: multipart/form-data" \\
        -F "files=@doc1.pdf" \\
        -F "files=@doc2.pdf"

4. Lihat konfigurasi:
   curl http://localhost:8000/config
""")

def example_configuration():
    """Contoh konfigurasi"""
    print("\n=== CONTOH KONFIGURASI ===")
    
    from config import settings
    
    print("Konfigurasi saat ini:")
    print(f"  App Name: {settings.app_name}")
    print(f"  Min Signatures: {settings.min_signatures}")
    print(f"  Max File Size: {settings.max_file_size_mb}MB")
    print(f"  Log Level: {settings.log_level}")
    print(f"  Google API Key: {'✓ Set' if settings.google_api_key else '✗ Not set'}")
    print(f"  Langfuse Public Key: {'✓ Set' if settings.langfuse_public_key else '✗ Not set'}")
    print(f"  Langfuse Secret Key: {'✓ Set' if settings.langfuse_secret_key else '✗ Not set'}")

def main():
    """Main function untuk menjalankan contoh"""
    print("PDF Validator Agent - Contoh Penggunaan")
    print("=" * 50)
    
    # Tampilkan konfigurasi
    example_configuration()
    
    # Contoh validasi file tunggal
    example_single_validation()
    
    # Contoh validasi batch
    example_batch_validation()
    
    # Contoh penggunaan API
    example_api_usage()
    
    print("\n" + "=" * 50)
    print("Contoh selesai!")
    print("\nUntuk informasi lebih lanjut, lihat README.md")

if __name__ == "__main__":
    main()
