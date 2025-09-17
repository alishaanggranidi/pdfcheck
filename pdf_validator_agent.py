import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pdf_processor import PDFProcessor
from gemini_judge import GeminiJudge
from langfuse_utils import send_trace_minimal
from config import settings

class PDFValidatorAgent:
    """
    Main PDF Validator Agent that orchestrates the entire validation process
    """
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.gemini_judge = GeminiJudge()
        self.app_name = settings.app_name
        
    def validate_pdf_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main method to validate a PDF file
        """
        start_time = datetime.now()
        
        result = {
            "file_path": pdf_path,
            "timestamp": start_time.isoformat(),
            "agent_version": "1.0.0",
            "processing_steps": [],
            "final_result": {},
            "processing_time_seconds": 0
        }
        
        try:
            # Step 1: Process PDF
            print(f"Processing PDF: {pdf_path}")
            result["processing_steps"].append({
                "step": "pdf_processing",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })
            
            pdf_data = self.pdf_processor.process_pdf(pdf_path)
            result["pdf_processing"] = pdf_data
            
            if pdf_data["processing_status"] == "error":
                result["final_result"] = {
                    "status": "error",
                    "message": f"PDF processing failed: {pdf_data.get('error', 'Unknown error')}",
                    "is_valid": False
                }
                result["processing_steps"][-1]["status"] = "failed"
                return result
            
            result["processing_steps"][-1]["status"] = "completed"
            
            # Step 2: LLM Evaluation
            print("Evaluating with Gemini LLM...")
            result["processing_steps"].append({
                "step": "llm_evaluation",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })
            
            validation_data = pdf_data["validation_data"]
            llm_result = self.gemini_judge.evaluate_pdf(validation_data)
            result["llm_evaluation"] = llm_result
            
            result["processing_steps"][-1]["status"] = "completed"
            
            # Step 3: Final Decision
            print("Making final decision...")
            result["processing_steps"].append({
                "step": "final_decision",
                "status": "started",
                "timestamp": datetime.now().isoformat()
            })
            
            final_result = self._make_final_decision(pdf_data, llm_result)
            result["final_result"] = final_result
            
            result["processing_steps"][-1]["status"] = "completed"
            
            # Calculate processing time
            end_time = datetime.now()
            result["processing_time_seconds"] = (end_time - start_time).total_seconds()
            
            # Log to Langfuse
            self._log_complete_validation(result)
            
            print(f"Validation completed in {result['processing_time_seconds']:.2f} seconds")
            print(f"Final status: {final_result['status']}")
            
        except Exception as e:
            result["final_result"] = {
                "status": "error",
                "message": f"Validation failed: {str(e)}",
                "is_valid": False
            }
            result["error"] = str(e)
            
            # Log error to Langfuse
            self._log_validation_error(result, str(e))
        
        return result
    
    def _make_final_decision(self, pdf_data: Dict[str, Any], llm_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make final decision based on PDF processing and LLM evaluation
        """
        # Extract key information
        document_type = pdf_data["document_type"]["document_type"]
        signature_count = pdf_data["signature_info"]["signature_count"]
        signature_valid = pdf_data["signature_info"]["signature_valid"]
        form_fields = pdf_data["form_fields"]
        
        # LLM evaluation results
        llm_is_valid = llm_result.get("is_valid", False)
        llm_confidence = llm_result.get("confidence", 0.0)
        llm_issues = llm_result.get("issues", [])
        llm_reasoning = llm_result.get("reasoning", "")
        
        # Final decision logic
        is_valid = llm_is_valid and signature_valid
        
        if is_valid:
            status = "approved_for_processing"
            message = f"Document approved. Type: {document_type}, Signatures: {signature_count}, Confidence: {llm_confidence:.2f}"
        else:
            status = "rejected_with_reason"
            reasons = []
            
            if not signature_valid:
                reasons.append(f"Insufficient signatures: {signature_count}/3 required")
            
            if llm_issues:
                reasons.extend(llm_issues[:3])  # Limit to top 3 issues
            
            if not reasons:
                reasons.append("Document does not meet validation criteria")
            
            message = f"Document rejected. Reasons: {'; '.join(reasons)}"
        
        return {
            "is_valid": is_valid,
            "status": status,
            "message": message,
            "confidence": llm_confidence,
            "document_type": document_type,
            "signature_count": signature_count,
            "signature_valid": signature_valid,
            "issues": llm_issues,
            "reasoning": llm_reasoning,
            "form_fields_completeness": len([f for f in form_fields.values() if f.strip()]) / len(form_fields) if form_fields else 0,
            "recommendations": llm_result.get("recommendations", [])
        }
    
    def validate_multiple_pdfs(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Validate multiple PDF files
        """
        results = []
        for i, pdf_path in enumerate(pdf_paths):
            print(f"\n=== Processing PDF {i+1}/{len(pdf_paths)}: {os.path.basename(pdf_path)} ===")
            result = self.validate_pdf_file(pdf_path)
            results.append(result)
        
        # Generate summary
        summary = self._generate_batch_summary(results)
        print(f"\n=== BATCH SUMMARY ===")
        print(f"Total processed: {summary['total_processed']}")
        print(f"Approved: {summary['approved_count']}")
        print(f"Rejected: {summary['rejected_count']}")
        print(f"Errors: {summary['error_count']}")
        print(f"Average processing time: {summary['avg_processing_time']:.2f}s")
        
        return results
    
    def _generate_batch_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of batch processing results
        """
        total = len(results)
        approved = sum(1 for r in results if r["final_result"].get("is_valid", False))
        rejected = sum(1 for r in results if r["final_result"].get("status") == "rejected_with_reason")
        errors = sum(1 for r in results if r["final_result"].get("status") == "error")
        
        processing_times = [r.get("processing_time_seconds", 0) for r in results]
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        return {
            "total_processed": total,
            "approved_count": approved,
            "rejected_count": rejected,
            "error_count": errors,
            "approval_rate": approved / total if total > 0 else 0,
            "avg_processing_time": avg_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_complete_validation(self, result: Dict[str, Any]):
        """
        Log complete validation result to Langfuse
        """
        try:
            input_data = {
                "file_path": result["file_path"],
                "processing_steps": len(result["processing_steps"]),
                "pdf_processing_status": result["pdf_processing"]["processing_status"]
            }
            
            output_data = {
                "final_status": result["final_result"]["status"],
                "is_valid": result["final_result"]["is_valid"],
                "confidence": result["final_result"].get("confidence", 0.0),
                "document_type": result["final_result"].get("document_type", "unknown"),
                "signature_count": result["final_result"].get("signature_count", 0),
                "processing_time": result["processing_time_seconds"]
            }
            
            metadata = {
                "agent_version": result["agent_version"],
                "app_name": self.app_name,
                "validation_timestamp": result["timestamp"]
            }
            
            send_trace_minimal(
                name="pdf_validation_complete",
                input_payload=input_data,
                output_payload=output_data,
                metadata=metadata
            )
        except Exception as e:
            print(f"Langfuse logging error: {e}")
    
    def _log_validation_error(self, result: Dict[str, Any], error_message: str):
        """
        Log validation error to Langfuse
        """
        try:
            input_data = {
                "file_path": result["file_path"],
                "error_message": error_message
            }
            
            output_data = {
                "status": "error",
                "is_valid": False
            }
            
            metadata = {
                "agent_version": result["agent_version"],
                "app_name": self.app_name,
                "error_type": "validation_error"
            }
            
            send_trace_minimal(
                name="pdf_validation_error",
                input_payload=input_data,
                output_payload=output_data,
                metadata=metadata
            )
        except Exception as e:
            print(f"Langfuse error logging failed: {e}")
    
    def get_validation_report(self, result: Dict[str, Any]) -> str:
        """
        Generate a human-readable validation report
        """
        final_result = result["final_result"]
        
        report = f"""
=== PDF VALIDATION REPORT ===
File: {os.path.basename(result['file_path'])}
Timestamp: {result['timestamp']}
Processing Time: {result['processing_time_seconds']:.2f} seconds

FINAL DECISION:
Status: {final_result['status'].upper()}
Valid: {'YES' if final_result['is_valid'] else 'NO'}
Confidence: {final_result.get('confidence', 0.0):.2f}

DOCUMENT ANALYSIS:
Type: {final_result.get('document_type', 'unknown')}
Signatures: {final_result.get('signature_count', 0)}/3 required
Signature Valid: {'YES' if final_result.get('signature_valid', False) else 'NO'}

REASONING:
{final_result.get('reasoning', 'No reasoning provided')}

ISSUES FOUND:
"""
        
        issues = final_result.get('issues', [])
        if issues:
            for i, issue in enumerate(issues, 1):
                report += f"{i}. {issue}\n"
        else:
            report += "No issues found.\n"
        
        recommendations = final_result.get('recommendations', [])
        if recommendations:
            report += "\nRECOMMENDATIONS:\n"
            for i, rec in enumerate(recommendations, 1):
                report += f"{i}. {rec}\n"
        
        return report
