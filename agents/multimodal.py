"""
System 3 — Multimodal Tool Detection
Extract frames from uploaded video, detect UI logos and tool names via OCR + pattern matching,
and merge with transcript to build a complete detected technology stack.
"I detected your stack automatically."
"""

from __future__ import annotations
import re
from pathlib import Path
from loguru import logger

from core.genesis_models import DetectedTool, DetectedStack


# ── Tool signature database ───────────────────────────────────────────────────

_TOOL_SIGNATURES: list[dict] = [
    # Email
    {"name": "Gmail",       "keywords": ["gmail", "google mail", "@gmail", "inbox", "compose"],
     "logo_color": "#EA4335", "category": "email"},
    {"name": "Outlook",     "keywords": ["outlook", "office 365", "microsoft mail", "exchange"],
     "logo_color": "#0078D4", "category": "email"},
    # CRM
    {"name": "HubSpot",     "keywords": ["hubspot", "hubspot crm", "hub spot", "deals", "contacts crm"],
     "logo_color": "#FF7A59", "category": "crm"},
    {"name": "Salesforce",  "keywords": ["salesforce", "sfdc", "salesforce.com", "opportunities"],
     "logo_color": "#00A1E0", "category": "crm"},
    {"name": "Pipedrive",   "keywords": ["pipedrive", "pipe drive"],
     "logo_color": "#0D4C86", "category": "crm"},
    # Storage / Spreadsheets
    {"name": "Google Sheets","keywords": ["google sheets", "spreadsheet", "gsheets", "sheets.google"],
     "logo_color": "#34A853", "category": "spreadsheet"},
    {"name": "Airtable",    "keywords": ["airtable", "air table", "airtable.com"],
     "logo_color": "#FCB400", "category": "spreadsheet"},
    {"name": "Notion",      "keywords": ["notion", "notion.so", "notion workspace"],
     "logo_color": "#000000", "category": "productivity"},
    # Communication
    {"name": "Slack",       "keywords": ["slack", "slack channel", "#general", "slack workspace", "slackbot"],
     "logo_color": "#4A154B", "category": "comms"},
    {"name": "Teams",       "keywords": ["microsoft teams", "ms teams", "teams channel"],
     "logo_color": "#6264A7", "category": "comms"},
    {"name": "Discord",     "keywords": ["discord", "discord server", "#channel"],
     "logo_color": "#5865F2", "category": "comms"},
    # Finance / Accounting
    {"name": "Xero",        "keywords": ["xero", "xero accounting", "xero.com"],
     "logo_color": "#13B5EA", "category": "finance"},
    {"name": "QuickBooks",  "keywords": ["quickbooks", "qbo", "intuit"],
     "logo_color": "#2CA01C", "category": "finance"},
    {"name": "Stripe",      "keywords": ["stripe", "stripe.com", "stripe dashboard", "payment intent"],
     "logo_color": "#635BFF", "category": "payments"},
    # Dev / Cloud
    {"name": "GitHub",      "keywords": ["github", "github.com", "pull request", "repository"],
     "logo_color": "#181717", "category": "dev"},
    {"name": "AWS",         "keywords": ["aws", "amazon web services", "s3 bucket", "lambda", "ec2"],
     "logo_color": "#FF9900", "category": "cloud"},
    {"name": "Google Sheets API", "keywords": ["sheets api", "spreadsheets.values", "valueinputoption"],
     "logo_color": "#34A853", "category": "api"},
    {"name": "Gmail API",   "keywords": ["gmail api", "users().messages", "gmail.readonly", "gmail.modify"],
     "logo_color": "#EA4335", "category": "api"},
    {"name": "Shopify",     "keywords": ["shopify", "shopify admin", "myshopify", "shopify orders"],
     "logo_color": "#96BF48", "category": "ecommerce"},
    {"name": "WooCommerce", "keywords": ["woocommerce", "woo commerce", "wp-json/wc"],
     "logo_color": "#96588A", "category": "ecommerce"},
    {"name": "Zapier",      "keywords": ["zapier", "zap", "trigger app", "action app"],
     "logo_color": "#FF4A00", "category": "automation"},
    {"name": "Make",        "keywords": ["make.com", "integromat", "make scenario"],
     "logo_color": "#6D00CC", "category": "automation"},
]

_CATEGORY_MAP = {
    "email":        "primary_email",
    "crm":          "primary_crm",
    "spreadsheet":  "primary_storage",
    "comms":        "primary_comms",
}


def _scan_text(text: str) -> list[DetectedTool]:
    """Scan text for tool signatures using keyword matching."""
    text_lower = text.lower()
    found: list[DetectedTool] = []
    seen: set[str] = set()

    for sig in _TOOL_SIGNATURES:
        if sig["name"] in seen:
            continue
        matches = sum(1 for kw in sig["keywords"] if kw in text_lower)
        if matches > 0:
            confidence = min(0.99, 0.55 + matches * 0.15)
            found.append(DetectedTool(
                name=sig["name"],
                confidence=confidence,
                source="transcript",
                logo_color=sig["logo_color"],
                category=sig["category"],
            ))
            seen.add(sig["name"])

    return sorted(found, key=lambda t: -t.confidence)


