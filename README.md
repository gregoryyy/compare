# BuChk: Backup checker

Check differences between two sets of folders, e.g., original and backup

# 1 Python scripts

## operate

## create hashes

fhash

# 2 Shell-based operation



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

