"""Flask AI Agent — conversational + classification backend.

Stdlib-friendly, feature-flagged. Without a key it uses safe rule-based
fallbacks so the service is demoable and testable with zero network calls.
"""
from __future__ import annotations

import os
from flask import Flask, request, jsonify

from ai_client import chat, complete, ai_enabled

app = Flask(__name__)


def _rule_fallback(text: str) -> str:
    t = (text or "").lower()
    if any(k in t for k in ("hour", "open", "time")):
        return "Our hours are Mon-Fri 9am-6pm. How else can I help?"
    if any(k in t for k in ("price", "cost", "pricing")):
        return "Pricing depends on scope. Could you tell me what you need built?"
    if any(k in t for k in ("refund", "cancel")):
        return "I'll connect you with support for refunds/cancellations. What's your order ID?"
    return "Thanks for reaching out! A teammate will follow up shortly. How can we help today?"


@app.get("/health")
def health():
    return jsonify({"status": "ok", "ai_enabled": ai_enabled()})


@app.post("/chat")
def chat_endpoint():
    data = request.get_json(force=True, silent=True) or {}
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "missing 'message'"}), 400
    if not ai_enabled():
        return jsonify({"reply": _rule_fallback(message)})
    res = complete(message, system="You are a helpful customer assistant.")
    if res.ok:
        return jsonify({"reply": res.text})
    return jsonify({"reply": _rule_fallback(message), "ai_error": res.error})


@app.post("/chat/multi")
def chat_multi():
    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "missing 'messages'"}), 400
    if not ai_enabled():
        last = messages[-1].get("content", "") if messages else ""
        return jsonify({"reply": _rule_fallback(last)})
    res = chat(messages)
    if res.ok:
        return jsonify({"reply": res.text})
    return jsonify({"reply": _rule_fallback(""), "ai_error": res.error})


@app.post("/classify")
def classify():
    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")
    labels = data.get("labels", ["general"])
    if not text:
        return jsonify({"error": "missing 'text'"}), 400
    if not ai_enabled():
        # Deterministic heuristic fallback
        lowered = text.lower()
        for lbl in labels:
            if lbl.lower() in lowered:
                return jsonify({"label": lbl, "reason": "keyword match (offline)"})
        return jsonify({"label": labels[0], "reason": "default (offline)"})
    sys = "Classify the user text into exactly one of these labels: " + ", ".join(labels) + \
          ". Reply with JSON: {\"label\": <one label>, \"reason\": <short>}"
    res = complete(sys, system="You are a strict classifier.", temperature=0.0)
    if res.ok:
        try:
            import json
            parsed = json.loads(res.text)
            return jsonify({"label": parsed.get("label", labels[0]), "reason": parsed.get("reason", "")})
        except Exception:
            return jsonify({"label": labels[0], "reason": "parse-failed", "raw": res.text})
    return jsonify({"label": labels[0], "reason": "ai-error", "ai_error": res.error})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
