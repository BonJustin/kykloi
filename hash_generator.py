import hashlib
from pathlib import Path

ARCHIVE_DIR = Path("system/tools/archives")

for file_path in sorted(ARCHIVE_DIR.iterdir()):
    if file_path.is_file():
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        print(f'"{file_path.name}": "{hasher.hexdigest()}"')
