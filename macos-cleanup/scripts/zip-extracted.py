"""zip-extracted.py ARCHIVE.zip... -- DIR...

Prints FULLY-EXTRACTED or MISSING <n> per archive: whether every file in the archive exists under
one of the DIRs with the same name, size and CRC32 (the checksum the zip stores per entry). Only a
FULLY-EXTRACTED archive is a redundant copy.
Matching ignores the path inside the archive because exports are often extracted into renamed
folders ("memories 2", "memories 3").
"""
import os
import sys
import zipfile
import zlib

if "--" not in sys.argv:
    sys.exit(__doc__)
split = sys.argv.index("--")
archives, dirs = sys.argv[1:split], sys.argv[split + 1:]

present = {}  # (name, size) -> paths
for root in dirs:
    for dirpath, _, files in os.walk(root):
        for name in files:
            path = os.path.join(dirpath, name)
            present.setdefault((name, os.path.getsize(path)), []).append(path)

crcs = {}


def crc(path):
    if path not in crcs:
        value = 0
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                value = zlib.crc32(chunk, value)
        crcs[path] = value
    return crcs[path]


def extracted(entry):
    candidates = present.get((os.path.basename(entry.filename), entry.file_size), [])
    return any(crc(path) == entry.CRC for path in candidates)


for archive in archives:
    try:
        entries = [e for e in zipfile.ZipFile(archive).infolist() if not e.is_dir()]
    except zipfile.BadZipFile:
        print(f"UNREADABLE\t{archive}")
        continue
    missing = [e.filename for e in entries if not extracted(e)]
    status = "FULLY-EXTRACTED" if not missing else f"MISSING {len(missing)}/{len(entries)}"
    print(f"{status}\t{archive}" + (f"\te.g. {missing[0]}" if missing else ""))
