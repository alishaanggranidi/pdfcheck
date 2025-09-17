#!/usr/bin/env python3
"""
Google ADK Configuration for PDF Validator Agent
Configuration file for Google ADK web interface
"""

import os
from typing import Dict, Any

# ADK Web Interface Configuration
ADK_CONFIG = {
    "app_name": "PDF Validator Agent",
    "version": "2.0.0",
    "description": "Validasi dokumen PDF permohonan VPN menggunakan Google Gemini 2.0",
    "author": "PDF Validator Team",
    
    # ADK Web Interface Settings
    "adk_web": {
        "enabled": True,
        "port": 8080,
        "host": "0.0.0.0",
        "debug": False,
        "auto_reload": True
    },
    
    # API Endpoints for ADK
    "endpoints": {
        "validate_pdf": "/validate-pdf",
        "validate_batch": "/validate-batch", 
        "health": "/health",
        "config": "/config",
        "upload": "/upload"
    },
    
    # File Upload Settings
    "upload": {
        "max_file_size_mb": 10,
        "allowed_extensions": [".pdf"],
        "temp_dir": "temp",
        "results_dir": "results"
    },
    
    # Validation Settings
    "validation": {
        "min_signatures": 3,
        "required_fields": [
            "NIK", "Nama", "No Tel", "Email", "Departement",
            "Manager", "Range Tanggal", "Range Waktu", "Approved by", "User VPN"
        ],
        "email_domain": "@infomedia.co.id"
    },
    
    # Gemini Settings
    "gemini": {
        "model": "gemini-2.0-flash-exp",
        "temperature": 0.1,
        "max_tokens": 2048
    },
    
    # Logging Settings
    "logging": {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "logs/adk_web.log"
    }
}

def get_adk_config() -> Dict[str, Any]:
    """Get ADK configuration"""
    return ADK_CONFIG

def get_adk_endpoint(endpoint_name: str) -> str:
    """Get ADK endpoint URL"""
    return ADK_CONFIG["endpoints"].get(endpoint_name, "")

def is_adk_web_enabled() -> bool:
    """Check if ADK web interface is enabled"""
    return ADK_CONFIG["adk_web"]["enabled"]

def get_upload_config() -> Dict[str, Any]:
    """Get upload configuration"""
    return ADK_CONFIG["upload"]

def get_validation_config() -> Dict[str, Any]:
    """Get validation configuration"""
    return ADK_CONFIG["validation"]

def get_gemini_config() -> Dict[str, Any]:
    """Get Gemini configuration"""
    return ADK_CONFIG["gemini"]

def get_logging_config() -> Dict[str, Any]:
    """Get logging configuration"""
    return ADK_CONFIG["logging"]

# Environment-specific overrides
def load_adk_config_from_env():
    """Load ADK configuration from environment variables"""
    config = ADK_CONFIG.copy()
    
    # Override from environment variables
    if os.getenv("ADK_WEB_PORT"):
        config["adk_web"]["port"] = int(os.getenv("ADK_WEB_PORT"))
    
    if os.getenv("ADK_WEB_HOST"):
        config["adk_web"]["host"] = os.getenv("ADK_WEB_HOST")
    
    if os.getenv("ADK_WEB_DEBUG"):
        config["adk_web"]["debug"] = os.getenv("ADK_WEB_DEBUG").lower() == "true"
    
    if os.getenv("MAX_FILE_SIZE_MB"):
        config["upload"]["max_file_size_mb"] = int(os.getenv("MAX_FILE_SIZE_MB"))
    
    if os.getenv("MIN_SIGNATURES"):
        config["validation"]["min_signatures"] = int(os.getenv("MIN_SIGNATURES"))
    
    if os.getenv("GEMINI_MODEL"):
        config["gemini"]["model"] = os.getenv("GEMINI_MODEL")
    
    if os.getenv("LOG_LEVEL"):
        config["logging"]["level"] = os.getenv("LOG_LEVEL")
    
    return config

# Get final configuration
FINAL_ADK_CONFIG = load_adk_config_from_env()

def get_final_config() -> Dict[str, Any]:
    """Get final ADK configuration with environment overrides"""
    return FINAL_ADK_CONFIG
