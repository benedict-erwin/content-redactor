#!/usr/bin/env python3
"""
Content Redactor v2.1
Safe recursive content replacer for sensitive data (domains, IPs, emails, usernames, tokens, etc.)

Features:
- Processes folders recursively
- Only processes specified file extensions
- Creates new files with suffix (default: -redacted) — original files are NEVER modified
- Supports multiple replacement rules (string or regex)
- Supports loading rules from a file
- Dry-run mode for safe preview
- Skips already redacted files automatically
"""

import argparse
from pathlib import Path
import re
import sys


def load_replacement_rules(rules_args=None, rules_file=None):
    """Load replacement rules from command line arguments and/or rules file."""
    rules = []
    
    # Load from --replace arguments
    if rules_args:
        for rule in rules_args:
            if "=" not in rule:
                print(f"⚠️  Invalid format: {rule} (must be SEARCH=REPLACE)")
                continue
            search, replace = rule.split("=", 1)
            rules.append((search.strip(), replace.strip()))
    
    # Load from rules file
    if rules_file:
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        print(f"⚠️  Invalid rule format on line {line_num}: {line}")
                        continue
                    search, replace = line.split("=", 1)
                    rules.append((search.strip(), replace.strip()))
            print(f"✅ Successfully loaded {len(rules)} rules from {rules_file}")
        except Exception as e:
            print(f"❌ Failed to read rules file: {e}")
            sys.exit(1)
    
    if not rules:
        print("❌ No valid replacement rules provided.")
        sys.exit(1)
    
    return rules


def main():
    parser = argparse.ArgumentParser(
        description="Safe Content Redactor - Replace sensitive data recursively without modifying original files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "directory",
        help="Target directory to process (recursive)"
    )
    parser.add_argument(
        "--extensions",
        required=True,
        help="Comma-separated file extensions to process (e.g. .txt,.json,.env,.log,.yaml,.md)"
    )
    parser.add_argument(
        "--replace",
        action="append",
        metavar="SEARCH=REPLACE",
        help="Replacement rule (can be used multiple times)"
    )
    parser.add_argument(
        "--rules-file",
        metavar="FILE",
        help="File containing list of replacement rules (one rule per line)"
    )
    parser.add_argument(
        "--suffix",
        default="-redacted",
        help="Suffix for newly created files (default: -redacted)"
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Enable regex mode (uses re.sub instead of string replace)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes only, do not create any files"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)"
    )

    args = parser.parse_args()

    # Validate directory
    dir_path = Path(args.directory).resolve()
    if not dir_path.is_dir():
        print(f"❌ Error: '{dir_path}' is not a valid directory.")
        sys.exit(1)

    # Parse extensions
    extensions = {ext.strip().lower() for ext in args.extensions.split(",") if ext.strip()}

    # Load replacement rules
    replacement_rules = load_replacement_rules(args.replace, args.rules_file)

    print(f"🚀 Starting redaction in folder: {dir_path}")
    print(f"   Extensions       : {', '.join(sorted(extensions))}")
    print(f"   Number of rules  : {len(replacement_rules)}")
    print(f"   New file suffix  : {args.suffix}")
    print(f"   Mode             : {'Regex' if args.regex else 'String Replace'}")
    print(f"   Dry-run          : {'Yes' if args.dry_run else 'No'}\n")

    processed = 0
    created = 0
    skipped = 0

    # Process all files recursively
    for file_path in dir_path.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in extensions:
            continue
        if file_path.stem.endswith(args.suffix):
            skipped += 1
            continue  # Skip already redacted files

        try:
            content = file_path.read_text(encoding=args.encoding)
        except UnicodeDecodeError:
            print(f"⏭️  Skipped (not a text file): {file_path.name}")
            continue
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}")
            continue

        # Apply all replacement rules
        new_content = content
        for search, replace in replacement_rules:
            if args.regex:
                new_content = re.sub(search, replace, new_content)
            else:
                new_content = new_content.replace(search, replace)

        # Skip if no changes were made
        if new_content == content:
            skipped += 1
            continue

        # Create new file name
        new_filename = f"{file_path.stem}{args.suffix}{file_path.suffix}"
        new_path = file_path.parent / new_filename

        if args.dry_run:
            print(f"[DRY-RUN] Would create → {new_path.name}")
        else:
            try:
                new_path.write_text(new_content, encoding=args.encoding)
                print(f"✅ Created: {new_path.name}")
                created += 1
            except Exception as e:
                print(f"❌ Failed to write {new_path.name}: {e}")
                continue

        processed += 1

    # Final summary
    print("\n" + "=" * 70)
    print("✅ PROCESS COMPLETED!")
    print(f"   Files processed     : {processed}")
    print(f"   Files created       : {created}")
    print(f"   Files skipped       : {skipped}")
    print("=" * 70)
    print("Original files remain 100% untouched and safe.")
    if not args.dry_run and created > 0:
        print(f"You can now use the newly created *-redacted files.")


if __name__ == "__main__":
    main()
