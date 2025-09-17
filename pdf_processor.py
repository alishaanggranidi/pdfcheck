import io
import re
from typing import Dict, List, Any, Optional, Tuple
import PyPDF2
import pdfplumber
from PIL import Image
import cv2
import numpy as np
from config import settings

class PDFProcessor:
    """PDF processing class for extracting content and validating signatures"""
    
    def __init__(self):
        self.min_signatures = settings.min_signatures
        
    def extract_text_content(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text content from PDF using multiple methods
        """
        content = {
            "raw_text": "",
            "structured_data": {},
            "pages": [],
            "extraction_method": "pdfplumber"
        }
        
        try:
            # Method 1: Using pdfplumber (better for structured data)
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    full_text += f"\n--- Page {i+1} ---\n{page_text}"
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    if tables:
                        content["pages"].append({
                            "page_number": i + 1,
                            "text": page_text,
                            "tables": tables
                        })
                    else:
                        content["pages"].append({
                            "page_number": i + 1,
                            "text": page_text,
                            "tables": []
                        })
                
                content["raw_text"] = full_text
                
        except Exception as e:
            print(f"pdfplumber extraction failed: {e}")
            
            # Fallback: Using PyPDF2
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    full_text = ""
                    for i, page in enumerate(pdf_reader.pages):
                        page_text = page.extract_text()
                        full_text += f"\n--- Page {i+1} ---\n{page_text}"
                        content["pages"].append({
                            "page_number": i + 1,
                            "text": page_text,
                            "tables": []
                        })
                    content["raw_text"] = full_text
                    content["extraction_method"] = "PyPDF2"
            except Exception as e2:
                print(f"PyPDF2 extraction also failed: {e2}")
                content["error"] = f"PDF extraction failed: {e2}"
        
        return content
    
    def detect_document_type(self, text_content: str) -> Dict[str, Any]:
        """
        Detect if document is VPN request or extension based on content
        """
        text_lower = text_content.lower()
        
        # Keywords for new VPN request
        new_vpn_keywords = [
            "permohonan vpn baru",
            "request vpn baru", 
            "pengajuan vpn baru",
            "new vpn request",
            "vpn baru",
            "permohonan akses vpn"
        ]
        
        # Keywords for VPN extension
        extension_keywords = [
            "perpanjangan vpn",
            "vpn extension",
            "perpanjangan akses vpn",
            "extend vpn",
            "renewal vpn",
            "perpanjangan"
        ]
        
        new_vpn_score = sum(1 for keyword in new_vpn_keywords if keyword in text_lower)
        extension_score = sum(1 for keyword in extension_keywords if keyword in text_lower)
        
        if new_vpn_score > extension_score:
            document_type = "new_vpn_request"
            confidence = min(0.9, 0.5 + (new_vpn_score * 0.1))
        elif extension_score > new_vpn_score:
            document_type = "vpn_extension"
            confidence = min(0.9, 0.5 + (extension_score * 0.1))
        else:
            document_type = "unknown"
            confidence = 0.3
        
        return {
            "document_type": document_type,
            "confidence": confidence,
            "new_vpn_score": new_vpn_score,
            "extension_score": extension_score
        }
    
    def extract_form_fields(self, text_content: str) -> Dict[str, str]:
        """
        Extract form fields from PDF text using regex patterns
        """
        fields = {}
        
        # Common field patterns
        field_patterns = {
            "NIK": r"(?:NIK|Nomor Induk Karyawan)[\s:]*([A-Z0-9]+)",
            "Nama": r"(?:Nama|Name)[\s:]*([A-Za-z\s]+)",
            "No Tel": r"(?:No\.?\s*Tel|Telepon|Phone)[\s:]*([0-9\s\-\+\(\)]+)",
            "Email": r"(?:Email|E-mail)[\s:]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            "Departement": r"(?:Departement|Department|Dept)[\s:]*([A-Za-z\s]+)",
            "Manager": r"(?:Manager|Atasan)[\s:]*([A-Za-z\s]+)",
            "Range Tanggal": r"(?:Range Tanggal|Date Range)[\s:]*([0-9\s\-\/]+)",
            "Range Waktu": r"(?:Range Waktu|Time Range)[\s:]*([0-9\s\-\:]+)",
            "Approved by": r"(?:Approved by|Disetujui oleh)[\s:]*([A-Za-z\s]+)",
            "User VPN": r"(?:User VPN|VPN User)[\s:]*([A-Za-z0-9\s]+)"
        }
        
        for field_name, pattern in field_patterns.items():
            matches = re.findall(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                # Take the first match and clean it
                value = matches[0].strip()
                fields[field_name] = value
        
        return fields
    
    def detect_signatures(self, pdf_path: str) -> Dict[str, Any]:
        """
        Detect signatures in PDF using image processing
        """
        signature_info = {
            "signature_count": 0,
            "signature_locations": [],
            "signature_valid": False,
            "signature_details": []
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Convert page to image
                    page_image = page.to_image(resolution=150)
                    img_array = np.array(page_image.original)
                    
                    # Convert to grayscale
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                    
                    # Apply threshold to detect dark areas (signatures)
                    _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
                    
                    # Find contours
                    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    # Filter contours that might be signatures
                    for contour in contours:
                        area = cv2.contourArea(contour)
                        x, y, w, h = cv2.boundingRect(contour)
                        
                        # Signature characteristics: reasonable size and aspect ratio
                        if (area > 500 and area < 50000 and 
                            w > 50 and h > 20 and 
                            w/h > 1.5 and w/h < 8):
                            
                            signature_info["signature_count"] += 1
                            signature_info["signature_locations"].append({
                                "page": page_num + 1,
                                "x": x, "y": y, "width": w, "height": h,
                                "area": area
                            })
                            
                            signature_info["signature_details"].append({
                                "page": page_num + 1,
                                "coordinates": (x, y, w, h),
                                "area": area,
                                "confidence": min(0.9, area / 10000)
                            })
        
        except Exception as e:
            print(f"Signature detection error: {e}")
            signature_info["error"] = str(e)
        
        # Validate signatures
        signature_info["signature_valid"] = (
            signature_info["signature_count"] >= self.min_signatures
        )
        
        return signature_info
    
    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main method to process PDF and extract all information
        """
        result = {
            "file_path": pdf_path,
            "processing_status": "success",
            "extracted_content": {},
            "document_type": {},
            "form_fields": {},
            "signature_info": {},
            "validation_result": {}
        }
        
        try:
            # Extract text content
            result["extracted_content"] = self.extract_text_content(pdf_path)
            
            # Detect document type
            result["document_type"] = self.detect_document_type(
                result["extracted_content"]["raw_text"]
            )
            
            # Extract form fields
            result["form_fields"] = self.extract_form_fields(
                result["extracted_content"]["raw_text"]
            )
            
            # Detect signatures
            result["signature_info"] = self.detect_signatures(pdf_path)
            
            # Combine all data for validation
            validation_data = {
                **result["form_fields"],
                "signature_valid": result["signature_info"]["signature_valid"],
                "signature_count": result["signature_info"]["signature_count"],
                "document_type": result["document_type"]["document_type"],
                "raw_text": result["extracted_content"]["raw_text"]
            }
            
            result["validation_data"] = validation_data
            
        except Exception as e:
            result["processing_status"] = "error"
            result["error"] = str(e)
        
        return result
