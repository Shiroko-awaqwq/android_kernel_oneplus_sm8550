#!/usr/bin/env python3
# Resolve the 3 SUSFS rejects that occur on the OPLUS 5.15.167 tree (include/extern blocks).
# Usage: fix_susfs_rejects.py <kernel_root>
import sys, os

W = sys.argv[1] if len(sys.argv) > 1 else '.'

def insert_after(path, anchor, text):
    full = os.path.join(W, path)
    with open(full, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    joined = ''.join(lines)
    if text in joined:
        print(f'skip (already present): {path}')
        return True
    positions = [i for i, l in enumerate(lines) if l.rstrip('\n') == anchor]
    if not positions:
        print(f'ERROR: anchor not found in {path}: {anchor!r}')
        return False
    i = positions[0]
    lines.insert(i + 1, text)
    with open(full, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f'patched {path} after line {i+1}')
    return True

INC_NS = '''#ifdef CONFIG_KSU_SUSFS
#include <linux/susfs_def.h>
#endif // #ifdef CONFIG_KSU_SUSFS
'''
EXT_NS = '''
#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT
extern bool susfs_is_current_ksu_domain(void);
extern struct static_key_true susfs_is_sdcard_android_data_not_decrypted;

#define CL_COPY_MNT_NS BIT(25) /* used by copy_mnt_ns() */
#endif // #ifdef CONFIG_KSU_SUSFS_SUS_MOUNT
'''
INC_TM = '''#if defined(CONFIG_KSU_SUSFS_SUS_KSTAT) || defined(CONFIG_KSU_SUSFS_SUS_MAP) || defined(CONFIG_KSU_SUSFS_OPEN_REDIRECT)
#include <linux/susfs_def.h>
#endif // #if defined(CONFIG_KSU_SUSFS_SUS_KSTAT) || defined(CONFIG_KSU_SUSFS_SUS_MAP) || defined(CONFIG_KSU_SUSFS_OPEN_REDIRECT)
'''
INC_MM = '''#ifdef CONFIG_KSU_SUSFS_SUS_MAP
#include <linux/susfs_def.h>
#endif // #ifdef CONFIG_KSU_SUSFS_SUS_MAP
'''

ok = True
ok &= insert_after('fs/namespace.c', '#include <linux/mnt_idmapping.h>', INC_NS)
ok &= insert_after('fs/namespace.c', '#include "internal.h"', EXT_NS)
ok &= insert_after('fs/proc/task_mmu.c', '#include <linux/pkeys.h>', INC_TM)
ok &= insert_after('mm/memory.c', '#include <linux/vmalloc.h>', INC_MM)

# Drop patch backups, but NEVER hide a reject we did not explicitly resolve.
# The workflow fails on any remaining .rej, so unknown rejects must stay visible.
known_rejects = {'fs/namespace.c.rej', 'fs/proc/task_mmu.c.rej', 'mm/memory.c.rej'}
removed = 0
unresolved = []
for root, _, files in os.walk(W):
    if '/.git' in root:
        continue
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, W).replace('\\', '/')
        if f.endswith('.orig'):
            os.remove(full)
            removed += 1
        elif f.endswith('.rej'):
            if ok and rel in known_rejects:
                os.remove(full)
                removed += 1
            else:
                unresolved.append(rel)
print(f'removed {removed} .orig/known-reject files')
if unresolved:
    print('UNRESOLVED rejects kept for the workflow to fail on: ' + ', '.join(unresolved))
    ok = False
sys.exit(0 if ok else 1)
