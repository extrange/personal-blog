# Windows 11 Gaming VM with GPU Passthrough on Fedora 36

<figure>
  <img src="/static/images/2022-07-10/demo.jpg" alt="Gaming on a laptop remotely over Nvidia Shield" loading="lazy"/>
  <figcaption>Gaming on a laptop remotely with Nvidia Shield using mobile data</figcaption>
</figure>

After this guide, you will have a Windows 11 headless VM that can be accessed via:

- [Moonlight][moonlight] (for high performance gaming)
- RDP (for office work)
- Web Browser (via [Apache Guacamole][apache-guacamole], no client required)

## Prerequisites:

1. Ensure you have a CPU with virtualization support (for Intel, this is known as [`VT-d`][vt-d]):

    ```
    $ lscpu | grep -i virtualization
    Virtualization:                  VT-x
    ```

2. NVIDIA GPU (for Moonlight streaming)

3. `VT-d` should be enabled in your BIOS (refer to the relevant manuals)

4. [Docker](https://docs.docker.com/desktop/linux/install/) is installed

5. Windows 11 Pro (for Remote Desktop)

## 1. Setup GPU Passthrough

Open `/etc/default/grub` with your editor of choice, and append `intel_iommu=on` to `GRUB_CMDLINE_LINUX`:

```
GRUB_CMDLINE_LINUX="resume=UUID=16671cec-3bb8-46bb-b931-083c93082763 rhgb quiet intel_iommu=on"  
```

Optionally, you may want to disable `os-prober` especially if you have Docker installed, as it will attempt to probe containers and create a lot of unnecessary startup entries:

```
GRUB_DISABLE_OS_PROBER=true  
```

Save the modified configuration file:

```
grub2-mkconfig -o /boot/grub2/grub.cfg
```

Next, create `/etc/dracut.conf.d/10-vfio.conf` with the following content:

```
add_drivers+=" vfio_pci vfio vfio_iommu_type1 vfio_virqfd " 
```

You will need to rebuild the initial ramdisk image:

```
dracut -fv
```

Now reboot, and check that IOMMU is working:

```shell hl_lines="4 8 9 10 11 12"
$ dmesg | grep -i iommu
[    0.000000] Command line: BOOT_IMAGE=(hd4,gpt4)/vmlinuz-5.18.10-200.fc36.x86_64 root=UUID=2a1d4d2a-7016-4f91-aa55-92d1b284668d ro rootflags=subvol=root resume=UUID=16671cec-3bb8-46bb-b931-083c93082763 rhgb quiet intel_iommu=on
[    0.133682] Kernel command line: BOOT_IMAGE=(hd4,gpt4)/vmlinuz-5.18.10-200.fc36.x86_64 root=UUID=2a1d4d2a-7016-4f91-aa55-92d1b284668d ro rootflags=subvol=root resume=UUID=16671cec-3bb8-46bb-b931-083c93082763 rhgb quiet intel_iommu=on
[    0.133749] DMAR: IOMMU enabled
[    0.224446] DMAR-IR: IOAPIC id 2 under DRHD base  0xfed91000 IOMMU 0
[    1.516533] iommu: Default domain type: Translated
[    1.516533] iommu: DMA domain TLB invalidation policy: lazy mode
[    1.560968] pci 0000:00:00.0: Adding to iommu group 0
[    1.560977] pci 0000:00:01.0: Adding to iommu group 1
[    1.560985] pci 0000:00:06.0: Adding to iommu group 2
[    1.560991] pci 0000:00:0a.0: Adding to iommu group 3
[    1.561003] pci 0000:00:14.0: Adding to iommu group 4
```

If you do not see the `... Adding to iommu group` lines, ensure `VT-d` has been turned on in your BIOS.

https://www.digitalcitizen.life/install-windows-11-virtual-machine/

## 2. Install Virtualization Packages

```
# sudo dnf install @virtualization
```

This will install the necessary packages, including [`libvirt`](https://libvirt.org/), an API to manage QEMU/KVM hypervisors.

## 3. Setup `virt-manager` in Docker

We will use `virt-manager` to manage the `libvirtd` backend. To make access easier, we will use [docker-virt-manager](https://github.com/m-bers/docker-virt-manager), which exposes `virt-manager` over a [GTK3 Broadway (HTML5) backend](https://blog.desdelinux.net/en/broadway-ejecuta-aplicaciones-gtk-navegador/).

Create a `docker-compose.yml` file with the following content:

```yaml
services:
  virt-manager:
    image: mber5/virt-manager:latest
    restart: always
    environment:
      HOSTS: "['qemu:///system']"
    ports:
      - "8080:80"

    volumes:
      - "/var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock"
      - "/vm:/vm" # Or wherever you want to store your VM images/virtual harddisks

    devices:
      - "/dev/kvm:/dev/kvm"
```

Start the container with `docker compose up -d`.


## 4. Install Windows

Now, navigate to `http://localhost:8080` and you should see the `virt-manager` interface:

![](/static/images/2022-07-10/docker-virt-manager.gif)

Create a new VM, and under `Add Hardware > PCI Host Device`, add your GPU.

Under `NIC`, ensure `Host device enpXsX: macvtap` is selected.

![](/static/images/2022-07-10/vm-network.jpg)

Install Windows 11 (you can get the ISO from [here](https://www.microsoft.com/software-download/windows11)).

You may encounter the error `This PC doesn't meet the minimum system requirements to install this version of Windows`. You can try this [fix](https://www.digitalcitizen.life/install-windows-11-virtual-machine/), or alternatively:

  - Press ++shift+f10++ to open a command prompt
  - Type `regedit`
  - Navigate to `HKLM\System\Setup\LabConfig` (create the key if it doesn't exist)
  - Add the following registry values (`DWORD (32-bit) Value`) with `1` as the value:
    - `BypassTPMCheck`
    - `BypassSecureBootCheck`
    - `BypassCPUCheck` (optional)
    - `BypassRAMCheck` (optional)

Once the Windows VM boots, install the NVIDIA drivers, and then ensure that the GPU is detected by the VM.

![](/static/images/2022-07-10/vm-gpu.jpg)

Then, open GeForce Experience, and under 'Settings > SHIELD', enable 'Gamestream'.

![](/static/images/2022-07-10/vm-gamestream.jpg)

If you want to stream the desktop instead of a game, add `C:\Windows\System32\mstsc.exe`.

At this point, download the [Moonlight][moonlight] client on another computer/device, and verify that you can stream a game/the desktop.

You can also [setup Remote Desktop](https://support.microsoft.com/en-us/windows/how-to-use-remote-desktop-5fe128d5-8fb1-7a23-3b8a-41e636865e8c#ID0EDD=Windows_11) now.

Now, you have a working VM with [Moonlight][moonlight] for gaming, and Remote Desktop for doing work!

## 5. Setup Apache Guacamole (WIP)

[Apache Guacamole][apache-guacamole] is a clientless remote desktop gateway, supporting proxying of RDP and VNC protocols over a HTML5 frontend. For this guide, we will use RDP, as it is more efficient than VNC and saves data.




## 6. (Optional) Setup NFS (WIP)


Write about enabling NFS support - using another host adapter
Macvtap allows guest to appear on LAN
Setting up NFS in windows and installing games on demand - must enable 'NFS services...'
Must also open NFS port in Libvirt zone

Setup NFS

## Known Issues

[Moonlight][moonlight] lags when displaying a remote desktop (when not in a game). I suspect this is probably because the desktop is not rendered using the GPU, and Moonlight can only transfer raw GPU video output, so the desktop is software rendered being transferred via some other protocol.

## Credits

- [Fedora 33: Ultimiate VFIO Guide for 2020/2021 [WIP]](https://forum.level1techs.com/t/fedora-33-ultimiate-vfio-guide-for-2020-2021-wip/163814)
- [PCI passthrough via OVMF](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Setting_up_IOMMU)

[vt-d]: https://d2pgu9s4sfmw1s.cloudfront.net/UAM/Prod/Done/a062E00001eOlkFQAS/6d0ff26e-78fe-42cf-b29d-0bd57685ca5d?Expires=1657719487&Key-Pair-Id=APKAJKRNIMMSNYXST6UA&Signature=waVppuy971q9Y-W9oM88UqwSMNidyxs6Huu7U0gGw30IWwVXTFPiR~EAMEjMfvECkdaYfSeEFJFvboMCsk82bmK0wG2ec3H-~hoR5JJJEaPvFw3lKvzXSvY87MmMpSDA~PYSVqI0tFaibt1eZBhgqggbQwsdYsqFq4RSRCOjXDJIUA8mZwF9-GtRc2xEZkqUliYoMLSSgfmDLNoC3nGZtFzH~wxPjI~-5zr9lvE1dTxiGMQOtzEM~EYleNZwjHuVmIBmzNuKLxRZtAQDFAApk05ZOw10AZsFqvq~RR5YwUjAuADxEL6TuQXTgXiCSK-qf6hOBUCrlgQu6IWlYtKa2A__
[moonlight]: https://moonlight-stream.org/
[apache-guacamole]: https://guacamole.apache.org/