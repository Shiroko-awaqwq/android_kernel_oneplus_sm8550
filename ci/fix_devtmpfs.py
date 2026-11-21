#!/usr/bin/env python3
# OPLUS's released 5.15.167 tree calls devtmpfs_* unconditionally while the stock
# config has CONFIG_DEVTMPFS=n and the headers lack the standard mainline stubs.
# Add the upstream stubs so the tree compiles with the shipping .config.
# Usage: fix_devtmpfs.py <kernel_root>
import sys, os

W = sys.argv[1] if len(sys.argv) > 1 else '.'
p = os.path.join(W, 'include/linux/device.h')
s = open(p).read()

old = '''#ifdef CONFIG_DEVTMPFS
int devtmpfs_mount(void);
#endif'''
new = '''#ifdef CONFIG_DEVTMPFS
int devtmpfs_init(void);
int devtmpfs_create_node(struct device *dev);
int devtmpfs_delete_node(struct device *dev);
int devtmpfs_mount(void);
#else
static inline int devtmpfs_init(void) { return 0; }
static inline int devtmpfs_create_node(struct device *dev) { return 0; }
static inline int devtmpfs_delete_node(struct device *dev) { return 0; }
static inline int devtmpfs_mount(void) { return 0; }
#endif'''

if new in s:
    print('devtmpfs stubs already present')
elif old in s:
    s = s.replace(old, new, 1)
    open(p, 'w').write(s)
    print('devtmpfs stubs added')
else:
    print('ERROR: devtmpfs block not found in device.h')
    sys.exit(1)
