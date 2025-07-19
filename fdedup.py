import os
import argparse
from fhash import scan_folder_parallel

def find_duplicates(directories, max_workers=8):
    '''Find duplicate files across multiple directories based on their hashes.'''
    _, hash_to_paths = scan_folder_parallel(directories, max_workers)
    return {h: sorted(paths) for h, paths in hash_to_paths.items() if len(paths) > 1}

def replace_with_hardlinks(duplicates, base_dir):
    '''Replace duplicate files with hard links to the first occurrence.'''
    for h, paths in duplicates.items():
        master = os.path.join(base_dir, paths[0])
        for dup_rel in paths[1:]:
            dup_path = os.path.join(base_dir, dup_rel)
            try:
                os.remove(dup_path)
                os.link(master, dup_path)
                print(f"[LINKED] {dup_rel} -> {paths[0]}")
            except Exception as e:
                print(f"[ERROR] Could not link {dup_rel}: {e}")

def print_duplicates(duplicates):
    '''Print the found duplicates in a readable format.'''
    for h, paths in duplicates.items():
        print(h)
        for p in paths:
            print(f"   {p}")

def main():
    '''Main function to parse arguments and find duplicates or create hard links.'''
    parser = argparse.ArgumentParser(description="Find and deduplicate files by hard linking")
    parser.add_argument("directories", nargs="+", help="Directories to scan for duplicates")
    parser.add_argument("--mode", choices=["find", "link"], default="find", help="Operation mode")
    parser.add_argument("--workers", type=int, default=8, help="Number of hashing threads")
    args = parser.parse_args()

    duplicates = find_duplicates(args.directories, max_workers=args.workers)

    if args.mode == "find":
        print_duplicates(duplicates)
    elif args.mode == "link":
        for base in args.directories:
            replace_with_hardlinks(duplicates, base)

if __name__ == "__main__":
    main()
