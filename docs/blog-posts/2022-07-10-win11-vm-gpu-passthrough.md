---
tags:
  - Programming
---

# Windows 11 Gaming VM with GPU Passthrough on Fedora 36

<figure>
  <img src="/static/images/2022-07-10/demo.jpg" alt="Gaming on a laptop remotely over Nvidia Gamestream" loading="lazy"/>
  <figcaption>Gaming on a laptop remotely with Nvidia Gamestream using mobile data</figcaption>
</figure>

After this guide, you will have a Windows 11 headless VM that can be accessed via:

-   [Moonlight][moonlight] (for high performance gaming)
-   RDP (for office work)
-   Web Browser (via [Apache Guacamole][apache-guacamole], no client required)

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

Open `/etc/default/grub` with your editor of choice, and append `intel_iommu=on` as well as `initcall_blacklist=sysfb_init` to `GRUB_CMDLINE_LINUX`:

```
GRUB_CMDLINE_LINUX="resume=UUID=16671cec-3bb8-46bb-b931-083c93082763 rhgb quiet intel_iommu=on initcall_blacklist=sysfb_init"
```

??? note "What is the purpose of `initcall_blacklist=sysfb_init`?"

    Even with the `vfio-pci` drivers utilized, the kernel appears to reserve portions of memory in the GPU which causes errors visible in `dmesg` as `[ 6044.433981] vfio-pci 0000:07:00.0: BAR 0: can't reserve [mem 0xe0000000-0xefffffff 64bit pref]`.

    The culprits for my system appeared to be `simplefb` and `bootfb`.

    Adding the above kernel parameter fixes the issue.

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

## 4. Install Windows and Setup Moonlight Streaming

Now, navigate to `http://localhost:8080` and you should see the `virt-manager` interface:

![](/static/images/2022-07-10/docker-virt-manager.gif)

Create a new VM, and under `Add Hardware > PCI Host Device`, add your GPU.

Under `NIC`, ensure `Host device enpXsX: macvtap` is selected.[^vm-nic]

![](/static/images/2022-07-10/vm-network.jpg)

