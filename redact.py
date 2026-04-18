#!/usr/bin/env python3
"""
Content Redactor v2.4
Safe recursive content replacer with optional file/folder renaming.
Original files and folders are NEVER modified.
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


def apply_name_replacement(name: str, rules: list, use_regex: bool) -> str:
    """Apply replacement rules to a filename or folder name."""
    for search, replace in rules:
        if use_regex:
            name = re.sub(search, replace, name)
        else:
            name = name.replace(search, replace)
    return name


def get_output_path(file_path: Path, src_dir: Path, output_base: Path, suffix: str, 
                   flat: bool, rename: bool, rules: list, use_regex: bool):
    """Generate the final output path with optional renaming."""
    relative = file_path.relative_to(src_dir)
    
    if rename:
        # Rename each folder part + filename
        new_parts = []
        for part in relative.parent.parts:
            new_part = apply_name_replacement(part, rules, use_regex)
            new_parts.append(new_part)
        
        new_filename = apply_name_replacement(relative.stem, rules, use_regex)
        new_filename = f"{new_filename}{suffix}{relative.suffix}"
    else:
        new_parts = relative.parent.parts
        new_filename = f"{relative.stem}{suffix}{relative.suffix}"

    if output_base:
        if flat:
            # Flat mode: use underscore prefix from (renamed) folders
            prefix = "_".join(new_parts) + "_" if new_parts else ""
            final_name = f"{prefix}{new_filename}"
            return output_base / final_name
        else:
            # Preserve structure with renamed folders
            new_path = output_base
            for part in new_parts:
                new_path = new_path / part
            new_path.mkdir(parents=True, exist_ok=True)
            return new_path / new_filename
    else:
        # Default: next to original
        return file_path.parent / new_filename


def main():
    parser = argparse.ArgumentParser(
        description="Content Redactor v2.4 - Replace content + optionally rename files/folders",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("directory", help="Source directory to process")
    parser.add_argument("--extensions", required=True, 
                        help="Comma-separated extensions (e.g. .txt,.json,.env)")
    parser.add_argument("--replace", action="append", metavar="SEARCH=REPLACE",
                        help="Replacement rule")
    parser.add_argument("--rules-file", metavar="FILE",
                        help="Rules file")
    parser.add_argument("--suffix", default="-redacted", 
                        help="Suffix for new files (default: -redacted)")
    parser.add_argument("--output", metavar="DIR",
                        help="Output base directory")
    parser.add_argument("--flat", action="store_true",
                        help="Put all files in one flat directory")
    parser.add_argument("--rename", action="store_true",
                        help="Also apply replacement rules to folder names and filenames")
    parser.add_argument("--regex", action="store_true",
                        help="Enable regex mode")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview only")
    parser.add_argument("--encoding", default="utf-8")

    args = parser.parse_args()

    src_dir = Path(args.directory).resolve()
    if not src_dir.is_dir():
        print(f"❌ Error: Source directory '{src_dir}' does not exist.")
        sys.exit(1)

    if args.output:
        output_base = Path(args.output).resolve()
        output_base.mkdir(parents=True, exist_ok=True)
        print(f"📁 Output directory : {output_base}")
    else:
        output_base = None
        if args.rename:
            print("⚠️  Warning: --rename is most useful when combined with --output.")

    extensions = {ext.strip().lower() for ext in args.extensions.split(",") if ext.strip()}
    rules = load_replacement_rules(args.replace, args.rules_file)

    print(f"🚀 Starting redaction in: {src_dir}")
    print(f"   Extensions       : {', '.join(sorted(extensions))}")
    print(f"   Rules            : {len(rules)}")
    print(f"   Suffix           : {args.suffix}")
    print(f"   Rename mode      : {'Enabled' if args.rename else 'Disabled'}")
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

        # Replace content
        new_content = content
        for search, replace in rules:
            if args.regex:
                new_content = re.sub(search, replace, new_content)
            else:
                new_content = new_content.replace(search, replace)

        if new_content == content and not args.rename:
            skipped += 1
            continue

        # Get final output path (with optional rename)
        new_path = get_output_path(
            file_path, src_dir, output_base, args.suffix,
            args.flat, args.rename, rules, args.regex
        )

        if args.dry_run:
            print(f"[DRY-RUN] Would create → {new_path}")
        else:
            try:
                if new_path.parent != file_path.parent:  # only create dirs if needed
                    new_path.parent.mkdir(parents=True, exist_ok=True)
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
    print("Original files and folders remain untouched.")


if __name__ == "__main__":
    main()
