---
date: 2024-04-29
categories:
    - Programming
---

# How to Undervolt a Laptop (with NixOS)

Sometimes your laptop might run too hot and you want to reduce the temperatures.

Apart from [cleaning the fans and changing the thermal paste], there are 2 software options available to you.

<!-- more -->

| Method                     | Pros                                                       | Cons                                                                                               |
| -------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Undervolting               | No performance impact. Lower battery usage.                | System instability                                                                                 |
| Lowering Temperature Limit | CPU cannot exceed the set temperature in any circumstance. | Poorer performance, as CPU will reduce frequency as necessary to keep within temperature envelope. |

Either or both methods can be used simultaneously.

The tool used for either of these is [`undervolt`][undervolt].

## Setup

Add the following packages:

```nix hl_lines="3-5"
home.packages = with pkgs; [
    # ...
    undervolt
    s-tui
    stress
];
```

Then run `sudo nixos-rebuild switch --flake path:.` in the same directory as your NixOS config.

To check if it works, run `sudo undervolt -r`. You should see output similar to the following:

```
❯ sudo undervolt -r
temperature target: -10 (90C)
core: 0.0 mV
gpu: 0.0 mV
cache: 0.0 mV
uncore: 8000.0 mV
analogio: 0.0 mV
powerlimit: 36.0W (short: 0.00244140625s - enabled) / 28.0W (long: 28.0s - enabled)
turbo: enable
```

## Undervolting

Undervolting reduces the voltage supplied to the CPU, reducing thermal generation, but also introducing instability, since the CPU is now running on a lower voltage than it was designed for.

There is no guaranteed value which will definitely be stable, so it is a process of trial and error.

Before applying any modifications, run `s-tui` and select `Stress`. Let it run for a few minutes and observe the maximum temperature, as well as average core frequency.

<figure>
  <img src="/static/images/2024-04-29/stress.png" alt="s-tui" loading="lazy"/>
  <figcaption>Baseline: the maximum temperature reached is 79C and average frequency is 2200MHz<figcaption/>
</figure>

We can start with -50mV to both the `core` and `cache` (note that the undervolt given to the `core` and `cache` must be identical).

```bash hl_lines="2 7 9"
# Settings are temporary and will be restored after reboot/crash
❯ sudo undervolt --core -50 --cache -50

# Confirm settings
❯ sudo undervolt -r
temperature target: -10 (90C)
core: -49.8 mV
gpu: 0.0 mV
cache: -49.8 mV
uncore: 8000.0 mV
analogio: 0.0 mV
powerlimit: 36.0W (short: 0.00244140625s - enabled) / 28.0W (long: 28.0s - enabled)
turbo: enable
```

Then, rerun `s-tui`. You should see that the average frequency is now higher, while the maximum temperature may be the same. This indicates that the CPU had additional thermal headroom to increase frequency further.

<figure>
  <img src="/static/images/2024-04-29/stress-undervolt.png" alt="s-tui" loading="lazy"/>
  <figcaption>The maximum temperature reached is still around 80C, but average frequency is 10% higher at 2400MHz<figcaption/>
</figure>

**Note: As you increase the undervolt (i.e. more negative), the system will become more unstable (BSOD, freezes, crashes, etc). The job here is to determine the highest undervolt that the CPU can tolerate stably.**

## Lowering Temperature Limit

This is the more stable method with possible performance penalty. It will, however, guarantee that the CPU will not go above a set temperature.

To set the upper limit to 60C, run:

```bash
~ 
❯ sudo undervolt --temp 60
```

Then rerun `s-tui`.

<figure>
  <img src="/static/images/2024-04-29/stress-temp.png" alt="s-tui" loading="lazy"/>
  <figcaption>The maximum temperature reached is now 60C, but average frequency has dropped to 1600MHz to compensate<figcaption/>
</figure>


[cleaning the fans and changing the thermal paste]: https://www.instructables.com/How-to-Clean-Laptop-Fan-and-Apply-Thermal-Paste-on/
[undervolt]: https://github.com/georgewhewell/undervolt
