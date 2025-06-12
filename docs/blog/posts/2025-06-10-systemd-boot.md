---
date: 2025-06-10
categories:
  - Programming
---

# Migrating to systemd-boot on Fedora

I have been using [GRUB] as the bootloader for my [home server]. Recently, I wanted to upgrade the boot drive (from 512GB to 1TB), and this necessitated regenerating the boot/ESP partitions as well as the bootloader.

!!! tip

    See [this][boot-process] for a detailed description of the entire boot process.

<!-- more -->

Unfortunately, reinstalling and configuring GRUB correctly was a major pain. I think part of the reason for that was that I wanted `/boot` to be on the same partition as my root filesystem (i.e., a [single root partition scheme]).

!!! note "My setup then"

    The `/boot` directory contains the [vmlinuz] (compressed kernel) and [initramfs] (initrd, initial ramdisk) images.

    ```sh
    #/etc/fstab
    UUID=xxxxx-yyyyy-zzzzzz1    /           btrfs   noatime 0 0
    UUID=xxxxx-yyyyy-zzzzzz2    /boot       ext4    defaults 1 2
    UUID=5B3D-F60A              /boot/efi   vfat    umask=0077 0 2 # ESP

    # umask=0077` ensures only the user has read/write permissions for files they own.
    ```

After moving `/boot` to the OS partition (keeping `/boot/efi` on a separate partition), GRUB refused to boot, despite [reinstalling][grub-reinstall] it multiple times with `dnf reinstall grub2-efi grub2-efi-modules shim-\*`. It kept falling back to the GRUB shell and I had to run the commands listed [here][grub-boot-prompt] manually in order to boot.

In the end, I decided to move to [systemd-boot]. This is a UEFI boot manager which is functionally very simple. It uses the [Boot Loader Specification] - boot entries are configured by generic configuration files on the ESP, one per boot entry, which prevents the previous conflicts between different OSes. It can read kernel/initramfs images on a separate partition (via [XBOOTLDR]) as well.

My final setup was as follows:

```sh
#/etc/fstab
UUID=xxxxx-yyyyy-zzzzzz1    /           btrfs   noatime 0 0
UUID=5B3D-F60A              /boot       vfat    umask=0077 0 2 # ESP
```

This setup is quite clean (to me) as all boot-related things are in one partition (and directory).

!!! note

    Ideally, `/boot` would be on my BtrFS OS partition (via XBOOTLDR), and the ESP on `/efi`. This would let me checksum/snapshot the kernel/initrd images. However, XBOOTLDR [uses the UEFI firmware to access filesystems][uefi-fs], and BtrFS is not supported.

## Setting it up

_With reference from [this guide][systemd-boot-fedora-guide]._

### Cleanup existing boot/EFI partitions

Unmount `/boot` and `/boot/efi` and delete the existing boot/EFI partitions (backing up if necessary).

Create a single `vfat` partition (via `parted`), and ensure the `boot` and `esp` flags are set (e.g. via `set 1 esp on`).

### Remove GRUB and install systemd-boot

```sh
sudo dnf remove -y grubby grub2\* memtest86\*
sudo dnf install -y systemd-boot-unsigned sdubby
```

Install the bootloader with `bootctl install`.

### Copy kernel and initrd images

First, check the output of `kernel-install` to determine what `KERNEL_INSTALL_BOOT_ROOT` is:

```sh
❯ kernel-install
        Machine ID: 558115e7bb59469e95e37044fb809c91
Kernel Image Type: pe
            Layout: bls
        Boot Root: /boot
  Entry Token Type: machine-id
      Entry Token: 558115e7bb59469e95e37044fb809c91
  Entry Directory: /boot/558115e7bb59469e95e37044fb809c91/6.14.9-200.fc41.x86_64
    Kernel Version: 6.14.9-200.fc41.x86_64
            Kernel: /usr/lib/modules/6.14.9-200.fc41.x86_64/vmlinuz
          Initrds: (unset)
  Initrd Generator: (unset)
    UKI Generator: (unset)
          Plugins: /usr/lib/kernel/install.d/40-dkms.install
                    /usr/lib/kernel/install.d/50-depmod.install
                    /usr/lib/kernel/install.d/50-dracut.install
                    /usr/lib/kernel/install.d/60-kdump.install
                    /usr/lib/kernel/install.d/90-loaderentry.install
                    /usr/lib/kernel/install.d/90-uki-copy.install
                    /usr/lib/kernel/install.d/92-crashkernel.install
                    /usr/lib/kernel/install.d/95-akmodsposttrans.install
Plugin Environment: LC_COLLATE=C.UTF-8
                    KERNEL_INSTALL_VERBOSE=0
                    KERNEL_INSTALL_IMAGE_TYPE=pe
                    KERNEL_INSTALL_MACHINE_ID=558115e7bb59469e95e37044fb809c91
                    KERNEL_INSTALL_ENTRY_TOKEN=558115e7bb59469e95e37044fb809c91
                    KERNEL_INSTALL_BOOT_ROOT=/boot
                    KERNEL_INSTALL_LAYOUT=bls
                    KERNEL_INSTALL_INITRD_GENERATOR=
                    KERNEL_INSTALL_UKI_GENERATOR=
                    KERNEL_INSTALL_STAGING_AREA=/tmp/kernel-install.staging.XXXXXX
  Plugin Arguments: add|remove
                    6.14.9-200.fc41.x86_64
                    /boot/558115e7bb59469e95e37044fb809c91/6.14.9-200.fc41.x86_64
                    /usr/lib/modules/6.14.9-200.fc41.x86_64/vmlinuz
                    [INITRD...]
