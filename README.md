<p align="center">
  <img src="tretlager/data/icons/de.linuxundich.Tretlager.svg" alt="Tretlager icon" width="128" height="128">
</p>

<h1 align="center">Tretlager</h1>

<p align="center"><strong>Zwift on Linux, set up in five steps.</strong></p>

<p align="center">
  Tretlager installs the official Windows version of Zwift on your Linux computer, signs you in and
  connects your smart trainer and heart rate strap over Bluetooth. No terminal, no Wine tinkering,
  no phone needed. If you prefer, the Zwift Companion app can hold the sensors instead. One button
  starts the ride.
</p>

<p align="center">
  <a href="https://github.com/freiversum/tretlager/releases/latest"><strong>Download Flatpak</strong></a>
  &nbsp;·&nbsp; Flathub: not planned &nbsp;·&nbsp;
  <a href="https://linuxundich.de/en/projects/tretlager/">Project page</a>
  &nbsp;·&nbsp;
  <a href="docs/HARDWARE.md">Tested hardware</a>
  &nbsp;·&nbsp;
  <a href="CHANGELOG.md">Changelog</a>
</p>

<p align="center">
  <img src="docs/screenshots/tretlager-ride.webp" alt="Tretlager shows live power, cadence and heart rate while Zwift runs in the background" width="100%">
</p>

> [!WARNING]
> **Not an official Zwift app, use at your own risk.** Tretlager is a private project. Zwift does not
> support Linux and has nothing to do with Tretlager. The sign-in happens outside the Zwift
> launcher, which contradicts Zwift's terms of service.
>
> **With the sensor bridge:** Zwift may not be happy that a software bridge sends data to Zwift
> that could be manipulated; restrictions up to a suspended account, including the XP and drops
> you earned, cannot be ruled out. **Not for races:** there is no guarantee that the bridge passes
> power, cadence and heart rate to Zwift correctly.
>
> **With the Zwift Companion app** instead of the bridge, Zwift's own app delivers power, cadence
> and heart rate, and the two notes on the bridge do not apply.
>
> Tretlager shows these points before the first start and only goes on once you accept them.

## See it in action

<table>
<tr>
<td valign="middle">

From the first start to the finish line: Tretlager checks the system, installs Wine and Zwift by
itself, signs in, pairs a trainer and a heart rate strap and starts Zwift on the NVIDIA graphics
card. Zwift then finds the sensors through the bridge, and Tretlager keeps watch during the ride.

[**Watch the demo**](docs/tretlager-demo.mp4) (3:43, MP4, 43 MB). The rider data in the video is
simulated, everything else is real.

</td>
<td width="55%">
<a href="docs/tretlager-demo.mp4"><img src="docs/screenshots/demo-poster.webp" width="100%" alt="Play the Tretlager demo video"/></a>
</td>
</tr>
</table>

## What it does

<table>
<tr>
<td width="33%" valign="top">

### A setup assistant instead of a wiki page

Getting Zwift to run under Wine usually means a long list of commands, .NET installers and
registry tweaks. Tretlager turns that into a guided setup. It checks graphics, Bluetooth, disk
space and network first, without changing anything, and tells you what is missing.

</td>
<td width="33%" valign="top">

### Installs Zwift by itself

Tretlager brings its own Wine and downloads the official Zwift installer straight from Zwift,
verifies its signature and sets up fonts, .NET 4.8 and WebView2. Then the Zwift launcher fetches
the 5 GB game. Tretlager shows the progress and needs about 15 minutes on a normal connection.
Zwift's own files stay untouched.

</td>
<td width="33%" valign="top">

### Signs you in

The sign-in page of the Zwift launcher does not work under Wine. Tretlager opens Zwift's own
sign-in page in a private window instead and keeps the session in your desktop's keyring
(KWallet or GNOME Keyring). You type your password into Zwift's page, never into Tretlager. This step is optional and only happens after
you agree.

</td>
</tr>
</table>

<p align="center">
  <img src="docs/screenshots/tretlager-welcome.webp" alt="Welcome page with requirements and the important notes" width="32%">
  <img src="docs/screenshots/tretlager-system-check.webp" alt="System check: system, graphics, hybrid graphics, Bluetooth, Avahi, disk space, internet, Wine and Zwift" width="32%">
  <img src="docs/screenshots/tretlager-setup.webp" alt="Setup page: installer verified, Wine environment, Microsoft components and launcher done, game download in progress" width="32%">
</p>

<table>
<tr>
<td width="55%">
<img src="docs/screenshots/tretlager-sensors.webp" alt="Sensors page: nearby trainers and straps, paired sensors with live values, bridge settings and troubleshooting" width="100%">
<img src="docs/screenshots/zwift-paired-devices.webp" alt="Zwift's Paired Devices screen with power, resistance, cadence and heart rate all connected through the bridge" width="100%">
</td>
<td valign="middle">

### Your sensors, without a phone

