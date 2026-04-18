# Content Redactor

**A safe, recursive content replacer for sensitive data (domains, IPs, emails, usernames, tokens, etc.)**

This Python script scans a folder recursively, replaces sensitive strings (or regex patterns) in text files, and **creates new files** with a suffix (default: `-redacted`).  
The original files are **never modified** — keeping your source data 100% safe.

Perfect for redacting production domains, real IPs, emails, API keys, or credentials before sharing logs, configs, or code.

## Features

- Recursive processing (all subfolders)
- Specify any number of file extensions
- Multiple replacement rules (plain string or regex)
- Load rules from a file (recommended for many rules)
- Creates new files with suffix → original files untouched
- `--dry-run` mode for safe preview
- Skips already redacted files automatically
- Pure Python Standard Library (no external dependencies)
- Works great with `.env`, `.json`, `.yaml`, `.log`, `.txt`, `.md`, `.conf`, etc.

## Requirements

- Python 3.6 or higher
- No external packages required (zero dependencies)

## Quick Start

### 1. Clone or Download

```bash
git clone https://github.com/benedict-erwin/content-redactor.git
cd content-redactor
```

### 2. (Recommended) Use a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# No pip install needed!
```

### 3. Create a Rules File

Create `redact_rules.txt` (example):

```txt
# Redaction rules - one per line (old=new)
production.example.com=internal.example.local
staging.example.com=internal.staging.local
192.168.10.45=10.0.0.45
admin@realcompany.com=admin@internal.local
admin-prod=admin-dev
https?://api\.live\.com=https://api.internal.local
super-secret-token=REDACTED-TOKEN
```

### 4. Run the Script

**Dry-run first (highly recommended):**

```bash
python redact.py ./target_folder \
  --extensions .txt,.json,.yaml,.env,.log,.md,.conf \
  --rules-file redact_rules.txt \
  --dry-run
```

**Real run:**

```bash
python redact.py ./target_folder \
  --extensions .txt,.json,.yaml,.env,.log,.md,.conf \
  --rules-file redact_rules.txt
```

### Alternative: Inline Rules (for quick use)

```bash
python redact.py ./myproject \
  --extensions .env,.json \
  --replace "production.example.com=internal.example.local" \
  --replace "192.168.100.50=10.0.0.50" \
  --suffix -redacted
```

## Command Line Options

| Argument           | Description                                              | Default          |
|--------------------|----------------------------------------------------------|------------------|
| `directory`        | Target folder (required)                                 | -                |
| `--extensions`     | Comma-separated file extensions                          | required         |
| `--rules-file`     | File containing replacement rules (one per line)         | -                |
| `--replace`        | Inline replacement rule (`SEARCH=REPLACE`) — repeatable  | -                |
| `--suffix`         | Suffix for new files                                     | `-redacted`      |
| `--regex`          | Enable regex mode (`re.sub`)                             | False            |
| `--dry-run`        | Preview only, do not create files                        | False            |
| `--encoding`       | File encoding                                            | `utf-8`          |

## Example Output

```
🚀 Starting redaction in folder: /home/user/project
   Extensions       : .json, .env, .log
   Number of rules  : 6
   New file suffix  : -redacted
   Mode             : String Replace
   Dry-run          : No

✅ Created: config-redacted.json
✅ Created: .env-redacted
...

==================================================
✅ PROCESS COMPLETED!
   Files processed     : 15
   Files created       : 11
   Files skipped       : 4
==================================================
Original files remain 100% untouched.
```

## Important Notes

- Files ending with the chosen suffix (e.g., `-redacted`) are automatically skipped to prevent re-processing.
- Only text files are processed. Binary files (images, PDFs, etc.) are skipped.
- Replacements are applied in the order listed in the rules file.
- Always run with `--dry-run` first when testing new rules.

## Repository Files

- `redact.py`          — Main script
- `redact_rules.example.txt` — Example rules file
- `.gitignore`         — Ignores venv and redacted files

## License

MIT License — Free to use, modify, and distribute.

---

Made for safe redaction of sensitive information.
