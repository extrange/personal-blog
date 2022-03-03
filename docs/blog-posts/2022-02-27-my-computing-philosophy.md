---
tags:
  - Programming
---
# My Computing Philosophy

What do people use a computer for? For me, in order of time spent:

- Web browsing (majority)
- Programming
- File management
- Messaging
- Gaming
- Word processing

I feel that there is not much to be gained by spending time learning the intricaties of each OS's GUI and their respective quirks (Gnome, KDE, Windows Desktop). I think one's time is better invested by developing a server (in Linux), with all the file/web hosting things you want, and then using other devices merely as clients to access that server and its data.

In essence, a **client-server** model for personal computing[^cloud-privacy].

The processing power or storage of the client then becomes irrelevant - any notebook, connected to the server using say `ssh` or some web frontend, will have the same capabilities as any other high-end notebook.

This saves money, as well as time spent configuring new devices (since everything is really being done on the server). As a bonus, since processing is [offloaded to the server][vscode-remote-containers] (for programming tasks), battery life is improved. The only configuration I'd do on the client would be:

- Changing the keyboard layout to Dvorak
- Setting up Flux or a blue screen filter equivalent
- Changing the default text editor to Vim, or similar keybindings

I used to spend a lot of time customizing my devices, but now the above is really all I need, the important customizations already stored in the cloud (VSCode, Firefox).

The important features of the client device that remain are the ergonomic comfort of the keyboard, total weight and the clarity of the display. Processor, hard disk space and memory take a backseat.

## Why not Windows

I've been using Windows ever since I started using computers. Recently however, I have been encountering a lot of frustrations in Windows.

- WSL has too many issues (no `systemd`, changing IP address, poor Docker volume mount performance)
- Potential windows spyware concerns, e.g. Edge requesting for more and more tracking
- Updates keep breaking things and resetting preferences (e.g. Edge homepage, system color theme)
- Updates force you to restart
- Even in 2022, Windows still lacks a decent package manager[^package-manager], making application updates a pain
- Powershell, while improving, is still behind Linux shells and utilities

## Why Windows
On the other hand, here are the reasons why I was using Windows:

- Gaming
- Really obscure, closed source, Windows-only tools
- Missing/substandard Linux device drivers[^linux-device-drivers]

## My Decision

On my client device (desktop/laptop), there isn't really much reason for me to use Windows apart from gaming, and so running Windows in either a VM (with GPU passthrough), or in a dualboot configuration (although that might cause more problems), is what I'll be doing.

The next few article in this series will chronicle my journey (and challenges) toward this end goal.

[^cloud-privacy]: Why not just store everything in the cloud? Because I don't trust Google (or Microsoft) with keeping the privacy of my data intact.
[^package-manager]: [Chocolatey](https://chocolatey.org/) is a good try, however.
[^linux-device-drivers]: E.g., my laptop's fingerprint reader couldn't be used for login, while it worked fine in Windows 11. Blame it on hardware vendors.



[vscode-remote-containers]: 2022-02-07-vscode-remote-containers-over-ssh.md