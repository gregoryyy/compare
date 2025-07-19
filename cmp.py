import os
import hashlib
import datetime
from collections import defaultdict

# Define status flags
EXISTS_IN_A = 1
SAME_POSITION = 2
DIFFERENT_POSITION = 4
DATE_DIFFERS = 8
SIZE_DIFFERS = 16
HASH_DIFFERS = 32
RELATIVE_PATH_DIFFERS = 64

def create_index(directory):
    """
    Create an index of file names in a directory with their hashes, sizes, dates, and relative paths.

    Args:
        directory (str): The directory path for which to create the index.

    Returns:
        dict: A dictionary where keys are file names and values are dictionaries
              containing hash, size, date, and relative path information for each file in the directory.
    """
    index = {}
    print(f"creating index for {directory}")
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, directory)
            with open(filepath, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
                index[filename] = {
                    'hash': file_hash,
                    'size': os.path.getsize(filepath),
                    'date': datetime.datetime.fromtimestamp(os.path.getmtime(filepath)),
                    'relpath': relpath
                }
    print(f"done with { len(index) } files.")
    return index

def compare_files(file_info_a, file_info_b):
    """
    Compare individual files in directories A and B for existence, position, date, size, hash, and relative path.

    Args:
        file_info_a (dict): File information dictionary from directory A.
        file_info_b (dict): File information dictionary from directory B.

    Returns:
        int: A numeric status variable indicating the comparison result using bitwise flags.
    """
    status = 0
    
    if file_info_a and file_info_b:
        status |= EXISTS_IN_A
        status |= SAME_POSITION if file_info_a['relpath'] == file_info_b['relpath'] else DIFFERENT_POSITION
        status |= DATE_DIFFERS if file_info_a['date'].replace(microsecond=0) != file_info_b['date'].replace(microsecond=0) else 0
        status |= SIZE_DIFFERS if file_info_a['size'] != file_info_b['size'] else 0
        status |= HASH_DIFFERS if file_info_a['hash'] != file_info_b['hash'] else 0
        status |= RELATIVE_PATH_DIFFERS if file_info_a['relpath'] != file_info_b['relpath'] else 0
    elif file_info_a:
        status |= EXISTS_IN_A

    if status & DIFFERENT_POSITION:
        print(f"file_info_a: {file_info_a['relpath']} <=> {file_info_b['relpath']}")
    if status & DATE_DIFFERS:
        print(f"file_info_a: {file_info_a['date']} <=> {file_info_b['date']}")
    if status & SIZE_DIFFERS:
        print(f"file_info_a: {file_info_a['size']} <=> {file_info_b['size']}")
    if status & HASH_DIFFERS:
        print(f"file_info_a: {file_info_a['hash']} <=> {file_info_b['hash']}")

    return status

def find_duplicates(index):
    """
    Find duplicate files in a file index based on their hash values.

    Args:
        index (dict): A dictionary containing file information with hash values.

    Returns:
        list: A list of lists where each inner list contains file names of duplicate files.
    """
    hash_to_files = defaultdict(list)

    for filename, file_info in index.items():
        file_hash = file_info['hash']
        hash_to_files[file_hash].append(filename)

    duplicates = [file_names for file_names in hash_to_files.values() if len(file_names) > 1]
    return duplicates

def print_file_status(filename, status, verbosity=1):
    """
    Print the status of a file comparison based on numeric status variable with varying verbosity.

    Args:
        filename (str): The name of the file being compared.
        status (int): A numeric status variable indicating the comparison result.
        verbosity (int, optional): Verbosity level (0, 1, or 2) to control the output.
    """
    if not (verbosity == 0 and status == 0):
        if verbosity == 2 or (verbosity == 1 and not (status & SAME_POSITION) and (status & HASH_DIFFERS or status & SIZE_DIFFERS)):
            print(f"File: {filename}")
            print(f"Exists in B: {'Yes, same position' if status & SAME_POSITION else 'Yes, different position'}")
            if status & HASH_DIFFERS:
                print("Hash: Yes", end=", ")
            else:
                print("Hash: No", end=", ")
            if status & SIZE_DIFFERS:
                print("Size: Yes", end=", ")
            else:
                print("Size: No", end=", ")
            if status & DATE_DIFFERS:
                print("Date: Yes", end=", ")
            else:
                print("Date: No", end=", ")
            if status & RELATIVE_PATH_DIFFERS:
                print("Relative Path: Yes")
            else:
                print("Relative Path: No")
        elif verbosity == 2 and status & SAME_POSITION:
            print(f"File: {filename}")
            print("Exists in B: Yes, same position")

def compare_directories(directory_a, directory_b, verbosity=1):
    """
    Compare two directory structures A and B for file existence and properties.

    Args:
        directory_a (str): The path to directory A.
        directory_b (str): The path to directory B.
        verbosity (int, optional): Verbosity level (0, 1, or 2) to control the output.
    """
    index_a = create_index(directory_a)
    index_b = create_index(directory_b)

    for filename, file_info_a in index_a.items():
        file_info_b = index_b.get(filename, None)
        
        status = compare_files(file_info_a, file_info_b)
        print_file_status(filename, status, verbosity)

if __name__ == "__main__":
    # directory_a = "/data/_local/cs-handover"
    # directory_b = "/Volumes/Backup/cs-handover"
    
    directory_a = "/data/_local/priv-backup"
    directory_b = "/Volumes/Backup/priv-backup"
    

    compare_directories(directory_a, directory_b)
