#!/usr/bin/env python3
# Verify the built kernel exports every symbol the stock vendor modules need,
# with identical CRCs. Usage: verify_build.py <Module.symvers> <expected.json>
import json, sys

symvers, expect_path = sys.argv[1], sys.argv[2]

def parse_symvers(path):
    out = {}
    for line in open(path, errors='replace'):
        parts = line.rstrip('\n').split('\t')
        if len(parts) >= 4:
            try:
                crc = int(parts[0], 16)
            except ValueError:
                continue
            out[parts[1]] = crc
    return out

expected = json.load(open(expect_path))
built = parse_symvers(symvers)
missing = [s for s in expected if s not in built]
common = [s for s in expected if s in built]
mismatch = [s for s in common if built[s] != expected[s]]
ok = len(common) - len(mismatch)

print(f'built exports                 : {len(built)}')
print(f'required by stock modules     : {len(expected)}')
print(f'  found                       : {len(common)}')
print(f'  CRC match                   : {ok}')
print(f'  CRC mismatch                : {len(mismatch)}')
print(f'  missing                     : {len(missing)}')
for s in mismatch[:60]:
    print(f'  MISMATCH {s}: built={built[s]:#x} stock={expected[s]:#x}')
for s in missing[:60]:
    print(f'  MISSING  {s}')

key = ['module_layout', 'kmalloc_caches', 'memcpy', 'memset', 'printk']
for s in key:
    print(f'KEY {s}: built={hex(built[s]) if s in built else None} stock={hex(expected[s]) if s in expected else None}')

sys.exit(0 if not missing and not mismatch else 1)
