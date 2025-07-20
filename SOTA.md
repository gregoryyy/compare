# fundiff baselines using shell commands

State of the art analysis for fundiff.

Variants of fundiff exist just using a shell commands (MacOS, possibly with homebrew), 
either as dedicated utilities or combination of low-level tools.

## Overview

| Tool             | Size | Date | Hash | Content | GUI | Sync |
|------------------|:----:|:----:|:----:|:-------:|:---:|:----:|
| `rsync`          | ✅   | ✅   | ✅   | ❌   | ❌  | ✅   |
| `diff -rq`       | ✅   | ✅   | ❌   | ✅       | ❌  | ❌   |
| `fdupes`         | ✅   | ❌   | ✅   | ✅       | ❌  | ❌   |
| `FreeFileSync`   | ✅   | ✅   | ✅   | ✅       | ✅  | ✅   |
| `Meld`           | ✅   | ✅   | ❌   | ✅       | ✅  | ❌   |
|------------------|:----:|:----:|:----:|:-------:|:---:|:----:|
| `fundiff`        | ❌   | ❌    | ✅   | ❌       | ❌  | ✅   |

# 1. Dedicated utilities

## `rsync`
Standard tool on Unix systems. My typical favorite.

```bash
rsync -rvnc --delete source/ target/      # Dry-run, verbose, checksum
rsync -av --checksum source/ target/      # Actual sync with hash (slow)
```

- Compares file size and mtime (modification time) by default.
- With --checksum, it compares hashes too (slow, but accurate).
- Great for syncing or dry-running comparisons.

## `diff`
Compare files; built-in, fast (by size/date).

```bash
diff -rq dirA/ dirB/
```

## `fdupes`
Duplicate finder (hash-based).

```bash
fdupes -r /path/to/dir
fdupes -rL /path/to/dir
```
- Uses MD5/SHA hash.
- Option `-L` to hardlink and delete redundant files. Keeps the first file in each duplicate group as the "master".

## `rmlint`
Duplicate finder with fast scanning. Fast, detailed output.
Install using homebrew.

```
rmlint /path/to/dir1 /path/to/dir2
```

- Find empty files, duplicate files, bad symlinks, etc.
- Useful for cleanup.

## `dircmp.py`
Python module for directory comparison.

```python
import filecmp
cmp = filecmp.dircmp("dir1", "dir2")
cmp.report()
```

# 2. GUI-based

## FreeFileSync
- Cross-platform (Windows/Linux/macOS)
- Compare by date, size, content
- isual UI + real-time sync + batch jobs

## Meld
- Open-source visual diff tool for files and directories
- Supports folder diffs, Git diffs, and merges

```bash
meld dirA dirB
```


# 3. Low-level tools

## create hashes
```bash
find original1 original2 -type f -exec shasum -a 256 {} + | sort > originals.txt
find backup1 backup2 -type f -exec shasum -a 256 {} + | sort > backups.txt
```

## compare file lists (1 moved = 1 extra, 1 missing)
```bash
comm -23 originals.txt backups.txt > missing_in_backup.txt
comm -13 originals.txt backups.txt > extra_in_backup.txt
```

## same path but different hash
```bash
join -t $'\t' -j 2 <(sort -k2 originals.txt) <(sort -k2 backups.txt) | \
awk '$1 != $2 {print "MODIFIED: " $3 "\n  original: " $1 "\n  backup:   " $2}'
```

## duplicates
```bash
cut -d' ' -f1 originals.txt | sort | uniq -d > dupes.txt
grep -Ff dupes.txt originals.txt > duplicate_sets.txt
```

## grouped
```bash
cut -d' ' -f1 originals.txt | sort | uniq -d > dupes.txt && \
grep -Ff dupes.txt originals.txt | sort | \
awk '{if ($1 != last) {print $1; last = $1} print "  "$2}' > duplicate_groups.txt
```