Wine cannot talk to Bluetooth sensors, and the Zwift Companion app is no fun on Linux. The
Tretlager sensor bridge connects to your smart trainer and heart rate strap over Bluetooth LE and
offers them to Zwift on the same computer, the way a Wahoo trainer with Direct Connect would. In
Zwift you simply pick "Wahoo KICKR …" and "Wahoo HRM …". ERG mode and climbs work, the trainer
gets harder when the road goes up.

Pause a sensor you don't need today, pick a USB Bluetooth adapter if the built-in chip is
unreliable, or let the bridge serve Zwift on another device in your network.

### Or through the Zwift Companion app

If you would rather keep Tretlager out of the path of your power data, choose *Zwift Companion
app* under *Sensors*. The phone then connects to trainer and heart rate strap, and Zwift fetches
them from the app over your local network, exactly as on Windows. The sensor bridge stays off and
the computer needs no Bluetooth at all. Phone and computer have to be on the same network.

</td>
</tr>
</table>

<table>
<tr>
<td valign="middle">

### One button to ride

The overview shows your sensors, the Zwift version, the graphics card, Wine and the sign-in at a
glance. "Start Zwift" runs the game on the dedicated NVIDIA card of a hybrid laptop and keeps the
screen resolution; on Plasma it also maximises the window. Tretlager waits in the background,
shows live values and tidies up after the ride. A menu entry "Zwift (Tretlager)" starts the ride
directly from the application launcher.

</td>
<td width="55%">
<img src="docs/screenshots/tretlager-ready.webp" alt="Overview before the ride: ready to ride, both sensors connected, Zwift up to date, NVIDIA GeForce RTX 3050 Ti" width="100%">
</td>
</tr>
</table>

<table>
<tr>
<td width="55%">
<img src="docs/screenshots/tretlager-warning.webp" alt="The warning dialog before the first start: not an official Zwift app, at your own risk, not for races, sign-in outside the launcher" width="100%">
</td>
<td valign="middle">

### Stays out of trouble

- Before every start Tretlager brings the Zwift environment in line and lets the Zwift launcher
  install game updates.
- A new Wine version comes with a new Tretlager version. The last working one is kept, and a
  switch brings it back if Zwift misbehaves.
- Tretlager warns when the laptop runs on battery or the power supply changes during a ride,
  and when Bluetooth headphones on the bridge's adapter crowd out the sensors.
- While Zwift starts and runs, the screen stays on, also during a break without mouse or keyboard.
- During a Zwift update the overview shows the download progress.
- *Save error report…* writes a ZIP with the logs; tokens, passwords and email addresses are removed.
- Help pages and troubleshooting tips are built in. The interface speaks English and German.

</td>
</tr>
</table>

## At a glance

| | |
|---|---|
| **Runs on** | Linux with Flatpak; TUXEDO OS with Plasma is the main target, GNOME works |
| **Your system provides** | BlueZ with a Bluetooth LE adapter, `avahi-daemon` and a Secret Service keyring (KWallet or GNOME Keyring); Tretlager brings its own Wine |
| **Works with** | Bluetooth LE trainers and heart rate straps (FTMS, Cycling Power, Cycling Speed and Cadence, Heart Rate), or the Zwift Companion app; no ANT+ |
| **Account** | your Zwift account, signed in on Zwift's own page |
| **Languages** | English and German |
| **Licence** | [GPL-3.0-or-later](LICENSE) |

## Install

> [!NOTE]
> Tretlager targets current distributions with Flatpak. TUXEDO OS with Plasma is the main
> target, GNOME works. Ubuntu 26.04 (GNOME) was tested with the Debian package, the Flatpak is
> untested there. Fedora and openSUSE are planned but untested; reports are welcome.

Your system needs Flatpak with the Flathub remote, BlueZ with a Bluetooth LE adapter, a running
`avahi-daemon` and a Secret Service keyring (KWallet or GNOME Keyring). Tretlager brings
everything else, including its own Wine.

### Flatpak bundle from GitHub

