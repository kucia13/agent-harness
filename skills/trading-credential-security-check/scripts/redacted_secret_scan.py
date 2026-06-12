#!/usr/bin/env python3
"""Redacted credential scanner for trading repositories."""

from __future__ import annotations

import argparse
import hashlib
import math
import re
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}

TEXT_EXTENSIONS = {
    ".cfg",
    ".conf",
    ".env",
    ".example",
    ".ini",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}

SECRET_KEY_RE = re.compile(
    r"(?i)(api[_-]?key|api[_-]?secret|secret[_-]?key|private[_-]?key|"
    r"privatekey|token|cookie|access[_-]?token|refresh[_-]?token|passphrase|"
    r"password|mnemonic|seed|bearer|authorization|client[_-]?secret|"
    r"signing[_-]?key|wallet[_-]?key|keypair|jwt|credential)"
)

ASSIGN_RE = re.compile(
    r"""(?ix)
    \b([A-Z0-9_.-]*?
    (?:api[_-]?key|api[_-]?secret|secret[_-]?key|private[_-]?key|
    privatekey|token|cookie|access[_-]?token|refresh[_-]?token|passphrase|
    password|mnemonic|seed|bearer|authorization|client[_-]?secret|
    signing[_-]?key|wallet[_-]?key|keypair|jwt|credential)
    [A-Z0-9_.-]*?)\s*[:=]\s*(["']?)([^"'\n#]+)\2
    """
)

GETENV_DEFAULT_RE = re.compile(
    r"""(?ix)
    (?:os\.getenv|os\.environ\.get|getenv)\s*\(\s*(["'])
    ([^"']*(?:KEY|SECRET|TOKEN|PASSWORD|PASSPHRASE|PRIVATE|MNEMONIC|SEED|CREDENTIAL)[^"']*)
    \1\s*,\s*(["'])([^"']+)\3
    """
)

PEM_RE = re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")
HEX64_RE = re.compile(r"(?<![A-Fa-f0-9])(?:0x)?[A-Fa-f0-9]{64}(?![A-Fa-f0-9])")
PROVIDER_PATTERNS = [
    ("OpenAI-like key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
]


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", "ignore")).hexdigest()[:12]


def entropy(value: str) -> float:
    if not value:
        return 0.0
    probabilities = [value.count(char) / len(value) for char in set(value)]
    return -sum(probability * math.log2(probability) for probability in probabilities)


def is_env_file(path: Path) -> bool:
    name = path.name.lower()
    return name == ".env" or name.startswith(".env.") or name.endswith(".env")


def is_text_file(path: Path) -> bool:
    if is_env_file(path) or path.name == ".env.example":
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def is_safe_value(value: str) -> bool:
    raw = value.strip().strip("\"'")
    lowered = raw.lower()
    if raw == "":
        return True
    if raw.startswith("${") and raw.endswith("}"):
        return True
    if raw.startswith("$"):
        return True
    if raw.startswith("<") and raw.endswith(">"):
        return True
    if raw in {"0", "1", "-1", "true", "false", "yes", "no", "null", "none", "[]", "{}"}:
        return True
    safe_markers = (
        "your_",
        "your-",
        "example",
        "placeholder",
        "changeme",
        "change_me",
        "replace",
        "redacted",
        "dummy",
        "demo_",
        "test_",
        "public_data_only",
        "paste_",
        "xxx",
        "***",
        "todo",
    )
    if any(marker in lowered for marker in safe_markers):
        return True
    return False


def is_probably_code_value(value: str) -> bool:
    raw = value.strip().strip(",")
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.]*", raw):
        return True
    if re.search(r"\b(or|and|if|else)\b", raw):
        return True
    code_markers = (
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        " or ",
        " if ",
        "get(",
        "getenv",
        "os.environ",
        "self.",
        "config",
        "auth_conf",
    )
    if any(marker in raw for marker in code_markers):
        return True
    return False


def is_low_risk_index_key(key: str) -> bool:
    return re.search(r"(?i)(api[_-]?key[_-]?index|account[_-]?index)$", key) is not None


def redact_line(line: str) -> str:
    output = line.rstrip("\n")
    output = ASSIGN_RE.sub(
        lambda match: f"{match.group(1)}={match.group(2)}<REDACTED:{sha(match.group(3).strip())}>{match.group(2)}",
        output,
    )
    output = HEX64_RE.sub(lambda match: f"<HEX64:{sha(match.group(0))}>", output)
    for _, pattern in PROVIDER_PATTERNS:
        output = pattern.sub(lambda match: f"<TOKEN:{sha(match.group(0))}>", output)
    if len(output) > 220:
        output = output[:217] + "..."
    return output


def iter_files(root: Path):
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file() or not is_text_file(path):
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
        except OSError:
            continue
        yield path


def scan(root: Path) -> list[tuple[Path, int, str, str, str]]:
    findings: list[tuple[Path, int, str, str, str]] = []
    for path in iter_files(root):
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            continue

        env_file = is_env_file(path)
        for line_number, line in enumerate(text.splitlines(), 1):
            if PEM_RE.search(line):
                findings.append((path, line_number, "PRIVATE_KEY_PEM", "<pem>", redact_line(line)))

            if not env_file:
                for label, pattern in PROVIDER_PATTERNS:
                    if pattern.search(line):
                        findings.append((path, line_number, label, "<provider>", redact_line(line)))

            stripped_line = line.lstrip()
            allow_comment_assignment = stripped_line.startswith("#") and "=" in stripped_line

            for match in ASSIGN_RE.finditer(line):
                key = match.group(1).strip()
                value = match.group(3).strip()
                if env_file and path.name == ".env":
                    continue
                if "==" in line or "!=" in line:
                    continue
                if stripped_line.startswith("#") and not allow_comment_assignment:
                    continue
                if is_safe_value(value):
                    continue
                if is_low_risk_index_key(key):
                    continue
                if match.group(2) == "" and is_probably_code_value(value):
                    continue
                if len(value) < 16 and entropy(value) < 3.0:
                    continue
                findings.append((path, line_number, "HARDCODED_SECRET_VALUE", key, redact_line(line)))

            for match in GETENV_DEFAULT_RE.finditer(line):
                variable = match.group(2)
                default = match.group(4)
                if not is_safe_value(default):
                    findings.append((path, line_number, "UNSAFE_ENV_DEFAULT", variable, redact_line(line)))

            if SECRET_KEY_RE.search(line) and not env_file:
                for match in HEX64_RE.finditer(line):
                    value = match.group(0)
                    if not is_safe_value(value):
                        findings.append((path, line_number, "HEX64_NEAR_SECRET_KEYWORD", "<hex64>", redact_line(line)))

    seen: set[tuple[str, int, str, str, str]] = set()
    unique: list[tuple[Path, int, str, str, str]] = []
    for finding in findings:
        key = (str(finding[0]), finding[1], finding[2], finding[3], finding[4])
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan a trading repo for credential exposure without printing raw secrets.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root")
    parser.add_argument("--max-findings", type=int, default=300)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    findings = scan(root)
    print(f"SCANNED_ROOT={root}")
    print(f"FINDINGS={len(findings)}")
    for path, line_number, reason, key, preview in findings[: args.max_findings]:
        rel = path.relative_to(root) if path.is_relative_to(root) else path
        print(f"{rel}:{line_number} [{reason}] {key} :: {preview}")
    if len(findings) > args.max_findings:
        print(f"... truncated {len(findings) - args.max_findings} more")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
