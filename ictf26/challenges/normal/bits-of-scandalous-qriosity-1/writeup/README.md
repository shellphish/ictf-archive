# Bits of Scan-dalous QRiosity Part 1 — Writeup

**Category:** Forensics  
**Flag:** `iCTF={PixlsRez2c&NOTc}`

---

## Overview

We're given a single PNG image (`1obfus.png`) and told a flag is hidden inside.
The challenge description mentions pixel-by-pixel manipulation and steganography — a clear hint at **LSB (Least Significant Bit) steganography**.

---

## The Technique

In LSB steganography, the least significant bit of each color channel (R, G, B) of every pixel is modified to encode a hidden message. Since changing one bit shifts the color value by at most 1, the difference is invisible to the human eye.

To recover the hidden data:
1. Read each pixel's RGB values
2. Extract the LSB from one (or more) channels
3. Reassemble the bits into bytes → the hidden message

---

## Solution

```python
from PIL import Image

img = Image.open("1obfus.png").convert("RGB")
pixels = list(img.getdata())

bits = []
for r, g, b in pixels:
    bits.append(r & 1)

# Group bits into bytes
chars = []
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) < 8:
        break
    chars.append(chr(int("".join(str(b) for b in byte), 2)))

message = "".join(chars)
# Find the flag
idx = message.find("iCTF=")
print(message[idx:idx+30])
```

Running the script extracts the hidden text from the red channel LSBs.

---

## Flag

`iCTF={PixlsRez2c&NOTc}`
