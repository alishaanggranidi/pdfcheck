import os
import sys
import tempfile
import json
from unittest.mock import Mock, patch
from pdf_validator_agent import PDFValidatorAgent
from pdf_processor import PDFProcessor
from gemini_judge import GeminiJudge
from config import settings

def test_configuration():
    """Test konfigurasi"""
    print("Testing configuration...")
    
    assert hasattr(settings, 'app_name'), "App name not configured"
    assert hasattr(settings, 'min_signatures'), "Min signatures not configured"
    assert hasattr(settings, 'max_file_size_mb'), "Max file size not configured"
    
    print("✓ Configuration test passed")

def test_pdf_processor():
    """Test PDF processor"""
    print("Testing PDF processor...")
    
    processor = PDFProcessor()
    
    # Test field extraction
    sample_text = """
    NIK: 1234567890
    Nama: John Doe
    Email: john.doe@infomedia.co.id
    Departement: IT
    """
    
    fields = processor.extract_form_fields(sample_text)
    
    assert "NIK" in fields, "NIK field not extracted"
    assert "Nama" in fields, "Nama field not extracted"
    assert "Email" in fields, "Email field not extracted"
    
    print("✓ PDF processor test passed")

def test_document_type_detection():
    """Test document type detection"""
    print("Testing document type detection...")
    
    processor = PDFProcessor()
    
    # Test new VPN request
    new_vpn_text = "Permohonan VPN baru untuk akses sistem"
    result = processor.detect_document_type(new_vpn_text)
    
    assert result["document_type"] in ["new_vpn_request", "vpn_extension", "unknown"], "Invalid document type"
    
    # Test extension
    extension_text = "Perpanjangan akses VPN untuk user"
    result = processor.detect_document_type(extension_text)
    
    assert result["document_type"] in ["new_vpn_request", "vpn_extension", "unknown"], "Invalid document type"
    
    print("✓ Document type detection test passed")

def test_gemini_judge_mock():
    """Test Gemini judge with mock"""
    print("Testing Gemini judge (mock)...")
    
    # Mock the Gemini API call
    with patch('gemini_judge.genai.GenerativeModel') as mock_model:
        # Setup mock response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "is_valid": True,
            "status": "approved_for_processing",
            "confidence": 0.9,
            "issues": [],
            "reasoning": "All fields are valid",
            "missing_fields": [],
            "signature_analysis": {"count": 3, "sufficient": True, "description": "Sufficient signatures"},
            "document_type_analysis": {"detected_type": "new_vpn_request", "confidence": 0.8, "description": "New VPN request detected"},
            "recommendations": []
        })
        
        mock_model.return_value.generate_content.return_value = mock_response
        
        # Test judge
        judge = GeminiJudge()
        
        validation_data = {
            "NIK": "1234567890",
            "Nama": "John Doe",
            "Email": "john.doe@infomedia.co.id",
            "signature_count": 3,
            "signature_valid": True,
            "document_type": "new_vpn_request"
        }
        
        result = judge.evaluate_pdf(validation_data)
        
        assert "is_valid" in result, "is_valid not in result"
        assert "status" in result, "status not in result"
        assert "confidence" in result, "confidence not in result"
        
        print("✓ Gemini judge test passed")

def test_agent_integration():
    """Test agent integration"""
    print("Testing agent integration...")
    
    # Create a mock PDF file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        temp_file.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
        temp_file.flush()
        temp_pdf_path = temp_file.name
    
    try:
        # Mock the PDF processing and Gemini evaluation
        with patch('pdf_processor.PDFProcessor.process_pdf') as mock_process, \
             patch('gemini_judge.GeminiJudge.evaluate_pdf') as mock_evaluate:
            
            # Setup mock responses
            mock_process.return_value = {
                "processing_status": "success",
                "extracted_content": {"raw_text": "Sample PDF content"},
                "document_type": {"document_type": "new_vpn_request", "confidence": 0.8},
                "form_fields": {
                    "NIK": "1234567890",
                    "Nama": "John Doe",
                    "Email": "john.doe@infomedia.co.id"
                },
                "signature_info": {
                    "signature_count": 3,
                    "signature_valid": True
                },
                "validation_data": {
                    "NIK": "1234567890",
                    "Nama": "John Doe",
                    "Email": "john.doe@infomedia.co.id",
                    "signature_count": 3,
                    "signature_valid": True,
                    "document_type": "new_vpn_request"
                }
            }
            
            mock_evaluate.return_value = {
                "is_valid": True,
                "status": "approved_for_processing",
                "confidence": 0.9,
                "issues": [],
                "reasoning": "All validations passed"
            }
            
            # Test agent
            agent = PDFValidatorAgent()
            result = agent.validate_pdf_file(temp_pdf_path)
            
            assert "final_result" in result, "final_result not in result"
            assert "processing_time_seconds" in result, "processing_time_seconds not in result"
            
            print("✓ Agent integration test passed")
    
    finally:
        # Clean up
        if os.path.exists(temp_pdf_path):
            os.unlink(temp_pdf_path)

def test_error_handling():
    """Test error handling"""
    print("Testing error handling...")
    
    agent = PDFValidatorAgent()
    
    # Test with non-existent file
    result = agent.validate_pdf_file("non_existent_file.pdf")
    
    assert result["final_result"]["status"] == "error", "Error status not set"
    assert "error" in result, "Error message not in result"
    
    print("✓ Error handling test passed")

def run_all_tests():
    """Run all tests"""
    print("Running PDF Validator Agent Tests")
    print("=" * 40)
    
    try:
        test_configuration()
        test_pdf_processor()
        test_document_type_detection()
        test_gemini_judge_mock()
        test_agent_integration()
        test_error_handling()
        
        print("\n" + "=" * 40)
        print("✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)

def test_with_real_pdf():
    """Test with real PDF file (if available)"""
    print("\nTesting with real PDF file...")
    
    # Look for sample PDF files
    sample_files = ["sample.pdf", "test.pdf", "document.pdf"]
    found_file = None
    
    for file in sample_files:
        if os.path.exists(file):
            found_file = file
            break
    
    if not found_file:
        print("No sample PDF file found. Skipping real PDF test.")
        print("To test with real PDF, place a sample file named 'sample.pdf' in the current directory.")
        return
    
    try:
        agent = PDFValidatorAgent()
        result = agent.validate_pdf_file(found_file)
        
        print(f"✓ Real PDF test completed for {found_file}")
        print(f"  Status: {result['final_result']['status']}")
        print(f"  Valid: {result['final_result']['is_valid']}")
        print(f"  Processing Time: {result['processing_time_seconds']:.2f}s")
        
    except Exception as e:
        print(f"✗ Real PDF test failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--real-pdf":
        test_with_real_pdf()
    else:
        run_all_tests()
