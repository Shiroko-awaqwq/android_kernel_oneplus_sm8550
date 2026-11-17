# KernelSU GKI kernel for OnePlus Ace 3 (sm8550 / PJE110)

This branch is `oneplus/sm8550_v_15.0.0_ace_3` (Linux **5.15.167**, the exact
kernel version reported by PJE110 `16.0.1.300(CN01)`) with the latest
[KernelSU](https://github.com/tiann/KernelSU) integrated **in-kernel**, built by
GitHub Actions into a flashable AnyKernel3 package.

| item | value |
| --- | --- |
| kernel base | OnePlus OSS `oneplus/sm8550_v_15.0.0_ace_3`, 5.15.167 |
| vendor tree | `PoXiao777/android_kernel_modules_and_devicetree_oneplus_sm8550` (same branch) |
| root solution | KernelSU `v3.3.1` (in-kernel, `CONFIG_KSU=y`, kprobe hooks) |
| toolchain | AOSP clang `r450784e` (`master-kernel-build-2022`) |
| defconfig | `gki_defconfig` + `vendor/kalama_GKI.config` |
| output | `out/arch/arm64/boot/Image` → AnyKernel3 zip |

## Why the extra vendor tree?

`arch/arm64/configs/*` and several drivers on this branch pull files from
`../vendor/oplus/...` through symlinks, so the OPLUS *modules & devicetree*
repository has to sit one level above the kernel tree:

```
ws/                        <- OPLUS modules & devicetree repo
└── kernel_platform/
    └── common/            <- this repository
out/                       <- build output
```

## Building

Actions → **Build KernelSU GKI kernel (OnePlus Ace 3 / sm8550)** → *Run workflow*.

Inputs:

* `ksu_ref` — KernelSU tag/branch/commit; empty or `latest` resolves the newest
  KernelSU release at build time (currently `v3.3.1`).
* `label` — optional suffix for the artifact name.

The workflow:

1. checks out the OPLUS vendor tree and this kernel tree in the layout above;
2. downloads AOSP clang `r450784e`;
3. clones KernelSU at the requested ref, links it to `drivers/kernelsu`, adds
   `source "drivers/kernelsu/Kconfig"` to `drivers/Kconfig` and
   `obj-$(CONFIG_KSU) += kernelsu/` to `drivers/Makefile`;
4. appends the selinux include paths KernelSU needs
   (`-I$(srctree)/security/selinux/include -I$(objtree)/security/selinux`,
   `file_wrapper.c` includes `objsec.h` → `avc.h` → generated `av_permissions.h`);
5. builds `gki_defconfig vendor/kalama_GKI.config` and compiles the kernel;
6. packs `Image` + `anykernel3/anykernel.sh` into an AnyKernel3 zip.

Artifacts: `AK3-KernelSU-<kernel.release>-<date>.zip` (flashable),
`Image-<kernel.release>` (raw kernel) and `build-log`.

## Flashing

1. Back up the current boot image first
   (`adb shell su -c "dd if=/dev/block/by-name/boot$(getprop ro.boot.slot_suffix) of=/sdcard/boot_stock.img"`,
   or use a kernel manager's own backup feature).
2. Flash the AK3 zip with Kernel Flasher / Horizon Kernel Flasher / TWRP, or
   `fastboot flash boot boot_new.img` after repacking.
3. Install the official **KernelSU Manager** (`me.weishu.kernelsu`) matching the
   integrated version — the manager signature hash is compiled in, forks of the
   manager will be rejected.

Rollback: flash the backed-up `boot_stock.img` to `boot`.

## Notes / caveats

* Only the kernel is flashed; the stock `vendor_dlkm` modules stay untouched, so
  the build must keep the OSS defconfig unchanged (apart from `CONFIG_KSU`),
  otherwise module CRC/vermagic checks can reject the stock modules.
* `CONFIG_KSU` requires `CONFIG_KPROBES`, `CONFIG_KALLSYMS_ALL` and
  `CONFIG_EXT4_FS`; all three are already enabled by `gki_defconfig`.
* KernelSU is built with the official manager signature; `KSU_DEBUG` stays off.
