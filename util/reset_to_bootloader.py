#!/usr/bin/env python3
"""Send System76 CMD_RESET (6) to the Launch Heavy 3 raw HID interface.

The keyboard must already be unlocked (FN + QK_BOOT, LEDs show the unlock effect).
Run with sudo: sudo python3 reset_to_bootloader.py
"""
import glob
import os
import sys

VID_PID = "00003384:0000000A"
RAW_USAGE_PAGE = bytes([0x06, 0x60, 0xFF])  # Usage Page 0xFF60
CMD_RESET = 6


def find_raw_hidraw():
    for sys_dir in sorted(glob.glob("/sys/class/hidraw/hidraw*")):
        with open(os.path.join(sys_dir, "device/uevent")) as f:
            if VID_PID not in f.read():
                continue
        with open(os.path.join(sys_dir, "device/report_descriptor"), "rb") as f:
            if RAW_USAGE_PAGE in f.read():
                return "/dev/" + os.path.basename(sys_dir)
    return None


path = find_raw_hidraw()
if path is None:
    sys.exit("Raw HID interface not found")
print("Using", path)

packet = bytes([CMD_RESET]) + bytes(31)
fd = os.open(path, os.O_RDWR)
os.write(fd, packet)
resp = os.read(fd, 32)
os.close(fd)

if resp[1] == 0:
    print("OK: keyboard is rebooting into the bootloader (RPI-RP2 drive)")
else:
    sys.exit("Keyboard refused: it is not unlocked (press FN + QK_BOOT first)")
