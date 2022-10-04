---
tags:
    - Programming
---

# Windows 11 Gaming VM with GPU Passthrough on Fedora 36

<figure>
  <img src="/static/images/2022-07-10/demo.jpg" alt="Gaming on a laptop remotely over Nvidia Gamestream" loading="lazy"/>
  <figcaption>Gaming on a laptop remotely with Nvidia Gamestream using mobile data</figcaption>
</figure>

After completing this guide, you will have a Windows 11 **headless** virtual machine that can be accessed via:

-   [Moonlight][moonlight]/[Steam Link][steam-link] for high performance gaming
-   RDP for less demanding tasks
-   RDP over a web browser (via [Apache Guacamole][apache-guacamole])

## Prerequisites:

1. Ensure you have a CPU with virtualization support (for Intel, this is known as [`VT-d`][vt-d]):

    ```
    $ lscpu | grep -i virtualization
    Virtualization:                  VT-x
    ```

2. NVIDIA GPU (for Moonlight streaming)

3. `VT-d` should be enabled in your BIOS (refer to the relevant manuals)

4. [Docker](https://docs.docker.com/desktop/linux/install/) is installed

5. Windows 11 Pro license (required for Remote Desktop)

## 1. Setup GPU Passthrough

**Enable IOMMU**

Open `/etc/default/grub` with your editor of choice, and append `intel_iommu=on` as well as `initcall_blacklist=sysfb_init` to `GRUB_CMDLINE_LINUX`:

```bash
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

```bash
grub2-mkconfig -o /boot/grub2/grub.cfg
```

**Configure `vfio-pci` module to load on boot**

Create the following files with the content as shown (you will need superuser privileges):

```bash
#/etc/dracut.conf.d/10-vfio.conf
add_drivers+=" vfio_pci vfio vfio_iommu_type1 vfio_virqfd "

#/etc/modules-load.d/vfio-pci.conf
vfio-pci

#/etc/modprobe.d/vfio.conf
options vfio-pci ids=<GPU-PCI-ID>
```

Where `<GPU-PCI-ID>` is the id `xxxx:xxxx` as shown by the output of `lspci -nn`, for example:

```
[root@server ~]# lspci -nn | grep -i vga
01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GP104 [GeForce GTX 1070 Ti] [10de:1b82] (rev a1)
```

You will need to rebuild the initial ramdisk (`initrd`) image after modifying the above files:

```
dracut -fv
```

Check that the generated ramdisk contains output similar to the following using `lsinitrd`:

```
[root@server ~]# lsinitrd | grep -i vfio
-rw-r--r--   1 root     root           31 Mar 30 16:53 etc/modprobe.d/vfio.conf
-rw-r--r--   1 root     root            9 Mar 30 16:53 etc/modules-load.d/vfio-pci.conf
drwxr-xr-x   1 root     root            0 Mar 30 16:53 usr/lib/modules/5.18.18-200.fc36.x86_64/kernel/drivers/vfio
<truncated>
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

??? note "Giving the VM an IP address on the LAN"

    If you would like your VM also have its own IP address on the LAN (e.g. to play multiplayer games with peers on the same subnet), you can add a [`macvtap`][macvtap] interface now, in addition to the standard bridge network between guest and host.

    To do this, add another `NIC` and ensure `Host device enpXsX: macvtap` is selected.

    ![](/static/images/2022-07-10/vm-network.jpg)

    If you just want to be able to access the VM over the internet, you can use a peer-to-peer VPN as shown [below](#5-setup-overlay-mesh-network-aka-peer-to-peer-vpn).

Next, install Windows 11 (you can get the ISO from [here](https://www.microsoft.com/software-download/windows11)).

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

??? note "Streaming the whole desktop"

    If you want to stream the desktop instead of a game, add `C:\Windows\System32\mstsc.exe`.

## 5. Setup Overlay Mesh Network (aka Peer-to-Peer VPN)

We will now setup a peer-to-peer VPN, which will let us access Moonlight both within the LAN and from the internet, without worrying about port forwarding or firewall configurations.

??? note "Rationale"

    Moonlight requires [certain ports][moonlight-ports] to be forwarded on your router, in order for the PC to be accessible over the internet.

    However, in our current setup, the VM is not directly accessible from the internet or even the LAN, because the [default network][default-network][^default-network] it is connected to is not assigned an IP address on the LAN, so there is no way to port forward the required ports.

    One way is to give the VM its own IP address on the network via a [`macvtap`][macvtap] interface, as [shown above](#4-install-windows-and-setup-moonlight-streaming).

    However, sometimes port forwarding may not work due to [NATs][nat], your ISP blocking ports, or firewalls.

    Therefore, a better solution is to use a peer-to-peer VPN provider, which utilize [NAT traversal][nat-traversal] techniques such as [UDP hole punching][udp-hole-punching] to connect to hosts behind NATs/firewalls.

    - [ZeroTier][zerotier]: partially open-source, freemium
    - [Tailscale][tailscale]: partially open-source, freemium
    - [Nebula][nebula]: open-source
    - [Netmaker][netmaker]: open-source, [claims to be the fastest][netmaker-claim]

    Overhead is minimal, as these tools connect directly if possible, using a relay only as a backup.

[ZeroTier][zerotier] is one such solution, and you can follow the [guide from the Moonlight docs][zerotier-guide].

After setting up the peer-to-peer VPN of your choice, download the [Moonlight][moonlight] client on another computer/device, and verify that streaming works.

You can also [setup Remote Desktop](https://support.microsoft.com/en-us/windows/how-to-use-remote-desktop-5fe128d5-8fb1-7a23-3b8a-41e636865e8c#ID0EDD=Windows_11) now.

Now, you have a working VM with [Moonlight][moonlight] for gaming, and Remote Desktop (slower, but much less data usage) for doing work!

## 6. Setup Apache Guacamole

<figure>
  <img src="/static/images/2022-07-10/guacamole.jpg" alt="Accessing a Windows VM over a browser with Apache Guacamole" loading="lazy"/>
  <figcaption>Accessing a Windows VM over a browser with Apache Guacamole</figcaption>
</figure>

[Apache Guacamole][apache-guacamole] is a clientless remote desktop gateway, supporting proxying of RDP and VNC protocols over a HTML5 frontend. For this guide, we will use RDP, as it is more efficient than VNC and saves data.

Of note, Guacamole also supports SSH connections to a remote server, displaying the terminal in the web browser. However, the current version (`1.4.0`) of the Apache Guacamole Server Docker [image](https://github.com/apache/guacamole-server) only supports connecting via `ssh-rsa` and `ssh-dss`, both of which have been [deprecated since OpenSSH 8.8][openssh-8.8] ([JIRA issue][guacamole-ssh]) due to security issues (SHA-1 is no longer considered secure). One workaround would be to enable `ssh-rsa` in `sshd`, however this is suboptimal. As a result, I have decided to use [SSHwifty][sshwifty] instead as an SSH web proxy.

To setup Apache Guacamole, follow the instructions [here][apache-guacamole-docker].

??? note "Notes"

    -   I have decided to use the `mysql` backend instead, as the `postgres` backend has [authentication problems][guacamole-postgresql] (slated to be fixed in `1.5.0`).
    -   If you are using a reverse proxy with authentication (e.g. Nginx with `auth_request`), you can use [header authentication][guacamole-header-auth] to avoid having to login into Guacamole.
    -   To change the password of the default `guacadmin` user, it is necessary to create another user account with admin rights.
    -   For RDP, ensure `Ignore server certificate` is checked, otherwise Guacamole will refuse to connect.

## 7. (Optional) Setup NFS/SAMBA

Network File System (NFS) is a handy way to share files on a Linux host with other Linux clients. For sharing files with Windows clients, SAMBA is the better option (much less delay on opening).

**Note**: If you are using a `macvtap` interface (to allow the guest to receive its own IP address on the network), it is [not possible][macvtap-issues] to connect to the host due to how `macvtap` works. You will need to create a `NAT` connection (e.g. `Virtual Network 'Default' : NAT`) to connect to the host, via a separate subnet.

**NFS**

Windows does not come with NFS support by default - you must enable it. In an elevated PowerShell window, run:

    ```powershell
    Enable-WindowsOptionalFeature -FeatureName ServicesForNFS-ClientOnly, ClientForNFS-Infrastructure -Online -NoRestart
    ```

This [fix][slow-nfs-fix] _may_ speed up NFS access on Windows (although I strongly recommend using SAMBA).

-   For Fedora: You must also open the NFS ports (TCP/UDP `111`, `2049` and `20048`) in the `Libvirt` zone.

**SAMBA**

[SAMBA][samba] is much faster than NFS for Windows guests.

To setup Samba:

1.  Install Samba on Linux:

    ```bash
    sudo dnf install samba samba-common
    ```

2.  Set the correct SELinux contexts for the directories you wish to share (in this example `/mnt/storage`):

    ```bash
    sudo chcon -R -t samba_share_t /mnt/storage
    ```

    ??? warning "SSH and SELinux"

        If you are executing the above command on your `home` directory, be careful to restore SELinux contexts for the `.ssh` directory:

        ```bash
        sudo restorecon -r .ssh
        ```

        Otherwise, `sshd` will be **denied access** to `authorized_keys` and you will lose login via SSH!

3.  Add the following to `/etc/samba/smb.conf`:

    ```config
    [storage]
        path = /mnt/storage
        public = yes
        guest ok = yes
        writable = yes
        browseable = yes
        acl allow execute always = yes
    ```

    This will create a share named `storage`, accessible without login or passwords. **Only do this on a secure LAN!**

4.  (For Fedora) Open the required ports in the `libvirt` zone (for the Windows guest), and in the `Public` zone for other computers on the network:

    -   TCP `139`, `445`
    -   UDP `137`, `138`

5.  Restart the `smb` and `nmb` daemons:

    ```bash
    sudo systemctl enable --now smb nmb
    ```

You should now have access to the Samba share on the Windows guest, by hitting ++win+r++ and entering the IP address of the host.

## 8. (Optional) Fix low FPS on desktop and certain games

[Moonlight][moonlight] runs at 30fps or less when displaying the remote desktop (when not in a game). I suspect this is probably because the desktop is not rendered using the GPU and natively running at a lower FPS. Moonlight is transferring this output when the GPU is not being utilized, for example with the desktop or certain 2D games.

To fix this, you will need to get an **HDMI dummy plug**.

-   Plug the HDMI dummy plug into the graphics card output.
-   In the Windows VM, ensure that displays are set to mirror each other.

    -   You might need to play around with the displays a bit, to ensure that Moonlight is streaming the display from the GPU output, and not that of the VM.

-   You might need to reboot the VM after.

You should now be getting ~60fps when streaming the bare desktop.

## Conclusion

And that's it! You now have a fully featured cloud gaming machine, accessible anywhere in the world.

## Known Issues/Notes/Fixes

### Disabling VFIO

At times you may want to disable VFIO or GPU passthrough, for example when you want to [use the GPU in the host](2022-07-10-docker-gpu-fedora.md).

To disable GPU passthrough:

-   Rename the file `/etc/modprobe.d/vfio-pci.conf` to `/etc/modprobe.d/vfio-pci.conf.bak`.
-   Add the following lines to `GRUB_CMDLINE_LINUX` in `/etc/default/grub`:

    ```
    rd.driver.blacklist=nouveau modprobe.blacklist=nouveau nvidia-drm.modeset=1 initcall_blacklist=simpledrm_platform_driver_init
    ```

-   Regenerate `grub.cfg` with `grub2-mkconfig -o /boot/grub2/grub.cfg`.
-   Regenerate the `initramfs` with `dracut -fv`.
-   Reboot.

To re-enable GPU passthrough, reverse the steps above.

### Moonlight-specific Issues

-   Moonlight requires that the server machine (whether VM or physical) be **unlocked**, and that there are **no Remote Desktop Connections** ongoing.

    -   After an RDP session, the main desktop is locked. To fix this, create a batch file with the following content, and run it **with administrator rights** to disconnect the RDP and unlock the main desktop:

        ```
        Powershell -Command "tscon rdp-tcp#0 /DEST:console"
        ```

-   The streaming resolution of Moonlight is **not** what is set in the GUI of Moonlight or in the game, but rather, it is capped at the resolution of the virtual machine's desktop. So, if you want to stream in 4K, ensure you change the virtual machine's desktop resolution to 4K prior to launching the game.

-   Some useful shortcuts:

    -   Quit moonlight: ++ctrl+alt+shift+q++
    -   Minimize window: ++ctrl+alt+shift+d++
    -   Show stats overlay: ++ctrl+alt+shift+s++
    -   Paste text from host: ++ctrl+alt+shift+v++
    -   Toggle mouse and keyboard capture: ++ctrl+alt+shift+z++

-   Moonlight not filling screen:

    -   [Use the Nvidia control panel to change the screen resolution.][moonlight-fix]

-   Intermittent black screen: [Disable hardware-accelerated GPU scheduling][gpu-scheduling]

### QEMU/`virt-manager`

-   Snapshotting the VM is not possible while a PCI device is being passed-through. However, if you are using BtrFS, you can make snapshots of the storage volume.

-   VM hangs/pauses, and in `dmesg` you see `[ 6044.433981] vfio-pci 0000:07:00.0: BAR 0: can't reserve [mem 0xe0000000-0xefffffff 64bit pref]` and similar errors:

    -   Ensure that the [`initcall_blacklist=sysfb_init`][gpu-fix] kernel parameter has been added to `grub.cfg`.

-   `virt-manager`/QEMU supports sharing the VM display via an embedded VNC server. For Apache Guacamole to connect to this however, the embedded viewer (in `virt-manager`) must first be closed.

-   Windows XP only: In `virt-manager`, the NIC device model must be `rtl8139`, and the sound card model as `AC97` in order for drivers to be installed.

-   Nvidia Geforce Experience says 'Unsupported CPU':

    -   Change the CPU model in `virt-manager` (in the XML) to `host-model` ([preferred][cpu-model]) or `host-passthrough`.

-   Passthrough-ed USB devices, when disconnected, prevent the VM from booting

    -   Add [`startupPolicy="optional"`][usb-devices] to the `<source>` tag in the XML for the passthrough-ed USB device

-   Low FPS when display is set to 'Duplicate these displays':

    -   Change display settings to 'Extend these displays' instead. I suspect when displays are duplicated, the GPU works extra to render frames on both monitors, causing the FPS drop.

-   [Useful VM performance tuning options][vm-tuning]

    -   For example, setting multiple sockets with each having 1 CPU and 1 core is more efficient.

-   Types of VM network connections compared:
    ![](/static/images/2022-07-10/vm-networking.png)

For more information on the `libvirt` domain XML, check out the [documentation][libvirt-xml].

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

-   Connection speed: Moonlight > Steam Link >> RDP > Guacamole > `virt-manager`

## Credits

-   [Fedora 33: Ultimiate VFIO Guide for 2020/2021 [WIP]](https://forum.level1techs.com/t/fedora-33-ultimiate-vfio-guide-for-2020-2021-wip/163814)
-   [PCI passthrough via OVMF](https://wiki.archlinux.org/title/PCI_passthrough_via_OVMF#Setting_up_IOMMU)

[^default-network]: The default network (which you can view with `sudo virsh net-dumpxml default`) is configured with [`forward mode='nat'`][libvirt-network-connectivity], which allows outbound communication for guests, but not inbound communications (unless you configure computers on the LAN to use your host as a NAT).

[vt-d]: https://d2pgu9s4sfmw1s.cloudfront.net/UAM/Prod/Done/a062E00001eOlkFQAS/6d0ff26e-78fe-42cf-b29d-0bd57685ca5d?Expires=1657719487&Key-Pair-Id=APKAJKRNIMMSNYXST6UA&Signature=waVppuy971q9Y-W9oM88UqwSMNidyxs6Huu7U0gGw30IWwVXTFPiR~EAMEjMfvECkdaYfSeEFJFvboMCsk82bmK0wG2ec3H-~hoR5JJJEaPvFw3lKvzXSvY87MmMpSDA~PYSVqI0tFaibt1eZBhgqggbQwsdYsqFq4RSRCOjXDJIUA8mZwF9-GtRc2xEZkqUliYoMLSSgfmDLNoC3nGZtFzH~wxPjI~-5zr9lvE1dTxiGMQOtzEM~EYleNZwjHuVmIBmzNuKLxRZtAQDFAApk05ZOw10AZsFqvq~RR5YwUjAuADxEL6TuQXTgXiCSK-qf6hOBUCrlgQu6IWlYtKa2A__
[moonlight]: https://moonlight-stream.org/
[apache-guacamole]: https://guacamole.apache.org/
[guacamole-ssh]: https://www.mail-archive.com/issues@guacamole.apache.org/msg06190.html
[openssh-8.8]: https://www.openssh.com/txt/release-8.8
[sshwifty]: https://github.com/nirui/sshwifty
[apache-guacamole-docker]: https://guacamole.apache.org/doc/gug/guacamole-docker.html
[guacamole-header-auth]: https://guacamole.apache.org/doc/gug/guacamole-docker.html#header-authentication
[guacamole-postgresql]: https://lists.apache.org/thread/mp6gfxtxwhnnk215crcjbt0106w03o7l
[macvtap-issues]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/virtualization_host_configuration_and_guest_installation_guide/app_macvtap
[slow-nfs-fix]: https://docs.oracle.com/en-us/iaas/Content/File/Troubleshooting/winNFSerror53.htm
[gpu-fix]: https://forum.proxmox.com/threads/problem-with-gpu-passthrough.55918/post-478351
[moonlight-fix]: https://github.com/moonlight-stream/moonlight-android/issues/588
[steam-link]: https://store.steampowered.com/remoteplay#anywhere
[nvenc]: https://en.wikipedia.org/wiki/Nvidia_NVENC
[usb-devices]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/sect-manipulating_the_domain_xml-devices#sect-Host_physical_machine_device_assignment-USB_PCI_devices
[chcon]: https://fedoraproject.org/wiki/SELinux/samba
[vm-tuning]: https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html-single/virtualization_tuning_and_optimization_guide/index
[libvirt-xml]: https://libvirt.org/formatdomain.html
[samba]: https://www.samba.org/
[moonlight-ports]: https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide#manual-port-forwarding-advanced
[zerotier-guide]: https://github.com/moonlight-stream/moonlight-docs/wiki/Setup-Guide#zerotier
[zerotier]: https://www.zerotier.com/
[udp-hole-punching]: https://en.wikipedia.org/wiki/UDP_hole_punching
[nat]: https://en.wikipedia.org/wiki/Network_address_translation
[tailscale]: https://tailscale.com/
[nat-traversal]: https://tailscale.com/blog/how-nat-traversal-works/
[macvtap]: https://virt.kernelnewbies.org/MacVTap
[cpu-model]: https://libvirt.org/formatdomain.html#cpu-model-and-topology
[default-network]: https://libvirt.org/formatnetwork.html#nat-based-network
[libvirt-network-connectivity]: https://libvirt.org/formatnetwork.html#connectivity
[nebula]: https://github.com/slackhq/nebula
[netmaker]: https://github.com/gravitl/netmaker/
[netmaker-claim]: https://medium.com/netmaker/battle-of-the-vpns-which-one-is-fastest-speed-test-21ddc9cd50db
[gpu-scheduling]: https://github.com/moonlight-stream/nvidia-gamestream-issues/issues/27
