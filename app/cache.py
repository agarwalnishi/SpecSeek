import hashlib


def file_hash(path):
    """SHA-256 fingerprint of a file. Same bytes always give the same hash."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        # read in 8 KB blocks so big PDFs don't have to fit in memory at once
        for block in iter(lambda: f.read(8192), b""):
            h.update(block)
    return h.hexdigest()