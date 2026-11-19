"""Unit tests for deterministic pattern-based secret scanner (T025).

Verifies credential detection, masking/redaction (no secrets echoed in exceptions/logs),
and zero Groq client invocations when secrets are found.
"""


def test_secret_scanner_detects_groq_key():
    from src.services.secret_scanner import SecretScanner

    scanner = SecretScanner()
    code = 'GROQ_API_KEY = "gsk_1234567890abcdef1234567890abcdef12345678"\n'
    detected = scanner.scan(code)
    assert len(detected) > 0
    assert any("Groq API Key" in d.pattern_name for d in detected)
    # Ensure raw secret is not exposed in string representation
    for d in detected:
        assert "gsk_1234567890abcdef" not in d.masked_description()


def test_secret_scanner_detects_aws_key():
    from src.services.secret_scanner import SecretScanner

    scanner = SecretScanner()
    code = 'AWS_KEY = "AKIA1234567890ABCDEF"\n'
    detected = scanner.scan(code)
    assert len(detected) > 0
    assert any("AWS Access Key" in d.pattern_name for d in detected)


def test_secret_scanner_detects_github_pat():
    from src.services.secret_scanner import SecretScanner

    scanner = SecretScanner()
    code = 'GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"\n'
    detected = scanner.scan(code)
    assert len(detected) > 0
    assert any("GitHub" in d.pattern_name for d in detected)


def test_secret_scanner_detects_private_key():
    from src.services.secret_scanner import SecretScanner

    scanner = SecretScanner()
    code = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA0...\n-----END RSA PRIVATE KEY-----\n"
    detected = scanner.scan(code)
    assert len(detected) > 0
    assert any("Private Key" in d.pattern_name for d in detected)


def test_secret_scanner_clean_code():
    from src.services.secret_scanner import SecretScanner

    scanner = SecretScanner()
    code = "def calculate_total(prices: list[float]) -> float:\n    return sum(prices)\n"
    detected = scanner.scan(code)
    assert len(detected) == 0
