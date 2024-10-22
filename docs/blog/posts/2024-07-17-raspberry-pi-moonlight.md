---
date: 2024-07-17
categories:
    - Programming
---

# Setting up Moonlight on a Raspberry Pi 4

Some notes on how I setup Moonlight to auto-launch on a Raspberry Pi 4, as well as random display/audio issues.

<!-- more -->

## Setup

Using the Raspberry Pi Imager, install the Lite version of the 64-bit Raspbian OS (this has no desktop environment). Configure SSH/wifi as required.

Boot/SSH into the Pi, and follow the instructions on [installing Moonlight].

To enable audio, install `pulseaudio`.

Then, run `sudo raspi-config` and ensure that `pulseaudio` is selected under Advanced > Audio Config.

To make Moonlight run on login, add the following to `~/.profile` (also adds an alias `moonlight`):

```sh
alias moonlight="moonlight-qt --1080 --quit-after --fps 60 --bitrate 20000 --game-optimization --audio-on-host stream windows-vm desktop"

# run moonlight only if we are in a non-ssh interactive shell on login
if [[ $- == *i* ]] && [[ -z $SSH_CLIENT ]]; then
    moonlight
fi
```

## Display Overscan/Cutoff

First, get the name of the display with `kmsprint`:

```text
user@pi:~ $ kmsprint
Connector 0 (32) HDMI-A-1 (disconnected)
  Encoder 0 (31) TMDS
Connector 1 (41) HDMI-A-2 (connected)
  Encoder 1 (40) TMDS
    Crtc 4 (105) 1920x1080@60.00 148.500 1920/88/44/148/+ 1080/4/5/36/+ 60 (60.00) U|D
      Plane 4 (95) fb-id: 343 (crtcs: 4) 0,0 1920x1080 -> 0,0 1920x1080 (XR24 AR24 AB24 XB24 RG16 BG16 AR15 XR15 RG24 BG24 YU16 YV16 YU24 YV24 YU12 YV12 NV12 NV21 NV16 NV61 P030 XR30 AR30 AB30 XB30 RGB8 BGR8 XR12 AR12 XB12 AB12 BX12 BA12 RX12 RA12)
        FB 343 1920x1080 NV12
```

Then, in `/boot/firmware/config.txt`, ensure that the following are set:

```
disable_fw_kms_setup=1
disable_overscan=1
```

In `/boot/firmware/cmdline.txt`, add the [following] (adjust as necessary):

```
video=HDMI-A-2:1920x1080@60,margin_left=48,margin_right=48,margin_top=32,margin_bottom=32
```

Finally, in order to keep bluetooth devices auto-connected (e.g. keyboard), you need to `trust` the device in `bluetoothctl`.

[installing Moonlight]: https://github.com/moonlight-stream/moonlight-docs/wiki/Installing-Moonlight-Qt-on-Raspberry-Pi-4
[following]: https://raspberrypi.stackexchange.com/a/145670
