# llm_judge.py
import json
from datetime import datetime
from typing import Dict, Any, List

# Try imports for modern Vertex AI
try:
    from vertexai.generative_models import GenerativeModel
    VERTEX_GEN_AVAILABLE = True
except Exception:
    VERTEX_GEN_AVAILABLE = False

# keep some rule config
REQUIRED_FIELDS = [
    "NIK", "Nama", "No Tel", "Email", "Departement", "Manager",
    "Range Tanggal", "Range Waktu", "Approved by", "User VPN"
]


def prepare_issues(ocr_data: Dict[str, Any], signature_valid: bool):
    issues: List[str] = []
    empty_fields: List[str] = []
    all_filled = True

    for field in REQUIRED_FIELDS:
        val = ocr_data.get(field, "")
        if not isinstance(val, str):
            try:
                val = str(val)
            except Exception:
                val = ""
        if not val.strip():
            issues.append(f"Field '{field}' kosong atau tidak diisi")
            empty_fields.append(field)
            all_filled = False

    # email check
    if ocr_data.get("Email", "").strip():
        if "@infomedia.co.id" not in ocr_data["Email"]:
            issues.append("Email tidak sesuai format perusahaan")
            all_filled = False

    # NIK basic check
    if ocr_data.get("NIK", "").strip():
        nik = ocr_data["NIK"].strip()
        if not nik.isdigit() or len(nik) < 5:
            issues.append("NIK tidak valid")
            all_filled = False

    # Range tanggal & waktu basic validation
    if ocr_data.get("Range Tanggal", "").strip():
        try:
            start, end = ocr_data["Range Tanggal"].split("–")
            start_date = datetime.strptime(start.strip(), "%d %b %Y")
            end_date = datetime.strptime(end.strip(), "%d %b %Y")
            if start_date >= end_date:
                issues.append("Range Tanggal tidak logis (mulai >= akhir)")
                all_filled = False
        except Exception:
            issues.append("Format Range Tanggal salah")
            all_filled = False

    if ocr_data.get("Range Waktu", "").strip():
        try:
            start_time, end_time = ocr_data["Range Waktu"].split("-")
            datetime.strptime(start_time.strip(), "%H:%M:%S")
            datetime.strptime(end_time.strip(), "%H:%M:%S")
        except Exception:
            issues.append("Format Range Waktu salah")
            all_filled = False

    # User VPN vs Nama
    if ocr_data.get("User VPN", "").strip() and ocr_data.get("Nama", "").strip():
        if ocr_data["Nama"].strip() not in ocr_data["User VPN"]:
            issues.append("User VPN tidak cocok dengan nama peminta")
            all_filled = False

    # signature
    if not signature_valid:
        issues.append("Tanda tangan tidak valid")
        all_filled = False

    return issues, all_filled, empty_fields


def safe_json_loads(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    if not text:
        return fallback
    try:
        return json.loads(text)
    except Exception:
        # attempt to extract JSON substring
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            sub = text[start:end]
            return json.loads(sub)
        except Exception:
            return fallback


def _call_llm(prompt: str) -> str:
    """
    Try to call vertexai GenerativeModel if available.
    Returns raw text or raises RuntimeError if not possible.
    """
    if VERTEX_GEN_AVAILABLE:
        try:
            model = GenerativeModel("gemini-1.5-flash")  # or another available model
            response = model.generate_content(prompt)
            return getattr(response, "text", "") or ""
        except Exception as e:
            raise RuntimeError(f"LLM call failed: {e}")
    else:
        # Not having vertexai available -> signal error to caller
        raise RuntimeError("GenerativeModel not available in environment")


def judge_form_vpn(ocr_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Input:
      ocr_data: dict — kalau berasal dari app.py parse_ocr_fields, akan berisi fields + "signature_valid"
    Returns:
      {
        "is_valid": bool,
        "issues": [...],
        "confidence": float (0..1),
        "remarks": str,
        "empty_fields": [...]
      }
    """
    # get signature flag from dict (if present)
    signature_valid = bool(ocr_data.get("signature_valid", False))

    # pre-checks (rule-based)
    issues, all_filled, empty_fields = prepare_issues(ocr_data, signature_valid)
    preliminary_valid = all_filled and signature_valid

    # build prompt (include rule-based issues to guide LLM)
    prompt = f"""
You are an assistant that judges the validity of a VPN request form.
Provide final judgement in JSON.

OCR-extracted fields:
{json.dumps(ocr_data, indent=2)}

Rule-based issues (preliminary):
{json.dumps(issues, indent=2)}

Empty fields:
{json.dumps(empty_fields, indent=2)}

Task:
1) Return JSON with keys: is_valid (bool), issues (list), confidence (0.0-1.0), remarks (string).
2) Combine rule-based issues and LLM findings.
3) If there are empty required fields, mark is_valid false.

Return only JSON.
"""

    fallback = {
        "is_valid": preliminary_valid,
        "issues": issues.copy(),
        "confidence": 0.5,
        "remarks": "Fallback: LLM unavailable or parse error."
    }

    # Try LLM call
    try:
        raw = _call_llm(prompt)
        parsed = safe_json_loads(raw, None)
        if isinstance(parsed, dict):
            # merge issues deterministic
            llm_issues = parsed.get("issues", []) or []
            merged = list(dict.fromkeys(issues + llm_issues))
            llm_is_valid = bool(parsed.get("is_valid", False))
            final_valid = llm_is_valid and (len(empty_fields) == 0)
            confidence = parsed.get("confidence", 0.5)
            try:
                confidence = float(confidence)
                if confidence > 1 and confidence <= 100:
                    confidence = confidence / 100.0
                confidence = max(0.0, min(1.0, confidence))
            except Exception:
                confidence = 0.5
            remarks = parsed.get("remarks", "") or parsed.get("explanation", "")
            result = {
                "is_valid": final_valid,
                "issues": merged,
                "confidence": confidence,
                "remarks": remarks
            }
        else:
            # LLM returned non-JSON -> fallback
            result = fallback
            result["remarks"] = "LLM returned non-JSON; using fallback."
            result["_llm_preview"] = (raw[:600] + "...") if raw else ""
    except Exception as e:
        result = fallback
        result["remarks"] = f"LLM error: {str(e)}"

    result["empty_fields"] = empty_fields
    return result
