# Dual-booting Fedora 35 with Windows 11


```
[nicholas@fedora ~]$ efibootmgr
BootCurrent: 0000
Timeout: 0 seconds
BootOrder: 0000,0004,2001,2002,2003
Boot0000* Fedora
Boot0001* Unknown Device: 
Boot0002* Unknown Device: 
Boot0004* Windows Boot Manager
Boot2001* EFI USB Device
Boot2002* EFI DVD/CDROM
Boot2003* EFI Network
```

How laptop EFI firmware is ignoring efibootmgr settings
Add as trusted key to UEFI otherwise it doesn't appear after Fedora install

https://github.com/rhboot/efibootmgr/issues/19
https://community.intel.com/t5/Intel-Desktop-Boards/EFI-boot-manager-ignores-menu-order-and-always-selects-to-load/td-p/197783

## Linux disadvantages

Devices drivers for some software are not yet mature, e.g. Elan fingerprint on my laptop, potentially scansnap scanner as well.

Using a central server instead of wasting time learning GUIs