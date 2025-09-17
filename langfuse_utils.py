# langfuse_utils.py
from langfuse import Langfuse
import os
from typing import Dict, Any, Optional
from datetime import datetime

LF_PUBLIC = os.getenv("LF_PUBLIC_KEY")
LF_SECRET = os.getenv("LF_SECRET_KEY")
LF_HOST = os.getenv("LF_HOST", "https://api.langfuse.com")

# init only if keys present
lf_client = None
if LF_PUBLIC and LF_SECRET:
    try:
        lf_client = Langfuse(public_key=LF_PUBLIC, secret_key=LF_SECRET, host=LF_HOST)
        print("✓ Langfuse initialized successfully")
    except Exception as e:
        print("Langfuse init error:", e)
        lf_client = None
else:
    print("⚠ Langfuse not configured (optional)")

def send_trace_minimal(name: str, input_payload: dict, output_payload: dict, metadata: dict = None):
    """Send minimal trace to Langfuse"""
    if not lf_client:
        return None
    try:
        trace = lf_client.trace(name=name, metadata=metadata or {})
        trace.span(
            name="pdf_validation_process",
            input=input_payload,
            output=output_payload
        )
        trace.end()
        return trace.id
    except Exception as e:
        print("Langfuse trace error:", e)
        return None

def send_detailed_trace(
    name: str, 
    input_payload: Dict[str, Any], 
    output_payload: Dict[str, Any], 
    metadata: Dict[str, Any] = None,
    spans: list = None
) -> Optional[str]:
    """Send detailed trace with multiple spans to Langfuse"""
    if not lf_client:
        return None
    
    try:
        trace = lf_client.trace(
            name=name, 
            metadata=metadata or {},
            input=input_payload,
            output=output_payload
        )
        
        # Add custom spans if provided
        if spans:
            for span in spans:
                trace.span(
                    name=span.get("name", "custom_span"),
                    input=span.get("input", {}),
                    output=span.get("output", {}),
                    metadata=span.get("metadata", {})
                )
        
        trace.end()
        return trace.id
    except Exception as e:
        print("Langfuse detailed trace error:", e)
        return None

def log_validation_metrics(
    document_type: str,
    is_valid: bool,
    confidence: float,
    processing_time: float,
    signature_count: int,
    issues_count: int
) -> Optional[str]:
    """Log validation metrics to Langfuse"""
    if not lf_client:
        return None
    
    try:
        trace = lf_client.trace(
            name="validation_metrics",
            metadata={
                "document_type": document_type,
                "is_valid": is_valid,
                "confidence": confidence,
                "processing_time": processing_time,
                "signature_count": signature_count,
                "issues_count": issues_count,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        trace.span(
            name="validation_summary",
            input={
                "document_type": document_type,
                "signature_count": signature_count
            },
            output={
                "is_valid": is_valid,
                "confidence": confidence,
                "processing_time": processing_time,
                "issues_count": issues_count
            }
        )
        
        trace.end()
        return trace.id
    except Exception as e:
        print("Langfuse metrics logging error:", e)
        return None

def log_error(error_type: str, error_message: str, context: Dict[str, Any] = None) -> Optional[str]:
    """Log error to Langfuse"""
    if not lf_client:
        return None
    
    try:
        trace = lf_client.trace(
            name="validation_error",
            metadata={
                "error_type": error_type,
                "error_message": error_message,
                "timestamp": datetime.now().isoformat(),
                "context": context or {}
            }
        )
        
        trace.span(
            name="error_details",
            input=context or {},
            output={
                "error_type": error_type,
                "error_message": error_message
            }
        )
        
        trace.end()
        return trace.id
    except Exception as e:
        print("Langfuse error logging error:", e)
        return None
