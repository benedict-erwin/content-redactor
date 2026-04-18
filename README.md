# Content Redactor

**Safe recursive content replacer with optional file & folder renaming**

Replace sensitive data inside files **and optionally rename files and folders** according to your rules — without modifying the originals.

**Version:** 2.4

## Features

- Recursive processing (all subfolders)
- Replace content inside files
- **New:** `--rename` option to also replace names of files and folders
- Save results to a separate output directory (`--output`)
- Flat mode (`--flat`) to put all files in one folder
- Dry-run mode for safe preview
- Supports both plain string and regex replacement
- Original files and folders are **never modified**

## Requirements

- Python 3.6 or higher
- No external dependencies

## Quick Start

### 1. Setup (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 2. Prepare Rules

```bash
cp redact_rules.example.txt redact_rules.txt
# Edit redact_rules.txt with your replacement rules
```

### 3. Recommended Commands

**Test with dry-run first:**

```bash
# Test content replacement only
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output \
  --dry-run

# Test with file & folder renaming
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output \
  --rename \
  --dry-run
```

**Run for real:**

```bash
# Only replace content (structure preserved)
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output

# Replace content + rename files and folders
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output \
  --rename
```

**Flat mode + Rename:**

```bash
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output \
  --flat \
  --rename
```

## Command Line Options

| Argument           | Description                                                                 | Default          |
|--------------------|-----------------------------------------------------------------------------|------------------|
| `directory`        | Source directory to process                                                 | required         |
| `--extensions`     | Comma-separated file extensions                                             | required         |
| `--rules-file`     | File containing replacement rules                                           | -                |
| `--replace`        | Inline replacement rule (`SEARCH=REPLACE`)                                  | -                |
| `--suffix`         | Suffix for new files                                                        | `-redacted`      |
| `--output`         | Output base directory (strongly recommended)                                | None             |
| `--flat`           | Put all files in one flat directory                                         | False            |
| `--rename`         | **Also apply rules to file names and folder names**                         | False            |
| `--regex`          | Enable regex mode (`re.sub`)                                                | False            |
| `--dry-run`        | Preview only, do not create files                                           | False            |
| `--encoding`       | File encoding                                                               | `utf-8`          |

## Important Notes about `--rename`

- `--rename` will apply your replacement rules to:
  - Every folder name in the path
  - The filename (without extension)
- `--rename` works best when combined with `--output`. Using it without `--output` is **not recommended** because it cannot safely rename original folders.
- When using `--rename` + `--flat`, the folder prefix will be based on the **renamed** folder names.

### Example with `--rename`

**Original structure:**
```
source-folder/
├── production-app/
│   └── config-prod.json
└── staging-data/
    └── api-staging.log
```

**Rules:**
```
production=internal
staging=internal
-prod=-dev
```

**After running with `--rename` and `--output`:**
```
redacted-output/
├── internal-app/
│   └── config-dev.json
└── internal-data/
    └── api-internal.log
```

## Output Modes Summary

| Mode                        | Flags                                      | Description |
|----------------------------|--------------------------------------------|-----------|
| Next to original           | (no `--output`)                            | Creates files beside originals |
| Preserve structure         | `--output DIR`                             | Keeps folder structure |
| Flat                       | `--output DIR --flat`                      | All files in one folder |
| Rename + Preserve          | `--output DIR --rename`                    | Renames folders & files |
| Rename + Flat              | `--output DIR --flat --rename`             | Flat + renamed names |

## Best Practices

- Always run with `--dry-run` first
- Use `--output` when using `--rename`
- Test rules thoroughly before running without dry-run
- Do not put real sensitive data in `redact_rules.example.txt`

## Repository Files

- `redact.py`                    — Main script
- `redact_rules.example.txt`     — Example replacement rules
- `.gitignore`                   — Recommended

## License

MIT License

---

**Safe redaction tool for domains, IPs, emails, credentials, and folder structures.**

---
