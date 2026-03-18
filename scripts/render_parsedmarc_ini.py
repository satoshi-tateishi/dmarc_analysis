import os
import re
import sys
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")
REQUIRED_VARS = [
    "IMAP_HOST",
    "IMAP_PORT",
    "IMAP_USE_SSL",
    "IMAP_USERNAME",
    "IMAP_PASSWORD",
    "IMAP_REPORTS_FOLDER",
    "IMAP_ARCHIVE_FOLDER",
]


def normalize_bool(value: str) -> str:
    lowered = value.strip().lower()
    if lowered in {"1", "true", "yes", "on"}:
        return "True"
    if lowered in {"0", "false", "no", "off"}:
        return "False"
    raise ValueError("IMAP_USE_SSL must be a boolean-like value")


def resolve_var(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    if name == "IMAP_USE_SSL":
        return normalize_bool(value)
    return value


def render_template(template_text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return resolve_var(match.group(1))

    return PLACEHOLDER_RE.sub(replace, template_text)


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_parsedmarc_ini.py TEMPLATE OUTPUT", file=sys.stderr)
        return 1

    missing = [name for name in REQUIRED_VARS if not os.getenv(name, "").strip()]
    if missing:
        print(f"missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        return 1

    template_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    rendered = render_template(template_path.read_text())
    output_path.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
