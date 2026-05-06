import hashlib

def string_hexdigest(text: str, *, algo="sha256", encoding="utf-8"):
    h = hashlib.new(algo)
    h.update(text.encode(encoding))
    return h.hexdigest()

def bytes_hexdigest(data: bytes, *, algo="sha256"):
    h = hashlib.new(algo)
    h.update(data)
    return h.hexdigest()

def file_hexdigest(path, *, algo="sha256", chunk_size=8192):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()
