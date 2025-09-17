# PDF Validator Agent - Google ADK Web Interface

Aplikasi validasi PDF yang kompatibel dengan Google ADK web interface, menggunakan Google Gemini 2.0 untuk validasi dokumen permohonan VPN.

## 🚀 Fitur Google ADK

- **Kompatibel dengan Google ADK**: Langsung terintegrasi dengan Google ADK web interface
- **Gemini 2.0**: Menggunakan Google Gemini 2.0 untuk validasi cerdas
- **API Endpoints**: Endpoint REST untuk integrasi dengan ADK
- **File Upload**: Support upload file PDF melalui ADK web
- **Batch Processing**: Validasi multiple file PDF sekaligus
- **Real-time Results**: Hasil validasi langsung ditampilkan di ADK

## 📋 Persyaratan

- Python 3.8+
- Google API Key untuk Gemini 2.0
- Google ADK environment
- Dependencies yang terinstall

## 🛠️ Instalasi

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Setup environment variables**:
```bash
python setup_env.py
```

3. **Set Google API Key**:
```bash
set GOOGLE_API_KEY=your_google_api_key_here
```

## 🎯 Penggunaan Google ADK

### 1. Jalankan ADK App
```bash
python run_adk.py
```

### 2. Gunakan Functions di ADK Code
```python
from adk_web_app import validate_pdf, validate_pdf_bytes, batch_validate

# Validate single PDF
result = validate_pdf("document.pdf")

# Validate PDF from bytes
with open("document.pdf", "rb") as f:
    pdf_bytes = f.read()
result = validate_pdf_bytes(pdf_bytes, "document.pdf")

# Batch validate
results = batch_validate(["doc1.pdf", "doc2.pdf"])
```

### 3. ADK Web Interface
Aplikasi akan berjalan di `http://localhost:8080` dengan endpoint:

- `GET /` - Home page
- `POST /validate-pdf` - Validate single PDF
- `POST /validate-batch` - Validate multiple PDFs
- `GET /health` - Health check
- `GET /config` - Configuration info

## 📊 Response Format

### Single PDF Validation
```json
{
  "success": true,
  "filename": "document.pdf",
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

### Batch Validation
```json
{
  "success": true,
  "summary": {
    "total_files": 3,
    "successful_validations": 3,
    "failed_validations": 0,
    "approved_count": 2,
    "rejected_count": 1
  },
  "results": [...]
}
```

## 🔧 Konfigurasi ADK

File `adk_config.py` berisi konfigurasi untuk Google ADK:

```python
ADK_CONFIG = {
    "app_name": "PDF Validator Agent",
    "version": "2.0.0",
    "adk_web": {
        "enabled": True,
        "port": 8080,
        "host": "0.0.0.0"
    },
    "validation": {
        "min_signatures": 3,
        "required_fields": ["NIK", "Nama", "Email", ...]
    },
    "gemini": {
        "model": "gemini-2.0-flash-exp"
    }
}
```

## 🌐 ADK Web Interface

### Upload PDF
```javascript
// Upload single PDF
const formData = new FormData();
formData.append('file', pdfFile);

fetch('/validate-pdf', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(result => console.log(result));
```

### Batch Upload
```javascript
// Upload multiple PDFs
const formData = new FormData();
pdfFiles.forEach(file => {
    formData.append('files', file);
});

fetch('/validate-batch', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(results => console.log(results));
```

## 📈 Monitoring

Aplikasi terintegrasi dengan Langfuse untuk monitoring:
- Logging proses validasi
- Tracking performa
- Audit trail
- Analytics

## 🔍 Troubleshooting

### Error: "GOOGLE_API_KEY not found"
- Pastikan environment variable `GOOGLE_API_KEY` sudah diset
- Verifikasi API key valid di Google Cloud Console

### Error: "Agent not initialized"
- Periksa koneksi internet
- Verifikasi Google API key
- Cek quota API Gemini

### ADK Web tidak bisa diakses
- Pastikan port 8080 tidak digunakan aplikasi lain
- Periksa firewall settings
- Cek log aplikasi untuk error details

## 📝 Contoh Penggunaan di ADK

### 1. Simple Validation
```python
from adk_web_app import validate_pdf

# Validate PDF file
result = validate_pdf("vpn_application.pdf")

if result["success"] and result["is_valid"]:
    print("✓ Document approved!")
else:
    print("✗ Document rejected:", result["message"])
```

### 2. Batch Processing
```python
from adk_web_app import batch_validate

# Validate multiple PDFs
pdf_files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = batch_validate(pdf_files)

print(f"Processed {results['summary']['total_files']} files")
print(f"Approved: {results['summary']['approved_count']}")
print(f"Rejected: {results['summary']['rejected_count']}")
```

### 3. Health Check
```python
from adk_web_app import health

# Check system health
status = health()
print(f"System status: {status['status']}")
print(f"Gemini model: {status.get('gemini_model', 'Unknown')}")
```

## 🚀 Deployment

### Local Development
```bash
python run_adk.py
```

### Production
```bash
# Set environment variables
export GOOGLE_API_KEY=your_key
export ADK_WEB_PORT=8080

# Run with uvicorn
uvicorn adk_web_app:app --host 0.0.0.0 --port 8080
```

## 📞 Support

Untuk pertanyaan atau bantuan terkait Google ADK integration:
- Periksa log aplikasi
- Verifikasi konfigurasi ADK
- Hubungi tim development

## 📄 Lisensi

MIT License - lihat file LICENSE untuk detail.