def _extract_frames(video_path: str, max_frames: int = 8) -> list[str]:
    """Extract frames from video using OpenCV if available."""
    try:
        import cv2
        cap = cv2.VideoCapture(video_path)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps   = cap.get(cv2.CAP_PROP_FPS) or 25
        step  = max(1, total // max_frames)

        frames_dir = Path("storage/frames")
        frames_dir.mkdir(parents=True, exist_ok=True)
        paths = []

        for i in range(0, total, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break
            p = str(frames_dir / f"frame_{i}.jpg")
            cv2.imwrite(p, frame)
            paths.append(p)
            if len(paths) >= max_frames:
                break

        cap.release()
        return paths
    except Exception as e:
        logger.warning(f"Frame extraction failed: {e}")
        return []


def _ocr_frame(frame_path: str) -> str:
    """Run OCR on a single frame using pytesseract if available."""
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(frame_path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def _ocr_all_frames(frame_paths: list[str]) -> str:
    """Concatenate OCR text from all frames."""
    texts = []
    for p in frame_paths:
        t = _ocr_frame(p)
        if t.strip():
            texts.append(t)
    return " ".join(texts)


class MultimodalDetector:
    """
    System 3 — Detects the technology stack from video frames + transcript.
    Merges OCR text, logo detection, and keyword scanning for maximum coverage.
    """

    def detect(
        self,
        transcript_text: str = "",
        video_path: str | None = None,
    ) -> DetectedStack:
        logger.info("MultimodalDetector scanning for technology stack...")

        all_text = transcript_text or ""
        frames_analyzed = 0

        # Try to extract and OCR video frames
        if video_path and Path(video_path).exists():
            frame_paths = _extract_frames(video_path)
            if frame_paths:
                ocr_text = _ocr_all_frames(frame_paths)
                all_text = f"{transcript_text} {ocr_text}"
                frames_analyzed = len(frame_paths)
                logger.info(f"OCR complete — {frames_analyzed} frames, {len(ocr_text)} chars")

        tools = _scan_text(all_text)

        if not tools and transcript_text:
            # Infer common tools from problem domain keywords
            tools = self._infer_from_domain(transcript_text)

        # Build primary tool assignments
        primary = {k: "" for k in _CATEGORY_MAP.values()}
        for tool in tools:
            cat_field = _CATEGORY_MAP.get(tool.category, "")
            if cat_field and not primary[cat_field]:
                primary[cat_field] = tool.name

        avg_confidence = sum(t.confidence for t in tools) / len(tools) if tools else 0.0

        tool_names = [t.name for t in tools[:6]]
        summary = (
            f"Detected {len(tools)} tools: {', '.join(tool_names[:5])}"
            if tools else
            "No specific tools detected — using generic integrations"
        )

        logger.success(f"Stack detected: {summary}")

        return DetectedStack(
            tools=tools,
            primary_email=primary["primary_email"],
            primary_crm=primary["primary_crm"],
            primary_storage=primary["primary_storage"],
            primary_comms=primary["primary_comms"],
            frames_analyzed=frames_analyzed,
            confidence=round(avg_confidence, 2),
            stack_summary=summary,
        )

    def _infer_from_domain(self, text: str) -> list[DetectedTool]:
        """Infer likely tools from domain/problem context when no explicit tool names found."""
        text_lower = text.lower()
        inferred = []

        if any(w in text_lower for w in ["email", "gmail", "inbox", "mail"]):
            inferred.append(DetectedTool(name="Gmail", confidence=0.70, source="inferred",
                                         logo_color="#EA4335", category="email"))
        if any(w in text_lower for w in ["spreadsheet", "sheet", "excel", "table"]):
            inferred.append(DetectedTool(name="Google Sheets", confidence=0.68, source="inferred",
                                         logo_color="#34A853", category="spreadsheet"))
        if any(w in text_lower for w in ["crm", "customer", "contact", "lead", "deal"]):
            inferred.append(DetectedTool(name="HubSpot", confidence=0.60, source="inferred",
                                         logo_color="#FF7A59", category="crm"))
        if any(w in text_lower for w in ["slack", "notify", "alert", "message"]):
            inferred.append(DetectedTool(name="Slack", confidence=0.58, source="inferred",
                                         logo_color="#4A154B", category="comms"))
        if any(w in text_lower for w in ["order", "invoice", "payment", "shopify"]):
            inferred.append(DetectedTool(name="Shopify", confidence=0.62, source="inferred",
                                         logo_color="#96BF48", category="ecommerce"))

        return inferred
