"""
ShieldAI - Phishing Detection Engine
=====================================
Pure detection logic. No GUI, no file I/O, no networking dependencies
other than the standard library. This module can be reused unchanged
by main.py (GUI) or app.py's CLI mode.

Public interface
-----------------
analyze_url(url) -> {
    "url": str,
    "risk_score": int (0-100),
    "danger_level": "SAFE" | "SUSPICIOUS" | "DANGER",
    "reasons": [str, ...]
}
"""

import ssl
import socket
import ipaddress
from urllib.parse import urlparse


# ── Heuristic data ──────────────────────────────────────────────────────────

SUSPICIOUS_TLDS = {
    ".xyz", ".top", ".click", ".tk", ".ml", ".ga", ".cf", ".biz",
}

SHORT_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co",
}

SUSPICIOUS_WORDS = [
    "login", "verify", "update", "password", "bank", "signin", "secure",
]

# Score thresholds for classification
DANGER_THRESHOLD = 60
SUSPICIOUS_THRESHOLD = 25

# Network timeout for the optional SSL handshake check
SSL_CHECK_TIMEOUT = 3


def _check_tld(domain):
    for tld in SUSPICIOUS_TLDS:
        if domain.endswith(tld):
            return 25, "Suspicious domain extension"
    return 0, None


def _check_ip_literal(domain):
    try:
        ipaddress.ip_address(domain)
        return 40, "Website uses an IP address instead of a domain name"
    except ValueError:
        return 0, None


def _check_short_domain(domain):
    if domain in SHORT_DOMAINS:
        return 20, "URL shortening service detected"
    return 0, None


def _check_subdomains(domain):
    if len(domain.split(".")) > 4:
        return 20, "Unusually many subdomains"
    return 0, None


def _check_https(scheme):
    if scheme != "https":
        return 15, "No HTTPS encryption"
    return 0, None


def _check_keywords(full_url):
    lowered = full_url.lower()
    hits = sum(1 for word in SUSPICIOUS_WORDS if word in lowered)
    if hits:
        return hits * 10, "Suspicious security-related words found in URL"
    return 0, None


def _check_ssl_certificate(domain, scheme):
    """Attempt a real TLS handshake. Any failure is treated as a red flag."""
    if scheme != "https":
        return 0, None
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=SSL_CHECK_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=domain):
                pass
        return 0, None
    except Exception:
        return 10, "SSL certificate problem or unreachable host"


def _classify(score):
    if score >= DANGER_THRESHOLD:
        return "DANGER"
    if score >= SUSPICIOUS_THRESHOLD:
        return "SUSPICIOUS"
    return "SAFE"


def analyze_url(url):
    """
    Analyze a single URL for phishing indicators and return a risk report.

    Always returns a dict with the four required keys. On a malformed URL,
    risk_score is 0, danger_level is "SAFE", and reasons explains the problem
    (the caller should still treat an empty/garbage URL as invalid upstream).
    """
    if not isinstance(url, str) or not url.strip():
        return {
            "url": url,
            "risk_score": 0,
            "danger_level": "SAFE",
            "reasons": ["No URL provided"],
        }

    original_input = url.strip()
    candidate = original_input
    if not candidate.startswith(("http://", "https://")):
        candidate = "https://" + candidate

    parsed = urlparse(candidate)
    domain = parsed.hostname

    if not domain:
        return {
            "url": original_input,
            "risk_score": 0,
            "danger_level": "SAFE",
            "reasons": ["Could not parse a valid domain from this URL"],
        }

    domain = domain.lower()
    score = 0
    reasons = []

    checks = [
        _check_tld(domain),
        _check_ip_literal(domain),
        _check_short_domain(domain),
        _check_subdomains(domain),
        _check_https(parsed.scheme),
        _check_keywords(candidate),
        _check_ssl_certificate(domain, parsed.scheme),
    ]

    for points, reason in checks:
        if points:
            score += points
            reasons.append(reason)

    score = min(score, 100)

    return {
        "url": candidate,
        "risk_score": score,
        "danger_level": _classify(score),
        "reasons": reasons if reasons else ["No suspicious activity detected"],
    }
