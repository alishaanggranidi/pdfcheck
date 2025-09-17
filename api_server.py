from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import shutil
from typing import List, Dict, Any
from pdf_validator_agent import PDFValidatorAgent
from config import settings
import uvicorn

app = FastAPI(
    title="PDF Validator Agent API",
    description="API untuk validasi dokumen PDF permohonan VPN menggunakan Google Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = PDFValidatorAgent()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "PDF Validator Agent API",
        "version": "1.0.0",
        "status": "running",
        "app_name": settings.app_name
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "pdf_processor": "active",
            "gemini_judge": "active",
            "langfuse": "active" if settings.langfuse_public_key else "inactive"
        }
    }

@app.post("/validate-pdf")
async def validate_pdf(file: UploadFile = File(...)):
    """
    Validate a single PDF file
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)
    
    max_size = settings.max_file_size_mb * 1024 * 1024  # Convert MB to bytes
    if file_size > max_size:
        raise HTTPException(
            status_code=400, 
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    # Create temporary file
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Validate PDF
        result = agent.validate_pdf_file(temp_file_path)
        
        # Generate report
        report = agent.get_validation_report(result)
        
        return {
            "success": True,
            "filename": file.filename,
            "file_size_bytes": file_size,
            "validation_result": result["final_result"],
            "processing_time_seconds": result["processing_time_seconds"],
            "report": report,
            "raw_result": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
    
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/validate-multiple-pdfs")
async def validate_multiple_pdfs(files: List[UploadFile] = File(...)):
    """
    Validate multiple PDF files
    """
    if len(files) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Maximum 10 files per batch")
    
    results = []
    temp_files = []
    
    try:
        # Process each file
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "File must be a PDF"
                })
                continue
            
            # Create temporary file
            content = await file.read()
            file_size = len(content)
            
            max_size = settings.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"File too large. Maximum size: {settings.max_file_size_mb}MB"
                })
                continue
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
                temp_files.append(temp_file_path)
            
            # Validate PDF
            try:
                result = agent.validate_pdf_file(temp_file_path)
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "file_size_bytes": file_size,
                    "validation_result": result["final_result"],
                    "processing_time_seconds": result["processing_time_seconds"],
                    "report": agent.get_validation_report(result)
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        # Generate batch summary
        successful_results = [r for r in results if r.get("success", False)]
        summary = {
            "total_files": len(files),
            "successful_validations": len(successful_results),
            "failed_validations": len(results) - len(successful_results),
            "approved_count": sum(1 for r in successful_results if r["validation_result"]["is_valid"]),
            "rejected_count": sum(1 for r in successful_results if not r["validation_result"]["is_valid"])
        }
        
        return {
            "success": True,
            "summary": summary,
            "results": results
        }
        
    finally:
        # Clean up temporary files
        for temp_file_path in temp_files:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

@app.get("/validation-history")
async def get_validation_history():
    """
    Get validation history (placeholder - would integrate with database)
    """
    return {
        "message": "Validation history endpoint",
        "note": "This would typically connect to a database to retrieve validation history"
    }

@app.get("/config")
async def get_config():
    """
    Get current configuration (without sensitive data)
    """
    return {
        "app_name": settings.app_name,
        "min_signatures": settings.min_signatures,
        "max_file_size_mb": settings.max_file_size_mb,
        "log_level": settings.log_level,
        "langfuse_enabled": bool(settings.langfuse_public_key),
        "gemini_enabled": bool(settings.google_api_key)
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
