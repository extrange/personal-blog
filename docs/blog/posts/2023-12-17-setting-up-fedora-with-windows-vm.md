---
date: 2023-12-17
categories:
    - Programming
---

# Setting up Fedora with a Windows VM

This is a short guide on how to setup Fedora with a Windows VM via [libvirt], optionally sharing a RAID-1 Btrfs volume from the host to the Windows guest via SAMBA. I'm assuming you are coming from Windows.

Reasons why you might want to do this:

-   Windows is quite [annoying].
-   With [Looking Glass], you can passthrough your GPU to the Windows guest and enjoy native graphics performance.
-   The [Btrfs] filesystem allows snapshotting, checksumming and multi-disk RAID with an unequal number/size of drives.
-   You can snapshot the entire Windows VM and revert to it anytime.

<!-- more -->

## 1. Install Fedora

Head over to the [Fedora] website and grab the ISO of your choice. Fedora offers several 'spins' - these are simply Fedora with different desktop environments preinstalled. GNOME is the default, with KDE Plasma, XFCE, Budgie, Cinnamon and others available. There is quite a bit of [satire] re. GNOME vs KDE online.

Fedora uses the [Btrfs] filesystem by default. It also enables [zram] by [default][fedora-zram], an alternative to using [swap].

Notes:

-   If you'd like to just copy the ISO on a thumbdrive without having to format it, check out [Ventoy]. This utility, installed on a USB drive, allows you to boot multiple ISOs from a single thumbdrive.
-   UEFI is preferred over BIOS, and you can only install Fedora with UEFI if you boot the USB thumbdrive in UEFI mode.
-   If you don't create a `/boot` partition during the install (even if you have `/boot/efi`), it seems Fedora won't give you a boot menu to choose between kernels at startup.
-   [zram] is not the only option for compressed memory-based swap; [zswap] is another method which uses compressed memory as a cache, together with the disk for rarely-accessed pages of memory.

## 2. Setup virtualization, install Windows guest

Fedora uses the `dnf` package manager. Regarding virtualization, `qemu` is the emulator, and [`libvirt`][libvirt] is an API to access `qemu`. `virt-manager` is a graphical virtual machine manager and viewer.

To install all of the above automatically, Fedora provides a [helpful guide][fedora-virtualization]. In short, once you have confirmed you have hardware support and enabled `VT-d` in the BIOS/UEFI, run the following command:

```bash
sudo dnf install @virtualization
```

After install, you should be able to access `virt-manager` from your desktop.

Download the Windows disk iso from [here][windows-iso]. Due to permission issues with `libvirt`, you have to place the iso in `/var/lib/libvirt/images` in order for it to be able to access it.

Create a new VM, and select the downloaded ISO as the install media. Then, install Windows like normal.

## 3. Setup GPU Passthrough

The virtualization setup is as follows:

-   Host (Fedora): Uses either chip integrated graphics, or a separate dedicated GPU (preferably AMD).
-   Guest (Windows): Uses a GPU (preferably NVIDIA), pass-through'ed from the host.

Before proceeding, ensure you are not using the display output of the GPU you want to passthrough.

In order to setup GPU passthrough, you will need to use the `vfio` driver for your GPU (instead of `amdgpu`, `nouveau` or `nvidia`).

Follow step 1 of [this guide][vfio].

Check if you are successful by running the following command:

```bash hl_lines="4"
$ lspci -knn | grep -i nvidia -A5
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP102 [GeForce GTX 1080 Ti] [10de:1b06] (rev a1)
        Subsystem: NVIDIA Corporation Device [10de:120f]
        Kernel driver in use: vfio-pci
        Kernel modules: nouveau, nvidia_drm, nvidia
```

## 4. Setup Looking Glass

[Looking Glass] is an application which uses a shared memory region (IVSHMEM) between the host and guest to exchange frames with low latency. It consists of a host application which runs on the Windows guest VM, and a client application (the viewer), running on the Fedora host.

First, ensure the GPU you want to passthrough has a [dummy plug] attached. This is [required] in order for the passthrough'ed GPU to output video.

Then, follow the [installation instructions].

If you have successfully setup Looking Glass, you should now be able to access your Windows VM using the Looking Glass client, and see that the GPU is indeed available to Windows.

## 5a. Setup Btrfs volume on host

Now, we will setup a Btrfs volume in mirror (RAID-1). You will require 2 drives of the same size (for 2 drives, the usable size of a RAID-1 mirror will be that of the smaller).

First, identify your drives to be used:

