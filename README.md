# Fan-control for Penta-Sata Tower

## History
extension was developed for [Penta-Sata-Towers](https://wiki.radxa.com/Penta_SATA_HAT)
with rockpi4 running [LibreELEC](https://libreelec.tv/).
Original driver from radxa uses propietary port of pigpio, which I could not
port it to LE. Furthermore LibreELEC (LE) does not provide a real shell, but
uses busybox. Busybox does not contain support for arrays in shellscripts,
nor does it support any real scripting language.

Therefore I had to write some python scripts, that work with the tools
provided by LE.

**Note:** uses legacy sysfs - but sysfs works with current linux-kernels if enabled.

One remaining problem is, that dtb overlays don't work for rockpi4 on LE.
Using overlays break boot process.

When the driver was ready and running, I found out, that it has no dependencies,
so that it may run on any linux system.
**That's the good news.**
_The bad news:_ any linux has its own dtb-handling - each of them
    (of cause) incompatible with others.

## Preparation

* **debian/ubuntu** use `/boot/hw_intfc.conf` to configure hardware modules.
  Search for lines like:
  - `intfc:pwm0=on/off`
  - `intfc:pwm1=on/off`
  If both values are set to *on* you're fine. If not, change them to **on**.
* **armbian** uses overlays at `/boot/dtb/rockchip/overlay`, but does not
  provide an overlay for pwm modules.
  Provided overlay was written by [PetrozPL](https://forum.armbian.com/topic/15341-rock-pi4-pwm-control-no-overlay/?do=findComment&comment=109579)
  compile it with:
  ```
  dts -O dtb -o rockchip-pwm-gpio.dtbo -b -0 -@ rockchip-pwm-gpio.dts
  ```
  and copy it to `/boot/dtb/rockchip/overlay`
  Enable that overlay by changing `/boot/armbianEnv.txt`
  Look for a line like: `overlay_prefix=rockchip`
  Add a line after that line: `overlays=pwm-gpio`

* **libreELEC**
  LE does not support dtb-overlays, nor does it support configurable
  hardware modules.
  So you have to patch the original dtb file:
  1. copy existing dtb from /flash to some place where you have space and
     write permission. Could be on LE, but does not need to (scp is your friend)

  2. decompile dtb into source with this command (my dtb is rk3399-rock-pi-4a.dtb):
      dtc -I dtb -O dts -o rk3399-rock-pi-4a.dts rk3399-rock-pi-4a.dtb

  3. load dts file in your favorite editor and search for "pwm@ff42" and you'll
     find several matching sections like this:
```
       pwm@ff420000 {
            compatible = "rockchip,rk3399-pwm\0rockchip,rk3288-pwm";
            reg = < 0x00 0xff420000 0x00 0x10 >;
            #pwm-cells = < 0x03 >;
            pinctrl-names = "default";
            pinctrl-0 = < 0x85 >;
            clocks = < 0x76 0x1e >;
            clock-names = "pwm";
            status = "disabled";
            phandle = < 0xf6 >;
            };

       pwm@ff420010 {
            compatible = "rockchip,rk3399-pwm\0rockchip,rk3288-pwm";
            reg = < 0x00 0xff420010 0x00 0x10 >;
            #pwm-cells = < 0x03 >;
            pinctrl-names = "default";
            pinctrl-0 = < 0x86 >;
            clocks = < 0x76 0x1e >;
            clock-names = "pwm";
            status = "disabled";
            phandle = < 0xf7 >;
            };
```

  4. replace line _status = "disabled"_ with line _status = "okay"_

  5. save file and exit editor

  6. copy file back to LE - to a writable directory

  7. compile dts file (on your LE) into dtb with this command:
      `dtc -O dtb -o rk3399-rock-pi-4a.dtb -b O -@ rk3399-rock-pi-4a.dts`

  8. copy compiled binary to /flash overwriting the original dtb file

* **slackware**
  slackware does not have overlay support, so try to follow instructions from LE
  Instead of `/flash` use `/boot`

**Note:** changes at dtb require reboot to become active

## Installation

* after preparing system run `sudo make install`

* Beside fan-control, this package provides support for the top-panel button.
  Three states are recognized:
  - **click** - default is toggle control between temperature based control
                and fan running at fullspeed
  - **double-click** - default reboots the system
  - **(long) pressed** - default shutdown to poweroff

## Customization

* if you like to change temperature-based fan-speed or change the button functions
  look at `/etc/rockpi-sata.conf`

## Update

* fanctl has been modified to be able to use [TempLogger](https://github.com/movinator/TempLogger)
  to reduce system load, if system runs [conky.arcs](https://github.com/movinator/conky.arcs) too.

Have fun
