# Bits of Scan-dalous QRiosity Part 2 — Writeup

**Category:** Forensics  
**Flag:** `iCTF={umustQRsickQRcodesorLSBware!}`

---

## Overview

We're given `CueAres.zip`, which contains multiple images of the same scene. The challenge description mentions **image stacking** to remove noise/outliers, followed by **LSB steganography** to extract a hidden message (likely a QR code).

---

## Step 1 — Extract the images

```bash
unzip CueAres.zip -d frames/
ls frames/
```

---

## Step 2 — Stack the images (median filter)

Multiple frames of the same scene are provided. Random noise differs frame-to-frame while the hidden signal stays constant. **Median stacking** removes outliers (noise) and keeps the stable signal.

```python
from PIL import Image
import numpy as np
import os

frames_dir = "frames/"
files = sorted(f for f in os.listdir(frames_dir) if f.endswith(".png"))

arrays = [np.array(Image.open(os.path.join(frames_dir, f)).convert("RGB")) for f in files]
stacked = np.median(arrays, axis=0).astype(np.uint8)

result = Image.fromarray(stacked)
result.save("stacked.png")
```

---

## Step 3 — Extract LSB steganography

After stacking, extract the least significant bit of the red channel from every pixel and reconstruct the hidden image:

```python
from PIL import Image
import numpy as np

img = np.array(Image.open("stacked.png").convert("RGB"))
h, w, _ = img.shape

# Extract LSB of red channel → reconstruct 1-bit image
lsb_plane = (img[:, :, 0] & 1) * 255
hidden = Image.fromarray(lsb_plane.astype(np.uint8), mode="L")
hidden.save("hidden.png")
```

---

## Step 4 — Decode the QR code

Opening `hidden.png` reveals a QR code. Decode it:

```bash
zbarimg hidden.png
# or
python3 -c "
import cv2
img = cv2.imread('hidden.png')
detector = cv2.QRCodeDetector()
data, _, _ = detector.detectAndDecode(img)
print(data)
"
```

The decoded QR code contains the flag.

---

## Flag

`iCTF={umustQRsickQRcodesorLSBware!}`
