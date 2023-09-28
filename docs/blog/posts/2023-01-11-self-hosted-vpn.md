---
categories:
    - Programming
date: 2023-01-11
---

# Self Hosted VPN with Tailscale

Having your own VPN can be useful for bypassing geo-restrictions and censorship, as your IP address is that of the exit node. Your traffic is also encrypted and this protects you against sniffing attacks when using public WiFi.

However most VPN services are paid. So if you have a physical server/VPS running somewhere, why not use that?

[Tailscale][tailscale] is an awesome open-source VPN service which lets you create a secure peer-to-peer network between your devices. It's built on the open-source [Wireguard][wireguard] protocol which is faster than the IPsec and OpenVPN protocols.

<!-- more -->

It turns out that Tailscale also allows you to redirect all traffic from your device to another device in your peer-to-peer network (an 'exit node'). This is what we will setup on Fedora, the distro I use for my [server][server].

## Setting up a Tailscale Exit Node on Fedora

To setup a Tailscale exit node, first ensure that you have Tailscale setup on both devices.

Then, follow the instructions [here][exit-node].

**Notes**

On the exit node, you will need to run the following [additional commands][firewalld] to add the `tailscale0` interface to the [`trusted`][zones] group of `firewalld`:

```bash
sudo firewall-cmd --zone=trusted --change-interface=tailscale0 --permanent
sudo systemctl restart tailscaled
```

This will prevent the firewall from blocking incoming connections from your devices.

## Using the Exit Node

To use the exit node, do:

```bash
sudo tailscale up --exit-node=<exit node ip>
```

Optionally, to access devices on the LAN in the VPN (disabled by default): do:

```bash
sudo tailscale up --exit-node=<exit node ip> --exit-node-allow-lan-access=true
```

[zones]: https://firewalld.org/documentation/zone/predefined-zones.html
[server]: 2022-05-22-my-self-hosting-journey.md
[wireguard]: https://www.wireguard.com/
[tailscale]: https://tailscale.com/
[exit-node]: https://tailscale.com/kb/1103/exit-nodes/
[firewalld]: https://github.com/tailscale/tailscale/issues/4639#issuecomment-1125643993
