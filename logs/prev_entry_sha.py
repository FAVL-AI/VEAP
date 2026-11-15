"""Print sha256 of the LAST steplog entry: bytes from the start of the last line beginning '### ' to EOF."""
import hashlib, sys
b = open(sys.argv[1], 'rb').read()
i = b.rfind(b"\n### ")
entry = b[i + 1:] if i >= 0 else b
print(hashlib.sha256(entry).hexdigest())
