# Windows 11 VM with GPU Passthrough

intel_iommu=on
grub2-mkconfig -i /boot/grub2/grub.cfg
https://www.digitalcitizen.life/install-windows-11-virtual-machine/
DMAR: IOMMU enable - This IS NOT sufficient, there must be additional dmesg stuff


Write about enabling NFS support - using another host adapter
Macvtap allows guest to appear on LAN
Setting up NFS in windows and installing games on demand - must enable 'NFS services...'
Must also open NFS port in Libvirt zone
