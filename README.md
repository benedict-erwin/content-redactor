# Content Redactor

**Safe recursive content replacer for sensitive data**  
Replace domains, IP addresses, emails, usernames, tokens, and other sensitive information without touching the original files.

**Version:** 2.3

## Features

- Recursive processing of folders and subfolders
- Only processes specified file extensions
- **Never modifies** original files — always creates new files
- Multiple replacement rules (plain string or regex)
- Load rules from a file (`--rules-file`)
- `--output` option to save results to a separate directory
- `--flat` mode: flatten all output into one folder (with folder prefix to prevent name collisions)
- `--dry-run` mode for safe preview before actual processing
- Pure Python — no external dependencies

## Requirements

- Python 3.6 or higher
- No external packages required

## Quick Start

### 1. Recommended: Use Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows
```

### 2. Prepare Rules File

Copy the example and customize:

```bash
cp redact_rules.example.txt redact_rules.txt
```

Edit `redact_rules.txt` with your own replacement rules.

### 3. Run the Script

**Basic usage (files created next to originals):**

```bash
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt
```

**Recommended: Save to separate output folder (preserves structure):**

```bash
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output
```

**Flat mode (all files in one folder):**

```bash
python redact.py ./source-folder \
  --extensions .txt,.json,.env,.log,.yaml,.md \
  --rules-file redact_rules.txt \
  --output ./redacted-output \
  --flat
```

**Always test first with dry-run:**

```bash
python redact.py ./source-folder \
  --extensions .txt,.json,.env \
  --rules-file redact_rules.txt \
  --output ./redacted-output \
  --dry-run
```

## Command Line Options

| Argument           | Description                                                                 | Default          |
|--------------------|-----------------------------------------------------------------------------|------------------|
| `directory`        | Source directory to process (required)                                      | -                |
| `--extensions`     | Comma-separated file extensions to process                                  | required         |
| `--rules-file`     | File containing replacement rules (one per line)                            | -                |
| `--replace`        | Inline replacement rule (`SEARCH=REPLACE`) — can be used multiple times     | -                |
| `--suffix`         | Suffix added to new files                                                   | `-redacted`      |
| `--output`         | Base output directory (if not set, files created next to originals)         | None             |
| `--flat`           | Flatten all files into one folder (adds folder prefix to filename)          | False            |
| `--regex`          | Enable regex mode (`re.sub`)                                                | False            |
| `--dry-run`        | Preview only — do not create any files                                      | False            |
| `--encoding`       | File encoding                                                               | `utf-8`          |

## Output Behavior

- **Without `--output`**: New files are created next to the original files (same folder structure).
- **With `--output` (default)**: Preserves the original folder structure inside the output directory.
  - Example: `source-a/sub-b/file.txt` → `redacted-output/source-a/sub-b/file-redacted.txt`
- **With `--output` + `--flat`**: All files are placed in a single flat directory.
  - To avoid name collisions, folder names are added as prefix using `_`.
  - Example: `source-a/sub-b/file.txt` → `redacted-output/source-a_sub-b_file-redacted.txt`

## Example Rules File

See `redact_rules.example.txt` for a complete example covering:
- Domains
- IP addresses
- Emails
- Usernames
- URLs (with regex)
- Tokens & secrets

## Important Notes

- Files ending with the chosen suffix (e.g. `-redacted`) are automatically skipped.
- Only text files are processed. Binary files are ignored.
- Always run with `--dry-run` first when testing new rules.
- Original files are **never modified**.

## Repository Files

- `redact.py`                    — Main script
- `redact_rules.example.txt`     — Example replacement rules
- `.gitignore`                   — Recommended gitignore

## License

MIT License — Free to use, modify, and distribute.

---

**Made for safe redaction of sensitive information.**
