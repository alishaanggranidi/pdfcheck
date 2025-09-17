import json
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from config import settings
from langfuse_utils import send_trace_minimal

class GeminiJudge:
    """LLM Judge using Google Gemini for PDF validation"""
    
    def __init__(self):
        self.api_key = settings.google_api_key
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def create_validation_prompt(self, validation_data: Dict[str, Any]) -> str:
        """
        Create a comprehensive prompt for Gemini to evaluate the PDF
        """
        prompt = f"""
Anda adalah seorang AI Judge yang bertugas mengevaluasi dokumen permohonan VPN. 
Tugas Anda adalah menganalisis data yang diekstrak dari PDF dan memberikan keputusan final.

DATA YANG DIEKSTRAK:
{json.dumps(validation_data, indent=2, ensure_ascii=False)}

KRITERIA EVALUASI:
1. KELENGKAPAN DATA:
   - NIK harus diisi dan berupa angka
   - Nama lengkap harus diisi
   - Nomor telepon harus diisi
   - Email harus diisi dan menggunakan domain @infomedia.co.id
   - Departement harus diisi
   - Manager/Atasan harus diisi
   - Range Tanggal harus diisi dengan format yang benar
   - Range Waktu harus diisi dengan format yang benar
   - Approved by harus diisi
   - User VPN harus diisi

2. VALIDASI TANDA TANGAN:
   - Dokumen harus memiliki minimal 3 tanda tangan
   - Tanda tangan harus dari: pemohon, atasan, dan pihak IT
   - Jumlah tanda tangan saat ini: {validation_data.get('signature_count', 0)}

3. JENIS DOKUMEN:
   - Tipe dokumen terdeteksi: {validation_data.get('document_type', 'unknown')}
   - Pastikan dokumen adalah permohonan VPN baru atau perpanjangan VPN

4. KONSISTENSI DATA:
   - Nama di form harus konsisten dengan User VPN
   - Tanggal dan waktu harus logis
   - Email harus sesuai format perusahaan

TUGAS ANDA:
Berdasarkan analisis di atas, berikan evaluasi dalam format JSON dengan struktur berikut:

{{
    "is_valid": boolean,
    "status": "approved_for_processing" atau "rejected_with_reason",
    "confidence": float (0.0 - 1.0),
    "issues": [list of issues found],
    "reasoning": "penjelasan singkat keputusan",
    "missing_fields": [list of missing required fields],
    "signature_analysis": {{
        "count": number,
        "sufficient": boolean,
        "description": "analisis tanda tangan"
    }},
    "document_type_analysis": {{
        "detected_type": string,
        "confidence": float,
        "description": "analisis jenis dokumen"
    }},
    "recommendations": [list of recommendations for improvement]
}}

PENTING:
- Jika ada field yang kosong atau tidak valid, set is_valid = false
- Jika tanda tangan kurang dari 3, set is_valid = false
- Jika email tidak menggunakan domain @infomedia.co.id, set is_valid = false
- Berikan reasoning yang jelas dan spesifik
- Confidence harus mencerminkan tingkat kepastian evaluasi

Jawab hanya dengan JSON, tanpa teks tambahan.
"""
        return prompt
    
    def evaluate_pdf(self, validation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate PDF using Gemini LLM
        """
        try:
            # Create prompt
            prompt = self.create_validation_prompt(validation_data)
            
            # Call Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Parse JSON response
            try:
                # Clean response text to extract JSON
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                result = json.loads(response_text)
                
                # Validate required fields in response
                required_fields = ['is_valid', 'status', 'confidence', 'issues', 'reasoning']
                for field in required_fields:
                    if field not in result:
                        result[field] = self._get_default_value(field)
                
                # Ensure confidence is float
                try:
                    result['confidence'] = float(result['confidence'])
                    result['confidence'] = max(0.0, min(1.0, result['confidence']))
                except (ValueError, TypeError):
                    result['confidence'] = 0.5
                
                # Log to Langfuse
                self._log_to_langfuse(validation_data, result, "success")
                
                return result
                
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                fallback_result = self._create_fallback_result(validation_data, f"JSON parsing error: {e}")
                self._log_to_langfuse(validation_data, fallback_result, "json_parse_error")
                return fallback_result
                
        except Exception as e:
            # Fallback for any other errors
            fallback_result = self._create_fallback_result(validation_data, f"LLM evaluation error: {e}")
            self._log_to_langfuse(validation_data, fallback_result, "llm_error")
            return fallback_result
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for missing fields"""
        defaults = {
            'is_valid': False,
            'status': 'rejected_with_reason',
            'confidence': 0.0,
            'issues': ['LLM evaluation failed'],
            'reasoning': 'Unable to evaluate due to processing error',
            'missing_fields': [],
            'signature_analysis': {'count': 0, 'sufficient': False, 'description': 'Unable to analyze'},
            'document_type_analysis': {'detected_type': 'unknown', 'confidence': 0.0, 'description': 'Unable to analyze'},
            'recommendations': ['Please check document format and try again']
        }
        return defaults.get(field, None)
    
    def _create_fallback_result(self, validation_data: Dict[str, Any], error_msg: str) -> Dict[str, Any]:
        """Create fallback result when LLM evaluation fails"""
        # Basic rule-based validation as fallback
        issues = []
        missing_fields = []
        
        # Check required fields
        required_fields = [
            "NIK", "Nama", "No Tel", "Email", "Departement", 
            "Manager", "Range Tanggal", "Range Waktu", "Approved by", "User VPN"
        ]
        
        for field in required_fields:
            if not validation_data.get(field, "").strip():
                missing_fields.append(field)
                issues.append(f"Field '{field}' is missing")
        
        # Check email format
        email = validation_data.get("Email", "")
        if email and "@infomedia.co.id" not in email:
            issues.append("Email must use @infomedia.co.id domain")
        
        # Check signatures
        signature_count = validation_data.get('signature_count', 0)
        if signature_count < 3:
            issues.append(f"Insufficient signatures: {signature_count}/3 required")
        
        is_valid = len(issues) == 0 and signature_count >= 3
        
        return {
            "is_valid": is_valid,
            "status": "approved_for_processing" if is_valid else "rejected_with_reason",
            "confidence": 0.3,  # Low confidence for fallback
            "issues": issues,
            "reasoning": f"Fallback evaluation due to: {error_msg}",
            "missing_fields": missing_fields,
            "signature_analysis": {
                "count": signature_count,
                "sufficient": signature_count >= 3,
                "description": f"Found {signature_count} signatures"
            },
            "document_type_analysis": {
                "detected_type": validation_data.get('document_type', 'unknown'),
                "confidence": 0.3,
                "description": "Basic detection only"
            },
            "recommendations": ["Please ensure all required fields are filled and document has sufficient signatures"]
        }
    
    def _log_to_langfuse(self, input_data: Dict[str, Any], output_data: Dict[str, Any], status: str):
        """Log evaluation to Langfuse"""
        try:
            metadata = {
                "status": status,
                "document_type": input_data.get('document_type', 'unknown'),
                "signature_count": input_data.get('signature_count', 0),
                "is_valid": output_data.get('is_valid', False),
                "confidence": output_data.get('confidence', 0.0)
            }
            
            send_trace_minimal(
                name="gemini_pdf_evaluation",
                input_payload=input_data,
                output_payload=output_data,
                metadata=metadata
            )
        except Exception as e:
            print(f"Langfuse logging error: {e}")
    
    def batch_evaluate(self, validation_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Evaluate multiple PDFs in batch
        """
        results = []
        for i, validation_data in enumerate(validation_data_list):
            print(f"Evaluating document {i+1}/{len(validation_data_list)}")
            result = self.evaluate_pdf(validation_data)
            results.append(result)
        return results
