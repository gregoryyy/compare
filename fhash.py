import os
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
from pathlib import Path

'''
File hash generator for a set of directories.
This script computes SHA-256 hashes for files in specified directories,
and allows for parallel processing to speed up the hashing process.
It returns a mapping of relative file paths to their hashes, and a mapping of hashes to sets of relative file paths.
It is useful for detecting duplicate files across multiple directories.
It can be used to compare files in backup directories against originals, or to find duplicates across multiple directories.
'''

def compute_hash(filepath, block_size=65536):
    '''Compute the SHA-256 hash of a file.'''
    try:
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            while chunk := f.read(block_size):
                sha256.update(chunk)
        return sha256.hexdigest(), filepath
    except Exception as e:
        return None, filepath

def scan_folder_parallel(base_dirs, max_workers=8):
    '''Scan multiple directories in parallel and compute file hashes.
    Args:
        base_dirs (list): List of base directories to scan.
        max_workers (int): Maximum number of threads to use for parallel processing.
    Returns:
        dict: A dictionary mapping relative file paths to their SHA-256 hashes.
        defaultdict: A dictionary mapping hashes to sets of relative file paths.'''
    file_paths = []
    for base in base_dirs:
        for root, dirs, files in os.walk(base):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base)
                file_paths.append((rel_path, full_path))

    path_to_hash = {}
    hash_to_paths = defaultdict(set)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_rel = {executor.submit(compute_hash, abs_path): rel_path for rel_path, abs_path in file_paths}
        for future in as_completed(future_to_rel):
            rel_path = future_to_rel[future]
            h, _ = future.result()
            if h:
                path_to_hash[rel_path] = h
                hash_to_paths[h].add(rel_path)

    return path_to_hash, hash_to_paths


if __file__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python buchk.py <directory1> <directory2> ...")
        sys.exit(1)

    directories = sys.argv[1:]
    hashes, hash_map = scan_folder_parallel(directories)
    
    for rel_path, file_hash in hashes.items():
        print(f"{rel_path}: {file_hash}")
    
    print("\nHash map:")
    for h, paths in hash_map.items():
        print(f"{h}: {', '.join(paths)}")