Install Windows 11 (you can get the ISO from [here](https://www.microsoft.com/software-download/windows11)).

??? help "Error: This PC doesn't meet the minimum system requirements to install this version of Windows"

    You may encounter the error `This PC doesn't meet the minimum system requirements to install this version of Windows`. You can try this [fix](https://www.digitalcitizen.life/install-windows-11-virtual-machine/), or alternatively:

    -   Press ++shift+f10++ to open a command prompt
    -   Type `regedit`
    -   Navigate to `HKLM\System\Setup\LabConfig` (create the key if it doesn't exist)
    -   Add the following registry values (`DWORD (32-bit) Value`) with `1` as the value:
        -   `BypassTPMCheck`
        -   `BypassSecureBootCheck`
        -   `BypassCPUCheck` (optional)
        -   `BypassRAMCheck` (optional)

    Once the Windows VM boots, install the NVIDIA drivers, and then ensure that the GPU is detected by the VM.

![](/static/images/2022-07-10/vm-gpu.jpg)

Then, open GeForce Experience, and under 'Settings > SHIELD', enable 'Gamestream'.

![](/static/images/2022-07-10/vm-gamestream.jpg)

If you want to stream the desktop instead of a game, add `C:\Windows\System32\mstsc.exe`.

At this point, download the [Moonlight][moonlight] client on another computer/device, and verify that you can stream a game/the desktop.

You can also [setup Remote Desktop](https://support.microsoft.com/en-us/windows/how-to-use-remote-desktop-5fe128d5-8fb1-7a23-3b8a-41e636865e8c#ID0EDD=Windows_11) now.

Now, you have a working VM with [Moonlight][moonlight] for gaming, and Remote Desktop for doing work!

## 5. Setup Apache Guacamole

<figure>
  <img src="/static/images/2022-07-10/guacamole.jpg" alt="Accessing a Windows VM over a browser with Apache Guacamole" loading="lazy"/>
  <figcaption>Accessing a Windows VM over a browser with Apache Guacamole</figcaption>
</figure>

[Apache Guacamole][apache-guacamole] is a clientless remote desktop gateway, supporting proxying of RDP and VNC protocols over a HTML5 frontend. For this guide, we will use RDP, as it is more efficient than VNC and saves data.

Of note, Guacamole also supports SSH connections to a remote server, displaying the terminal in the web browser. However, the current version (`1.4.0`) of the Apache Guacamole Server Docker [image](https://github.com/apache/guacamole-server) only supports connecting via `ssh-rsa` and `ssh-dss`, both of which have been [deprecated since OpenSSH 8.8][openssh-8.8] ([JIRA issue][guacamole-ssh]) due to security issues (SHA-1 is no longer considered secure). One workaround would be to enable `ssh-rsa` in `sshd`, however this is suboptimal. As a result, I have decided to use [SSHwifty][sshwifty] instead as an SSH web proxy.

To setup Apache Guacamole, follow the instructions [here][apache-guacamole-docker].

Some notes:

-   I have decided to use the `mysql` backend instead, as the `postgres` backend has [authentication problems][guacamole-postgresql] (slated to be fixed in `1.5.0`).
-   If you are using a reverse proxy with authentication (e.g. Nginx with `auth_request`), you can use [header authentication][guacamole-header-auth] to avoid having to login into Guacamole.
-   To change the password of the default `guacadmin` user, it is necessary to create another user account with admin rights.
-   For RDP, ensure `Ignore server certificate` is checked, otherwise Guacamole will refuse to connect.

## 6. (Optional) Setup NFS

Network File System (NFS) is a handy way to share files on a Linux host with the Windows VM(s), so I have also set that up.

Some notes:

-   If you are using a `macvtap` interface (to allow the guest to receive its own IP address on the network), it is [not possible][macvtap] to connect to the host due to how `macvtap` works. You will need to create a `NAT` connection (e.g. `Virtual Network 'Default' : NAT`) to connect to the host, via a separate subnet.
-   Windows does not come with NFS support by default - you must enable it. In an elevated PowerShell window, run:

    ```powershell
    Enable-WindowsOptionalFeature -FeatureName ServicesForNFS-ClientOnly, ClientForNFS-Infrastructure -Online -NoRestart
    ```

-   To fix slow NFS access speeds on Windows, try this [fix][slow-nfs-fix].
-   For Fedora: You must also open the NFS ports (TCP/UDP `111`, `2049` and `20048`) in the `Libvirt` zone.

## Moonlight: Fix low FPS on desktop and certain games

[Moonlight][moonlight] runs at 30fps or less when displaying the remote desktop (when not in a game). I suspect this is probably because the desktop is not rendered using the GPU and natively running at a lower FPS. Moonlight is transferring this output when the GPU is not being utilized, for example with the desktop or certain 2D games.

To fix this, you will need to get an HDMI dummy plug.

-   Plug the HDMI dummy plug into the graphics card output.
-   In the Windows VM, ensure that displays are set to mirror each other.

    -   You might need to play around with the displays a bit, to ensure that Moonlight is streaming the display from the GPU output, and not that of the VM.

-   You might need to reboot the VM after.

You should now be getting 60fps when streaming the bare desktop.

## Conclusion

And that's it! You now have a fully featured cloud gaming machine, with web browser access, accessible anywhere in the world.

## Known Issues/Notes/Fixes

### Moonlight

-   Moonlight requires that the server machine (whether VM or physical) be **unlocked**, and that there are **no Remote Desktop Connections** ongoing.

    -   After an RDP session, the main desktop is locked. To fix this, create a batch file with the following content, and run it **with administrator rights** to disconnect the RDP and unlock the main desktop:

        ```
        Powershell -Command "tscon rdp-tcp#0 /DEST:console"
        ```

-   The streaming resolution of Moonlight is **not** what is set in the GUI of Moonlight or in the game, but rather, it is capped at the resolution of the virtual machine's desktop. So, if you want to stream in 4K, ensure you change the virtual machine's desktop resolution to 4K prior to launching the game.
-   Some useful shortcuts:
    -   Minimize window: ++ctrl+alt+shift+d++
    -   Show stats overlay: ++ctrl+alt+shift+s++
-   Moonlight not filling screen:
    -   [Use the Nvidia control panel to change the screen resolution.][moonlight-fix]

### QEMU/`virt-manager`

-   Snapshotting the VM is not possible while a PCI device is being passed-through. However, if you are using BtrFS, you can make snapshots of the storage volume.
-   VM hangs/pauses, and in `dmesg` you see `[ 6044.433981] vfio-pci 0000:07:00.0: BAR 0: can't reserve [mem 0xe0000000-0xefffffff 64bit pref]` and similar errors:
    -   Ensure that the [`initcall_blacklist=sysfb_init`][gpu-fix] kernel parameter has been added to `grub.cfg`.
-   `virt-manager`/QEMU supports sharing the VM display via an embedded VNC server. For Apache Guacamole to connect to this however, the embedded viewer (in `virt-manager`) must first be closed.
-   Windows XP only: In `virt-manager`, the NIC device model must be `rtl8139`, and the sound card model as `AC97` in order for drivers to be installed.
-   Types of VM network connections compared:
    ![](/static/images/2022-07-10/vm-networking.png)
-   Nvidia Geforce Experience says 'Unsupported CPU':
    -   Change the CPU model in `virt-manager` (in the XML) to `host-passthrough`.

### Apache Guacamole

-   For RDP, 'Support audio in console' must be **unchecked** for sound to work.

### Steam Link

[Steam Link][steam-link] is another solution for low latency desktop streaming, which is also available cross-platform. One advantage compared to [Moonlight][moonlight] is that it works without a GPU installed (it uses `libx264` on the CPU). While the performance using a GPU (using [NVENC][nvenc]) is roughly equivalent to Moonlight at the same bitrate, performance without a GPU leaves a lot to be desired, in terms of encoding time and therefore latency.

<figure>
  <img src="/static/images/2022-07-10/steamlink.jpg" alt="Steam Link without GPU" loading="lazy"/>
  <figcaption>Steam Link using <code>libx264</code> (CPU) encoding. <br/>Note the encoding latency of 130ms (game: Hearthstone)</figcaption>
</figure>

Gaming (even light) is therefore not possible without a GPU. Even for non-gaming tasks, there is little reason not to use Remote Desktop/Apache Guacamole instead, which have much lower network bandwidth requirements.

Steam Link also appears to render the cursor client-side, compared to Moonlight which renders the cursor on the server. This introduces some visible screen artifacts, as can be seen in the comparison images when the cursor is click-dragged rapidly (the desktop lags behind the cursor for Steam Link).

<figure>
  <img src="/static/images/2022-07-10/steamlink-cursor.jpg" alt="Steam Link" loading="lazy"/>
  <figcaption>Steam Link</figcaption>
</figure>

<figure>
  <img src="/static/images/2022-07-10/moonlight-cursor.jpg" alt="Moonlight" loading="lazy"/>
  <figcaption>Moonlight</figcaption>
</figure>

One advantage of Steam Link however is that no port forwarding appears to be required, while Moonlight sometimes has issues with UDP port 47999 when on mobile data (from my experience).

### Misc

-   Connection speed: Moonlight > RDP > Guacamole > `virt-manager`

## Credits

-   [Fedora 33: Ultimiate VFIO Guide for 2020/2021 [WIP]](https://forum.level1techs.com/t/fedora-33-ultimiate-vfio-guide-for-2020-2021-wip/163814)
-   [PCI passthrough via OVMF](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Setting_up_IOMMU)

[^vm-nic]: This is necessary to ensure that the VM gets an IP address on the LAN, so that you can connect to it with Moonlight.

[vt-d]: https://d2pgu9s4sfmw1s.cloudfront.net/UAM/Prod/Done/a062E00001eOlkFQAS/6d0ff26e-78fe-42cf-b29d-0bd57685ca5d?Expires=1657719487&Key-Pair-Id=APKAJKRNIMMSNYXST6UA&Signature=waVppuy971q9Y-W9oM88UqwSMNidyxs6Huu7U0gGw30IWwVXTFPiR~EAMEjMfvECkdaYfSeEFJFvboMCsk82bmK0wG2ec3H-~hoR5JJJEaPvFw3lKvzXSvY87MmMpSDA~PYSVqI0tFaibt1eZBhgqggbQwsdYsqFq4RSRCOjXDJIUA8mZwF9-GtRc2xEZkqUliYoMLSSgfmDLNoC3nGZtFzH~wxPjI~-5zr9lvE1dTxiGMQOtzEM~EYleNZwjHuVmIBmzNuKLxRZtAQDFAApk05ZOw10AZsFqvq~RR5YwUjAuADxEL6TuQXTgXiCSK-qf6hOBUCrlgQu6IWlYtKa2A__
[moonlight]: https://moonlight-stream.org/
[apache-guacamole]: https://guacamole.apache.org/
[guacamole-ssh]: https://www.mail-archive.com/issues@guacamole.apache.org/msg06190.html
[openssh-8.8]: https://www.openssh.com/txt/release-8.8
[ssh-wifty]: https://github.com/nirui/sshwifty
[apache-guacamole-docker]: https://guacamole.apache.org/doc/gug/guacamole-docker.html
[guacamole-header-auth]: https://guacamole.apache.org/doc/gug/guacamole-docker.html#header-authentication
[guacamole-postgresql]: https://lists.apache.org/thread/mp6gfxtxwhnnk215crcjbt0106w03o7l
[macvtap]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_host_configuration_and_guest_installation_guide/app_macvtap
[slow-nfs-fix]: https://docs.oracle.com/en-us/iaas/Content/File/Troubleshooting/winNFSerror53.htm
[gpu-fix]: https://forum.proxmox.com/threads/problem-with-gpu-passthrough.55918/post-478351
[moonlight-fix]: https://github.com/moonlight-stream/moonlight-android/issues/588
[steam-link]: https://store.steampowered.com/remoteplay#anywhere
[nvenc]: https://en.wikipedia.org/wiki/Nvidia_NVENC