1. Download `tretlager-<version>-x86_64.flatpak` from the
   [latest release](https://github.com/freiversum/tretlager/releases/latest).
2. Install it:

   ```sh
   flatpak install --user tretlager-*.flatpak
   ```

### Build it yourself

```sh
git clone https://github.com/freiversum/tretlager.git
cd tretlager
build-aux/flatpak/build.sh
```

The first build compiles Wine and takes a while (about 15 minutes on 20 cores).

Flatpak fetches the KDE 6.11 runtime from Flathub if it is missing, and on NVIDIA systems the
matching driver extension. Start Tretlager from the application menu and follow the assistant;
setting up Wine and downloading Zwift takes about 15 minutes.

> [!TIP]
> Bundles don't update themselves, so check the Releases page for new versions and install the
> new bundle the same way.

To remove Tretlager including the Zwift installation (about 10 GB), run
`flatpak uninstall --delete-data de.linuxundich.Tretlager`. Sign out in Tretlager first to remove
the Zwift session from your keyring.

## Why Linux, why now

Windows 10 no longer gets updates, and plenty of the computers that only ever run Zwift cannot
officially run Windows 11. Zwift has already dropped support for Windows 8, and Windows 10 will
probably follow at some point. Then it is either upgrading the hardware or switching to Linux. That
is where Tretlager comes in: the old computer can stay, only the system underneath changes.

## How it works

1. Tretlager runs as a Flatpak with its own Wine (built from source, WoW64) and everything else
   Zwift needs. Your system only provides Bluetooth, Avahi and a keyring.
2. Zwift is the unmodified Windows game from Zwift's servers. It renders with OpenGL through
   XWayland, on NVIDIA via PRIME offload.
3. The sensor bridge talks to BlueZ on one side and speaks Wahoo's Direct Connect protocol
   (DIRCON) to Zwift on the other, announced over mDNS on the local machine.
4. Experimental: the *Watch remote* page lets a Garmin watch running the Wristpilot app steer Zwift
   (turns, Ride On, power-up). Tretlager offers a Bluetooth LE service for the watch and types
   Zwift's keyboard shortcuts into the game window, or – with the optional Companion link – talks to
   the game like the Zwift Companion app and shows junctions and power-ups on the watch. Off by
   default; the watch app is not published yet.

No telemetry, no changed Zwift files, no bypassing of sign-in or licence checks. Network traffic
goes only to Zwift, to GitHub for winetricks and to the download sources of winetricks (Microsoft
fonts, .NET and WebView2) during setup.

The interface uses Kirigami and Kirigami Addons on PySide6, the bridge uses
[Bleak](https://github.com/hbldh/bleak). [qdomyos-zwift](https://github.com/cagnulein/qdomyos-zwift)
served as the reference for the DIRCON protocol.

## Tested hardware

Tretlager is tested on two laptops with one smart trainer and two heart rate straps. Details, versions and
known quirks are in [docs/HARDWARE.md](docs/HARDWARE.md).

| | Main system | Second system |
|---|---|---|
| Computer | TUXEDO InfinityBook Pro Gen7, Intel Core i7-12700H, 32 GB RAM | Dell XPS 15 9560, Intel Core i7-7700HQ, 16 GB RAM |
| Graphics | Intel Iris Xe + NVIDIA GeForce RTX 3050 Ti Laptop (driver 580.178.04) | Intel HD Graphics 630 + NVIDIA GeForce GTX 1050 Mobile (driver 580.196.07) |
| System | TUXEDO OS (Debian forky base), KDE Plasma 6.7 on Wayland | Arch Linux, GNOME 51 on Wayland |
| Bluetooth | Intel AX201, TP-Link UB500 USB adapter | Qualcomm Atheros QCA61x4 |

| Sensor | Connection | Status |
|---|---|---|
| Wahoo KICKR V4 smart trainer | Bluetooth LE (FTMS, Cycling Power) | power, cadence, ERG mode and climbs work |
| Wahoo TICKR heart rate strap | Bluetooth LE (Heart Rate) | works |
| Garmin HRM-Pro Plus heart rate strap | Bluetooth LE (Heart Rate) | works with the Intel AX201 and the TP-Link UB500; ends its connection by itself every 7–15 minutes and reconnects after a few minutes |

Other trainers and straps that use the standard Bluetooth services (FTMS, Cycling Power, Cycling
Speed and Cadence, Heart Rate) should work but are untested. ANT+ is not supported.

## More

- [Tested hardware and software](docs/HARDWARE.md) in detail
- [Project page on my blog](https://linuxundich.de/en/projects/tretlager/) · [Changelog](CHANGELOG.md) · [Backlog](BACKLOG.md)
- [Technical notes](docs/technical-notes.md): requirements, everyday use, troubleshooting, development
- Background: [feasibility study](FEASIBILITY.md), [UX concept](docs/ux-concept.md),
  [Flatpak plan](docs/flatpak.md), [updates](docs/updates.md),
  [QA audit](docs/qa-audit-2026-10-30.md)
- Found a bug or tested other hardware? [Open an issue](https://github.com/freiversum/tretlager/issues)

## On the blog

Tretlager has its own page on my blog
[Linux und Ich](https://linuxundich.de/en/projects/tretlager/), with more
details on the app and news about upcoming versions. The
[project overview](https://linuxundich.de/en/projects/) lists everything else
I build for the Linux desktop. Questions, ideas or feedback that don't fit
into an issue? [Get in touch](https://linuxundich.de/en/contact/), I read
every message.

## Use of AI

Tretlager is AI-assisted. Most of the code, the icon and the translations were written with AI
assistance, directed by me: I set the requirements, made the design decisions, reviewed the
results and tested everything on my own trainer, heart rate straps and laptops. Commits written
with AI assistance carry a `Co-Authored-By` line.

Tretlager is free software under the [GPL-3.0-or-later](LICENSE). It is a personal project,
not affiliated with or endorsed by Zwift, Inc. Zwift is a trademark of Zwift, Inc.; Wahoo, KICKR
and TICKR are trademarks of Wahoo Fitness; Garmin and HRM-Pro are trademarks of Garmin Ltd. Names
of other riders in the screenshots are blurred.