```hl_lines="5 7"
$ lsblk
NAME        MAJ:MIN RM   SIZE RO TYPE  MOUNTPOINTS
sda           8:0    0   5.5T  0 disk
└─sda1        8:1    0   5.5T  0 part  /vm-storage
sdb           8:16   0  10.9T  0 disk
└─sdb1        8:17   0  10.9T  0 part
sdc           8:32   0  10.9T  0 disk
└─sdc1        8:33   0  10.9T  0 part  /mnt/storage
                                       /mnt/storage-root
```

In this example, I am using `/dev/sdb` and `/dev/sdc`.

Create a GPT partition table on the first drive (note: this will **delete** everything on it!):

```bash
sudo parted /dev/sdb -- mklabel gpt
```

Then, make a single partition spanning the whole drive.

```bash
sudo parted /dev/sdb -- mkpart storage btrfs 0% 100%
```

You can check that there is indeed a partition being created with `lsblk`.

Next, we format this partition with Btrfs:

```bash
sudo mkfs.btrfs /dev/sdb1
```

Btrfs allows the user to have multiple [subvolumes] within the filesystem, unlike other filesystems which would require you to instead make multiple partitions. Snapshots are perfomed on subvolumes, and the snapshots themselves are subvolumes.

By default, [Btrfs creates a 'root' subvolume at `/` of the drive][subvolumes]. We will create another subvolume named `root`, at `/root` (not to be confused with `/`). This will be where we put our files. In the future, snapshots of `/root` can be stored in another subvolume, e.g. `/snapshots`.

In order to create a subvolume, the drive must be mounted. In Linux, drives are mounted to folders, usually in `/mnt`.

Create a folder in `/mnt`:

```bash
sudo mkdir /mnt/storage
```

Mount the Btrfs real root (`/`) on it:

```bash
sudo mount /dev/sdb1 /mnt/storage
```

Create our subvolume, then unmount:

```bash
sudo btrfs subvolume create /mnt/storage/root
sudo umount /mnt/storage/root
```

To mount our `/root` subvolume, we can run:

```bash
sudo mount /dev/sdb1 -o subvol=root /mnt/storage
```

## 5b. Setup Btrfs RAID-1 mirror

Next, with your Btrfs volume mounted at `/mnt/storage`, copy all your files over to it:

```bash
# Assuming your files are in /home/user/my-files
# The '.' is important - see https://askubuntu.com/a/86891
cp -av /home/user/my-files/. /mnt/storage
```

Create an empty partition for your other drive in the same way as above (assuming it is `/dev/sdc`):

```bash
sudo parted /dev/sdc -- mklabel gpt
sudo parted /dev/sdc -- mkpart storage btrfs 0% 100%
# Note: we don't create a Btrfs filesystem now, it will be done automatically next step
```

Then, add this drive to our existing filesystem at `/mnt/storage`:

```bash
# This will create a Btrfs filesystem on /dev/sdc
sudo btrfs device add /dev/sdc1 /mnt/storage
```

Set up RAID-1, for both metadata and data:

```bash
sudo btrfs balance start -mconvert=raid1 -dconvert=raid1
```

This operation will take a while. If you want to read more on setting up RAID-1, you can refer to the [Btrfs documentation].

When it is complete, you should have a working RAID-1 setup. Check this with the following commands (note: I am using 3 drives for RAID 1, yours may be different):

```bash hl_lines="4-6 23"
$ sudo btrfs filesystem show /mnt/storage
Label: 'Main Storage'  uuid: 535ba318-5337-4b28-84c3-14fa6ef041a3
        Total devices 3 FS bytes used 7.14TiB
        devid    1 size 10.91TiB used 6.05TiB path /dev/sdc1
        devid    2 size 10.91TiB used 6.05TiB path /dev/sdb1
        devid    3 size 7.28TiB used 2.19TiB path /dev/sdd1

$ sudo btrfs filesystem usage /mnt/storage
Overall:
    Device size:                  29.11TiB
    Device allocated:             14.29TiB
    Device unallocated:           14.81TiB
    Device missing:                  0.00B
    Device slack:                    0.00B
    Used:                         14.29TiB
    Free (estimated):              7.41TiB      (min: 7.41TiB)
    Free (statfs, df):             4.86TiB
    Data ratio:                       2.00
    Metadata ratio:                   2.00
    Global reserve:              512.00MiB      (used: 0.00B)
    Multiple profiles:                  no

Data,RAID1: Size:7.13TiB, Used:7.13TiB (99.95%)
   /dev/sdc1       6.04TiB
   /dev/sdb1       6.04TiB
   /dev/sdd1       2.18TiB

Metadata,RAID1: Size:14.00GiB, Used:12.54GiB (89.60%)
   /dev/sdc1       9.00GiB
   /dev/sdb1      12.00GiB
   /dev/sdd1       7.00GiB

System,RAID1: Size:8.00MiB, Used:1.02MiB (12.70%)
   /dev/sdc1       8.00MiB
   /dev/sdb1       8.00MiB

Unallocated:
   /dev/sdc1       4.86TiB
   /dev/sdb1       4.86TiB
   /dev/sdd1       5.09TiB
```

