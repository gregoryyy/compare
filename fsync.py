import os
import shutil
import argparse
from pathlib import Path
from cmpdirs import compare_directories
from fhash import scan_folder_parallel

def ensure_dir_exists(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def sync_copy(additions, modifications, source_dir, target_dir):
    '''Copy new and modified files from source to target directory.'''
    for rel_path in sorted(additions | set(modifications)):
        src = os.path.join(source_dir, rel_path)
        dst = os.path.join(target_dir, rel_path)
        ensure_dir_exists(dst)
        print(f"[COPY] {rel_path}")
        shutil.copy2(src, dst)

def sync_delete(deletions, target_dir):
    '''Delete files in target directory that are not present in source directory.'''
    for rel_path in sorted(deletions):
        target_path = os.path.join(target_dir, rel_path)
        if os.path.exists(target_path):
            print(f"[DELETE] {rel_path}")
            os.remove(target_path)

def sync_directories(dir_a, dir_b, mode="copy", max_workers=8):
    '''Synchronize two directories by copying new and modified files, and deleting files that no longer exist in the source directory.'''
    result = compare_directories(dir_a, dir_b, max_workers=max_workers)

    additions = set(result["additions"])
    deletions = set(result["deletions"])
    modifications = set(result["modifications"])

    if mode == "copy":
        sync_copy(additions, modifications, dir_a, dir_b)
    elif mode == "mirror":
        sync_copy(additions, modifications, dir_a, dir_b)
        sync_delete(deletions, dir_b)
    else:
        raise ValueError(f"Unsupported sync mode: {mode}")

def main():
    '''Main function to parse arguments and initiate directory synchronization.'''
    parser = argparse.ArgumentParser(description="Directory synchronization tool (like rsync)")
    parser.add_argument("source", help="Source directory (A)")
    parser.add_argument("target", help="Target directory (B)")
    parser.add_argument("--mode", choices=["copy", "mirror"], default="copy", help="Sync mode")
    parser.add_argument("--workers", type=int, default=8, help="Number of threads")
    args = parser.parse_args()

    sync_directories(args.source, args.target, mode=args.mode, max_workers=args.workers)

if __name__ == "__main__":
    main()
