# Google ADK Quick Start Guide

## 🚀 Quick Start

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup environment:**
```bash
python setup_env.py
```

3. **Start ADK app:**
```bash
python start_adk.py
```

## 📁 File Structure (Cleaned)

```
pdfcheck/
├── start_adk.py            # ⭐ Simple ADK launcher
├── run_adk.py              # Full ADK launcher with web interface
├── adk_web_app.py          # Main ADK web application
├── adk_config.py           # ADK configuration
├── pdf_validator_agent.py  # Core PDF validator
├── gemini_judge.py         # Gemini 2.0 integration
├── pdf_processor.py        # PDF processing
├── config.py               # Configuration management
├── langfuse_utils.py       # Langfuse integration
├── setup_env.py            # Environment setup
├── requirements.txt        # Dependencies
├── README.md               # Main documentation
├── ADK_README.md           # Detailed ADK documentation
└── ADK_QUICK_START.md      # This file
```

## 🎯 Usage in Google ADK

### Import Functions
```python
from adk_web_app import validate_pdf, validate_pdf_bytes, batch_validate, get_config, health
```

### Validate Single PDF
```python
result = validate_pdf("document.pdf")
print(f"Valid: {result['is_valid']}")
print(f"Status: {result['status']}")
```

### Validate PDF from Bytes
```python
with open("document.pdf", "rb") as f:
    pdf_data = f.read()
result = validate_pdf_bytes(pdf_data, "document.pdf")
```

### Batch Validate
```python
results = batch_validate(["doc1.pdf", "doc2.pdf", "doc3.pdf"])
print(f"Approved: {results['summary']['approved_count']}")
```

### Health Check
```python
status = health()
print(f"System: {status['status']}")
```

## ⚙️ Configuration

Set environment variables:
```bash
GOOGLE_API_KEY=your_google_api_key_here
LF_PUBLIC_KEY=your_langfuse_public_key (optional)
LF_SECRET_KEY=your_langfuse_secret_key (optional)
```

## 🔧 Troubleshooting

- **GOOGLE_API_KEY not set**: Run `python setup_env.py`
- **Import errors**: Run `pip install -r requirements.txt`
- **Agent not initialized**: Check Google API key and internet connection

## 📊 Response Format

```json
{
  "success": true,
  "is_valid": true,
  "status": "approved_for_processing",
  "message": "Document approved. Type: new_vpn_request, Signatures: 3, Confidence: 0.95",
  "confidence": 0.95,
  "document_type": "new_vpn_request",
  "signature_count": 3,
  "signature_valid": true,
  "issues": [],
  "recommendations": [],
  "processing_time_seconds": 2.5
}
```

## ✅ Ready for Google ADK!

Your PDF Validator Agent is now ready to use in Google ADK web interface!
