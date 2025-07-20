# fundiff: diff and undiff files and directories

A Python-based toolkit for comparing, analyzing, and synchronizing directories using SHA-256 file hashes. Useful for backup verification, duplicate detection, and efficient rsync-like synchronization.

# Motivation

Utilities like `rdfind`, `fdupes`, `rsync`, `restic` or `hashdeep` are great for backing up files and checking integrity.

But there are a few flaws I ran into, like 

- scalability when large sets of files need to be synced or deduped, 
- missing functionality to compare across a set of directories (e.g., different versions of the same backup at different points in time), 
- dependencies of Unix utilities installed in specific versions on different machines.

With undiff, which stands for "remove differences", a flexible and extensible toolset for backups is available that is:

- adjusted to my needs,
- memory-based + multithreaded to speed up operations,
- extensible with the functionality in the Python ecosystem (for instance to run with DB backend to scale further, to analyze files using AI, etc.).


# Functionality

## Features

- Fast SHA-256 hashing with multithreading

- Detect file moves by content even if renamed or relocated

- Simple, extensible architecture

- Cross-platform (Python 3.8+)


## 1. `fhash.py` — File Hash Scanner
Scans one or more directories and computes SHA-256 hashes for all files using parallel processing.

```
python fhash.py <directory1> <directory2> ...
```

Output:

- List with lines: File path \t Hash
- List with lines: Hash \t File path

## 2. `cmpdirs.py` — Comparison Tool
Compares two directory trees or finds duplicates within a directory set.

```
python cmpdirs.py compare /path/to/dirA /path/to/dirB
```

Output:

- Additions: files in B but not in A
- Deletions: files in A but not in B
- Modifications: same path, different content (hash value)
- Relocations: same file (by hash), different path


## 3. `fsync.py` — Synchronization Tool
Synchronizes two directory trees (source → target) in various modes (copy, mirror) based on file content hashes.

```
python fsync.py /path/to/sourceA /path/to/targetB --mode copy
python fsync.py /path/to/sourceA /path/to/targetB --mode mirror
```

Effect: 

- `--mode copy`: Copy new and changed files from A → B
- `--mode mirror`: Mirror A → B (like rsync: copy + delete removed files in B)


## 4. `fdedup.py` — Deduplication Tool
Finds duplicates between files (hash-based) and allows deleting and hard-linking the duplicates.

```
python fdedup.py /path/to/source --mode find
python fdedup.py /path/to/source --mode link
```

Effect:

- `--mode find`: Find duplicate files
- `--mode link`: Replace all duplicate files beyond the first one (the master file) with hard links to the master

Output:

- List of duplicate files:
```
hash
   path1
   path2
hash
   path3
   path4
```

# Roadmap

- Duplicates finder and deduplication (see 4.) DONE.
- Integrate date, file size checks as optional
- Option `dry-run`
- Logging with `quiet` to `verbose` options
- Support move/rename optimization (relocate mode)

# Installation

Currently simply use standard Python. Assumption for above synopses: Python 3.11+ in path, as `python`.