```

If it is not `/boot`, then you need to change it by editing `/etc/kernel/install.conf` and ensure `BOOT_ROOT=/boot`. Otherwise, the images will be installed to the wrong directory.

Recheck this again with `kernel-install`.

Then, you can install and copy over the kernel/initramfs images. Note that the install scripts also regenerate the initramfs for you, as well as run `kernel-install`. Kernel parameters are fetched from `/etc/kernel/cmdline`, and configuration for dracut (initramfs generator) is in `/etc/dracut.conf.d`.

```sh
dnf reinstall kernel kernel-core kernel-modules
```

### Reboot

After this, confirm that your configuration is working with `bootctl`:

```sh
❯ sudo bootctl
System:
      Firmware: UEFI 2.80 (American Megatrends 5.27)
Firmware Arch: x64
  Secure Boot: disabled (setup)
  TPM2 Support: yes
  Measured UKI: no
  Boot into FW: supported

Current Boot Loader:
      Product: systemd-boot 256.15-1.fc41
    Features: ✓ Boot counting
              ✓ Menu timeout control
              ✓ One-shot menu timeout control
              ✓ Default entry control
              ✓ One-shot entry control
              ✓ Support for XBOOTLDR partition
              ✓ Support for passing random seed to OS
              ✓ Load drop-in drivers
              ✓ Support Type #1 sort-key field
              ✓ Support @saved pseudo-entry
              ✓ Support Type #1 devicetree field
              ✓ Enroll SecureBoot keys
              ✓ Retain SHIM protocols
              ✓ Menu can be disabled
              ✓ Boot loader sets ESP information
          ESP: /dev/disk/by-partuuid/a7ddf3f5-f9ce-41bf-80b2-36b2c8e15dfc
        File: └─/EFI/systemd/systemd-bootx64.efi

Random Seed:
System Token: set
      Exists: yes

Available Boot Loaders on ESP:
          ESP: /boot (/dev/disk/by-partuuid/a7ddf3f5-f9ce-41bf-80b2-36b2c8e15dfc)
        File: ├─/EFI/systemd/systemd-bootx64.efi (systemd-boot 256.15-1.fc41)
              └─/EFI/BOOT/BOOTX64.EFI (systemd-boot 256.15-1.fc41)

Boot Loaders Listed in EFI Variables:
        Title: Linux Boot Manager
          ID: 0x0001
      Status: active, boot-order
    Partition: /dev/disk/by-partuuid/a7ddf3f5-f9ce-41bf-80b2-36b2c8e15dfc
        File: └─/EFI/systemd/systemd-bootx64.efi

        Title: UEFI OS
          ID: 0x0002
      Status: active, boot-order
    Partition: /dev/disk/by-partuuid/a7ddf3f5-f9ce-41bf-80b2-36b2c8e15dfc
        File: └─/EFI/BOOT/BOOTX64.EFI

Boot Loader Entries:
        $BOOT: /boot (/dev/disk/by-partuuid/a7ddf3f5-f9ce-41bf-80b2-36b2c8e15dfc)
        token: fedora

Default Boot Loader Entry:
        type: Boot Loader Specification Type #1 (.conf)
        title: Fedora Linux 41 (Server Edition)
          id: 558115e7bb59469e95e37044fb809c91-6.14.9-200.fc41.x86_64.conf
      source: /boot//loader/entries/558115e7bb59469e95e37044fb809c91-6.14.9-200.fc41.x86_64.conf
    sort-key: fedora
    version: 6.14.9-200.fc41.x86_64
machine-id: 558115e7bb59469e95e37044fb809c91
      linux: /boot//558115e7bb59469e95e37044fb809c91/6.14.9-200.fc41.x86_64/linux
    initrd: /boot//558115e7bb59469e95e37044fb809c91/6.14.9-200.fc41.x86_64/initrd
    options: root=UUID=2a1d4d2a-7016-4f91-aa55-92d1b284668d ro rootflags=subvol=root noresume intel_iommu=on initcall_blacklist=sysfb_init >
```

If 'Default Boot Loader Entry' points to your OS, you're set, and you can reboot now.

[GRUB]: https://wiki.archlinux.org/title/GRUB
[home server]: 2022-05-22-my-self-hosting-journey.md#
[single root partition scheme]: https://wiki.archlinux.org/title/Partitioning#Single_root_partition
[initramfs]: https://wiki.archlinux.org/title/Arch_boot_process#initramfs
[vmlinuz]: https://en.wikipedia.org/wiki/Vmlinux
[boot-process]: https://wiki.archlinux.org/title/Arch_boot_process
[grub-reinstall]: https://docs.fedoraproject.org/en-US/quick-docs/grub2-bootloader/#_installing_grub2_on_a_uefi_system
[grub-boot-prompt]: https://docs.fedoraproject.org/en-US/quick-docs/grub2-bootloader/#_using_the_grub2_boot_prompt
[systemd-boot]: https://wiki.archlinux.org/title/Systemd-boot
[XBOOTLDR]: https://wiki.archlinux.org/title/Systemd-boot#Installation_using_XBOOTLDR
[Boot Loader Specification]: https://uapi-group.org/specifications/specs/boot_loader_specification/
[uefi-fs]: https://uapi-group.org/specifications/specs/boot_loader_specification/#the-partitions
[systemd-boot-fedora-guide]: https://github.com/hboetes/wiki/wiki/systemd%E2%80%90boot-on-fedora-40
