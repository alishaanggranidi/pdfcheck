# PDF Validator Agent - Google ADK

Agent PDF Validator yang kompatibel dengan Google ADK web interface, menggunakan Google Gemini 2.0 untuk validasi dokumen permohonan VPN. Aplikasi ini dirancang khusus untuk berjalan langsung di Google ADK tanpa perlu HTML/CSS terpisah.

## 🚀 Fitur Utama

- **Ekstraksi Konten PDF**: Membaca dan mengekstrak teks dari dokumen PDF
- **Deteksi Jenis Dokumen**: Mengidentifikasi apakah dokumen adalah permohonan VPN baru atau perpanjangan
- **Validasi Tanda Tangan**: Mendeteksi dan memvalidasi minimal 3 tanda tangan
- **LLM Judge**: Menggunakan Google Gemini 2.0 untuk evaluasi cerdas
- **Integrasi Langfuse**: Logging dan monitoring proses validasi
- **API REST**: Endpoint untuk integrasi dengan sistem lain
- **Google ADK Interface**: Interface sederhana untuk Google ADK tanpa CLI

## 📋 Persyaratan Sistem

- Python 3.8+
- Google API Key untuk Gemini
- Langfuse account (opsional)

## 🛠️ Instalasi

1. **Clone repository**
```bash
git clone <repository-url>
cd pdf-validator-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
```bash
# Run setup script
python setup_env.py

# Or manually create .env file with your API keys
GOOGLE_API_KEY=your_google_api_key_here
LF_PUBLIC_KEY=your_langfuse_public_key
LF_SECRET_KEY=your_langfuse_secret_key
LF_HOST=https://api.langfuse.com
```

4. **Verifikasi instalasi**
```bash
python start_adk.py
```

## 🎯 Penggunaan

### Google ADK Interface (Recommended)

**Menjalankan aplikasi:**
```bash
python start_adk.py
```

**Atau untuk web interface:**
```bash
python run_adk.py
```

**Gunakan functions di Google ADK:**
```python
from adk_web_app import validate_pdf, validate_pdf_bytes, batch_validate

# Validate single PDF
result = validate_pdf("document.pdf")

# Validate PDF from bytes
result = validate_pdf_bytes(pdf_data, "document.pdf")

# Batch validate
results = batch_validate(["doc1.pdf", "doc2.pdf"])
```

### File Structure

```
pdfcheck/
├── adk_web_app.py          # Main ADK web application
├── adk_config.py           # ADK configuration
├── start_adk.py            # Simple ADK launcher
├── run_adk.py              # Full ADK launcher with web interface
├── pdf_validator_agent.py  # Core PDF validator
├── gemini_judge.py         # Gemini 2.0 integration
├── pdf_processor.py        # PDF processing
├── config.py               # Configuration management
├── langfuse_utils.py       # Langfuse integration
├── setup_env.py            # Environment setup
└── requirements.txt        # Dependencies
```

### API Server

**Menjalankan server:**
```bash
python api_server.py
```

Server akan berjalan di `http://localhost:8000`

**API Endpoints:**

- `GET /` - Health check
- `GET /health` - Detailed health check
- `POST /validate-pdf` - Validasi file PDF tunggal
- `POST /validate-multiple-pdfs` - Validasi multiple PDF
- `GET /config` - Konfigurasi saat ini

**Contoh penggunaan API:**

```bash
# Validasi file tunggal
curl -X POST "http://localhost:8000/validate-pdf" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.pdf"

# Validasi multiple files
curl -X POST "http://localhost:8000/validate-multiple-pdfs" \
     -H "Content-Type: multipart/form-data" \
     -F "files=@doc1.pdf" \
     -F "files=@doc2.pdf"
```

### Python Library

```python
from pdf_validator_agent import PDFValidatorAgent

# Initialize agent
agent = PDFValidatorAgent()

# Validate single PDF
result = agent.validate_pdf_file("document.pdf")

# Check result
if result["final_result"]["is_valid"]:
    print("Document approved!")
else:
    print("Document rejected:", result["final_result"]["message"])
```

## 📊 Output Format

### Hasil Validasi

