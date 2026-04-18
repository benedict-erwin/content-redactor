#!/usr/bin/env python3
"""
Content Redactor v2.3
Safe recursive content replacer with support for custom output directory and flat mode.
Original files are NEVER modified.
"""

import argparse
from pathlib import Path
import re
import sys


def load_replacement_rules(rules_args=None, rules_file=None):
    """Load replacement rules from arguments and/or rules file."""
    rules = []
    
    if rules_args:
        for rule in rules_args:
            if "=" not in rule:
                print(f"⚠️  Invalid format: {rule} (must be SEARCH=REPLACE)")
                continue
            search, replace = rule.split("=", 1)
            rules.append((search.strip(), replace.strip()))
    
    if rules_file:
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" not in line:
                        print(f"⚠️  Invalid rule on line {line_num}: {line}")
                        continue
                    search, replace = line.split("=", 1)
                    rules.append((search.strip(), replace.strip()))
            print(f"✅ Loaded {len(rules)} rules from {rules_file}")
        except Exception as e:
            print(f"❌ Failed to read rules file: {e}")
            sys.exit(1)
    
    if not rules:
        print("❌ No valid replacement rules provided.")
        sys.exit(1)
    
    return rules


def get_flat_filename(file_path: Path, src_dir: Path, suffix: str) -> str:
    """Generate flat filename with folder structure as prefix to avoid name collision."""
    relative = file_path.relative_to(src_dir)
    parts = list(relative.parent.parts)
    if parts:
        prefix = "_".join(parts) + "_"
    else:
        prefix = ""
    
    return f"{prefix}{relative.stem}{suffix}{relative.suffix}"


def main():
    parser = argparse.ArgumentParser(
        description="Safe Content Redactor v2.3 - Replace sensitive data recursively",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "directory",
        help="Source directory to process (recursive)"
    )
    parser.add_argument(
        "--extensions",
        required=True,
        help="Comma-separated file extensions (e.g. .txt,.json,.env,.log,.yaml,.md)"
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
        help="File containing replacement rules (one per line)"
    )
    parser.add_argument(
        "--suffix",
        default="-redacted",
        help="Suffix for new files (default: -redacted)"
    )
    parser.add_argument(
        "--output",
        metavar="OUTPUT_DIR",
        help="Base output directory. Preserves folder structure by default."
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Put all files in one flat directory (adds folder prefix to filename to avoid collision)"
    )
    parser.add_argument(
        "--regex",
        action="store_true",
        help="Enable regex mode (re.sub)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview only, do not create files"
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding (default: utf-8)"
    )

    args = parser.parse_args()

    src_dir = Path(args.directory).resolve()
    if not src_dir.is_dir():
        print(f"❌ Error: Source directory '{src_dir}' does not exist.")
        sys.exit(1)

    # Setup output directory
    if args.output:
        output_base = Path(args.output).resolve()
        output_base.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory : {output_base}")
    else:
        output_base = None

    if args.flat and not output_base:
        print("⚠️  Warning: --flat is only meaningful when used with --output. Ignoring --flat.")

    extensions = {ext.strip().lower() for ext in args.extensions.split(",") if ext.strip()}
    replacement_rules = load_replacement_rules(args.replace, args.rules_file)

    print(f"🚀 Starting redaction in folder: {src_dir}")
    print(f"   Extensions       : {', '.join(sorted(extensions))}")
    print(f"   Number of rules  : {len(replacement_rules)}")
    print(f"   New file suffix  : {args.suffix}")
    print(f"   Output mode      : {'Flat' if args.flat and output_base else 'Preserve structure'}")
    print(f"   Dry-run          : {'Yes' if args.dry_run else 'No'}\n")

    processed = 0
    created = 0
    skipped = 0

    for file_path in src_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in extensions:
            continue
        if file_path.stem.endswith(args.suffix):
            skipped += 1
            continue

        try:
            content = file_path.read_text(encoding=args.encoding)
        except UnicodeDecodeError:
            print(f"⏭️  Skipped (not text): {file_path.name}")
            continue
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            continue

        new_content = content
        for search, replace in replacement_rules:
            if args.regex:
                new_content = re.sub(search, replace, new_content)
            else:
                new_content = new_content.replace(search, replace)

        if new_content == content:
            skipped += 1
            continue

        # Determine output path
        if output_base:
            if args.flat:
                new_filename = get_flat_filename(file_path, src_dir, args.suffix)
                new_path = output_base / new_filename
            else:
                # Preserve folder structure
                relative = file_path.relative_to(src_dir)
                new_filename = f"{relative.stem}{args.suffix}{relative.suffix}"
                new_path = output_base / relative.parent / new_filename
                new_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Default: next to original file
            new_filename = f"{file_path.stem}{args.suffix}{file_path.suffix}"
            new_path = file_path.parent / new_filename

        if args.dry_run:
            print(f"[DRY-RUN] Would create → {new_path}")
        else:
            try:
                new_path.write_text(new_content, encoding=args.encoding)
                print(f"✅ Created: {new_path}")
                created += 1
            except Exception as e:
                print(f"❌ Failed to write {new_path}: {e}")
                continue

        processed += 1

    print("\n" + "=" * 70)
    print("✅ PROCESS COMPLETED!")
    print(f"   Files processed     : {processed}")
    print(f"   Files created       : {created}")
    print(f"   Files skipped       : {skipped}")
    print("=" * 70)
    print("Original files remain 100% untouched and safe.")


if __name__ == "__main__":
    main()
