"""Rename every file with a given extension in a folder to <base>_1.ext, <base>_2.ext, ...

Usage:
    python scripts/bulk_file_renamer.py ./photos .jpg holiday --dry-run
    python scripts/bulk_file_renamer.py ./photos .jpg holiday
"""
import argparse
import os


def plan_renames(directory, extension, base_name):
    """Return a list of (old_name, new_name) pairs, sorted so the order is predictable."""
    files = sorted(f for f in os.listdir(directory)
                   if f.endswith(extension) and os.path.isfile(os.path.join(directory, f)))
    return [(name, f"{base_name}_{i}{extension}") for i, name in enumerate(files, start=1)]


def rename_files(directory, extension, base_name, dry_run=False):
    """Rename the files; with dry_run=True only print what would happen."""
    renames = plan_renames(directory, extension, base_name)
    targets = {new for _, new in renames}
    existing = set(os.listdir(directory)) - {old for old, _ in renames}
    clashes = targets & existing
    if clashes:
        raise FileExistsError(f"Would overwrite existing files: {sorted(clashes)}")

    for old, new in renames:
        print(f"{'[dry run] ' if dry_run else ''}{old} -> {new}")
    if dry_run:
        return renames

    # Two passes via temporary names, so a file whose current name is another file's
    # target (e.g. file_2.txt) is never overwritten mid-way.
    for i, (old, _) in enumerate(renames):
        os.rename(os.path.join(directory, old), os.path.join(directory, f".renaming_{i}.tmp"))
    for i, (_, new) in enumerate(renames):
        os.rename(os.path.join(directory, f".renaming_{i}.tmp"), os.path.join(directory, new))
    return renames


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory")
    parser.add_argument("extension", help="e.g. .txt")
    parser.add_argument("base_name", help="e.g. file")
    parser.add_argument("--dry-run", action="store_true", help="show the changes without renaming")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        parser.error(f"Not a directory: {args.directory}")
    renames = rename_files(args.directory, args.extension, args.base_name, args.dry_run)
    print(f"{len(renames)} file(s) {'would be ' if args.dry_run else ''}renamed.")


if __name__ == "__main__":
    main()