```json
{
  "file_path": "document.pdf",
  "timestamp": "2024-01-01T12:00:00",
  "final_result": {
    "is_valid": true,
    "status": "approved_for_processing",
    "message": "Document approved. Type: new_vpn_request, Signatures: 3, Confidence: 0.95",
    "confidence": 0.95,
    "document_type": "new_vpn_request",
    "signature_count": 3,
    "signature_valid": true,
    "issues": [],
    "reasoning": "All required fields are present and signatures are valid",
    "recommendations": []
  },
  "processing_time_seconds": 2.5
}
```

### Status Codes

- `approved_for_processing`: Dokumen valid dan dapat diproses
- `rejected_with_reason`: Dokumen ditolak dengan alasan spesifik
- `error`: Terjadi error dalam proses validasi

## 🔧 Konfigurasi

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google Gemini API key | Required |
| `LF_PUBLIC_KEY` | Langfuse public key | Optional |
| `LF_SECRET_KEY` | Langfuse secret key | Optional |
| `LF_HOST` | Langfuse host URL | https://api.langfuse.com |
| `APP_NAME` | Application name | PDF_Validator_Agent |
| `LOG_LEVEL` | Logging level | INFO |

### Konfigurasi Validasi

- **Min Signatures**: Minimal 3 tanda tangan (dapat diubah di `config.py`)
- **Max File Size**: 10MB per file (dapat diubah di `config.py`)
- **Required Fields**: NIK, Nama, Email, dll. (dapat diubah di `llm_judge.py`)

## 📈 Monitoring dengan Langfuse

Sistem terintegrasi dengan Langfuse untuk:

- **Logging Proses**: Input, output, dan reasoning dari setiap validasi
- **Monitoring Kualitas**: Tracking akurasi dan performa evaluasi
- **Audit Trail**: Riwayat validasi untuk keperluan audit
- **Analytics**: Statistik penggunaan dan performa

## 🏗️ Arsitektur

```
PDF Validator Agent
├── pdf_processor.py      # Ekstraksi konten PDF
├── gemini_judge.py       # LLM evaluation dengan Gemini
├── pdf_validator_agent.py # Main orchestrator
├── api_server.py         # FastAPI server
├── cli_validator.py      # Command line interface
├── langfuse_utils.py     # Langfuse integration
├── llm_judge.py          # Legacy LLM judge
└── config.py             # Configuration management
```

## 🔍 Proses Validasi

1. **PDF Processing**: Ekstraksi teks dan deteksi tanda tangan
2. **Content Analysis**: Deteksi jenis dokumen dan ekstraksi field
3. **LLM Evaluation**: Evaluasi menggunakan Google Gemini
4. **Final Decision**: Keputusan final berdasarkan semua analisis
5. **Logging**: Pencatatan ke Langfuse untuk monitoring

## 🚨 Troubleshooting

### Error: "GOOGLE_API_KEY not found"
- Pastikan environment variable `GOOGLE_API_KEY` sudah diset
- Verifikasi API key valid di Google Cloud Console

### Error: "PDF extraction failed"
- Pastikan file adalah PDF yang valid
- Coba dengan PDF yang lebih sederhana
- Periksa ukuran file (max 10MB)

### Error: "LLM evaluation failed"
- Periksa koneksi internet
- Verifikasi Google API key
- Cek quota API Gemini

### Langfuse tidak berfungsi
- Langfuse bersifat opsional
- Sistem tetap berfungsi tanpa Langfuse
- Periksa kredensial Langfuse jika diperlukan

## 📝 Contoh Dokumen

Sistem dirancang untuk memvalidasi dokumen permohonan VPN dengan format:

- **Header**: Judul dokumen (Permohonan VPN Baru/Perpanjangan)
- **Form Fields**: NIK, Nama, Email, Departement, dll.
- **Tanda Tangan**: Minimal 3 tanda tangan (pemohon, atasan, IT)

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch
3. Commit perubahan
4. Push ke branch
5. Buat Pull Request

## 📄 Lisensi

MIT License - lihat file LICENSE untuk detail.

## 📞 Support

Untuk pertanyaan atau bantuan, silakan buat issue di repository atau hubungi tim development.