Understanding exactly how much free space you have can be confusing on Btrfs, but for now you can just refer to the 'Free (estimated)' line.

We can also setup automounting on boot by editing `/etc/fstab`.

Open `/etc/fstab` with your editor of choice (e.g. `sudo nano /etc/fstab`) and add the following line:

```
UUID=<your-disk-uuid> /mnt/storage            btrfs   subvol=root,compress-force=zstd,nofail 0 0
```

The portion `subvol=root,compress-force=zstd,nofail` are the mount options. For general mount options, see `man mount`. Fer Btrfs specific mount options (e.g. `subvol, compress-force`), refer to the [Btrfs documentation][btrfs-mount].

Check that you didn't make any mistakes:

```bash
sudo findmnt --verify
```

Now, when you reboot, you should be able to see your storage volumes in the file manager.

## 6. Share Btrfs host volume with Windows guest

Unfortunately, Windows cannot read Btrfs. To share your Btrfs volume with Linux, setup a network share from the Fedora host to the Windows guest.

Follow the instructions [here][samba] for setting up SAMBA.

That's it! You should now have a working Windows VM capable of playing games with GPU passthrough.

## Common Linux commands

-   `ls`: list files. Add `-l` to show a list, `-a` to show hidden files, `-h` to show sizes in human readable format. You can combine multiple options e.g. `ls -alh`.
-   `cd <directory>`: change directory. If no arguments are given, default to the user's home directory
-   `pwd`: shows the current directory path
-   `rm <filename>`: delete a file
-   `nano <filename>`: open a small terminal editor to edit/create a text file
-   `sudo <command>`: run a command as superuser
-   `man <command>`: show manual for a command. Use `u` or `d` to scroll up/down.

## Other stuff to check out

-   [Lutris]: Play Windows games on Linux. Supports Starcraft 2, DotA 2 and so on.
-   [Obsidian]: Open-source note taking app with graph view of your notes and more.
-   [Syncthing]: Peer-to-peer filesharing with Android support. Google Drive alternative.
-   [Tailscale]: Peer-to-peer VPN, which lets you access computers anywhere as if they were on your LAN. Supports Android, Linux and Windows.

[Tailscale]: https://tailscale.com/
[Syncthing]: https://syncthing.net/
[Obsidian]: http://obsidian.md/
[Lutris]: https://lutris.net/
[libvirt]: https://libvirt.org/
[annoying]: 2022-02-27-my-computing-philosophy.md#declarative-environment
[Looking Glass]: https://looking-glass.io/
[Btrfs]: https://btrfs.readthedocs.io/en/latest/
[Fedora]: https://fedoraproject.org/
[Ventoy]: https://www.ventoy.net/en/index.html
[satire]: https://baine.jeojck.com/GNOMEvKDE.html
[zram]: https://wiki.archlinux.org/title/Zram
[fedora-zram]: https://fedoraproject.org/wiki/Changes/SwapOnZRAM#Detailed_Description
[swap]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/storage_administration_guide/ch-swapspace
[zswap]: https://wiki.archlinux.org/title/zswap
[fedora-virtualization]: https://docs.fedoraproject.org/en-US/quick-docs/virtualization-getting-started/
[windows-iso]: https://www.microsoft.com/software-download/windows11
[vfio]: 2022-07-10-win11-vm-gpu-passthrough.md#1-setup-gpu-passthrough
[dummy-plug]: https://shopee.sg/[SG+Local+Seller]+HDMI+dummy+dongle+plug+for+Computer-Laptop-Graphics+card-i.35062141.9337174262/
[required]: https://looking-glass.io/docs/B6/requirements/
[installation instructions]: https://looking-glass.io/docs/B6/install/
[subvolumes]: https://wiki.archlinux.org/title/btrfs#Subvolumes
[Btrfs documentation]: https://btrfs.readthedocs.io/en/latest/btrfs-device.html#starting-with-a-single-device-filesystem
[btrfs-mount]: https://btrfs.readthedocs.io/en/latest/Administration.html
[samba]: 2022-07-10-win11-vm-gpu-passthrough.md#7-optional-filesharing-virtiofsnfssamba
