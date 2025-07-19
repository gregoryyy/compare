# fundiff: diff and undiff files and directories

A Python-based toolkit for comparing, analyzing, and synchronizing directories using SHA-256 file hashes. Useful for backup verification, duplicate detection, and efficient rsync-like synchronization.

## 1. fhash.py — File Hash Scanner
Scans one or more directories and computes SHA-256 hashes for all files using parallel processing.

## 2. compare_dirs.py — Comparison Tool
Compares two directory trees or finds duplicates within a directory set.

## 3. fsync.py — Synchronization Tool
Synchronizes two directory trees (source → target) in various modes (copy, mirror) based on file content hashes.

# Appendix: Shell-based operation

A variant of this exists just using a shell (MacOS, possibly with homebrew).

## create hashes
find original1 original2 -type f -exec shasum -a 256 {} + | sort > originals.txt
find backup1 backup2 -type f -exec shasum -a 256 {} + | sort > backups.txt

## compare file lists (1 moved = 1 extra, 1 missing)
comm -23 originals.txt backups.txt > missing_in_backup.txt
comm -13 originals.txt backups.txt > extra_in_backup.txt

## same path but different hash
join -t $'\t' -j 2 <(sort -k2 originals.txt) <(sort -k2 backups.txt) | \
awk '$1 != $2 {print "MODIFIED: " $3 "\n  original: " $1 "\n  backup:   " $2}'

## duplicates
cut -d' ' -f1 originals.txt | sort | uniq -d > dupes.txt
grep -Ff dupes.txt originals.txt > duplicate_sets.txt

## grouped
cut -d' ' -f1 originals.txt | sort | uniq -d > dupes.txt && \
grep -Ff dupes.txt originals.txt | sort | \
awk '{if ($1 != last) {print $1; last = $1} print "  "$2}' > duplicate_groups.txt

