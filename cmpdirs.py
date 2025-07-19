import os
import argparse
from fhash import scan_folder_parallel
from collections import defaultdict

def compare_directories(dir_a, dir_b, max_workers=8):
    '''Compare two directories and return a summary of additions, deletions, modifications, and relocations.'''
    path_to_hash_a, hash_to_paths_a = scan_folder_parallel([dir_a], max_workers)
    path_to_hash_b, hash_to_paths_b = scan_folder_parallel([dir_b], max_workers)

    rel_a = set(path_to_hash_a.keys())
    rel_b = set(path_to_hash_b.keys())

    additions = rel_b - rel_a
    deletions = rel_a - rel_b
    common = rel_a & rel_b

    modifications = []
    for rel in common:
        if path_to_hash_a[rel] != path_to_hash_b[rel]:
            modifications.append(rel)

    # Check for relocations (same hash, different path)
    hash_set_a = set(hash_to_paths_a.keys())
    hash_set_b = set(hash_to_paths_b.keys())

    relocations = []
    for h in hash_set_a & hash_set_b:
        paths_a = hash_to_paths_a[h]
        paths_b = hash_to_paths_b[h]
        if paths_a != paths_b:
            relocations.append((h, paths_a, paths_b))

    return {
        "additions": sorted(additions),
        "deletions": sorted(deletions),
        "modifications": sorted(modifications),
        "relocations": relocations,
    }

def find_duplicates(directories, max_workers=8):
    '''Find duplicate files across multiple directories based on their hashes.'''
    _, hash_to_paths = scan_folder_parallel(directories, max_workers)
    duplicates = {h: sorted(paths) for h, paths in hash_to_paths.items() if len(paths) > 1}
    return duplicates

def main():
    parser = argparse.ArgumentParser(description="Directory comparison and duplicate finder")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Compare command
    compare_parser = subparsers.add_parser("compare", help="Compare two directory trees")
    compare_parser.add_argument("dir_a", help="First directory")
    compare_parser.add_argument("dir_b", help="Second directory")
    compare_parser.add_argument("--workers", type=int, default=8, help="Number of threads")

    # Duplicates command
    dup_parser = subparsers.add_parser("duplicates", help="Find duplicate files in directories")
    dup_parser.add_argument("dirs", nargs="+", help="Directories to scan")
    dup_parser.add_argument("--workers", type=int, default=8, help="Number of threads")

    args = parser.parse_args()

    if args.command == "compare":
        result = compare_directories(args.dir_a, args.dir_b, max_workers=args.workers)
        print("=== Additions ===")
        for f in result["additions"]:
            print(f"+ {f}")
        print("\n=== Deletions ===")
        for f in result["deletions"]:
            print(f"- {f}")
        print("\n=== Modifications ===")
        for f in result["modifications"]:
            print(f"* {f}")
        print("\n=== Relocations ===")
        for h, from_paths, to_paths in result["relocations"]:
            print(f"~ Hash {h[:8]} moved:")
            print(f"  A: {sorted(from_paths)}")
            print(f"  B: {sorted(to_paths)}")

    elif args.command == "duplicates":
        dups = find_duplicates(args.dirs, max_workers=args.workers)
        print("=== Duplicates ===")
        for h, paths in dups.items():
            print(f"{h[:8]}: {', '.join(paths)}")

if __name__ == "__main__":
    main()
