# Lost Album

**Edition:** iCTF 2023 (Undergrad Track)
**Category:** misc
**Points:** 500

## Description

I had a nice album with photos of all of my friends and family. I remember at one point I scanned each of these photos and trained a smile detection model as part of 
a course in my undergrad. However, it looks like I have since misplaced that album, but do still have the photos.
I remember some of the pockets in the album had watermarks on them.

Specifically, every 3 in 4 pages (so 75% probability) had a watermark on it. I don't remember what the watermark was, but I do remember that
it was 3-digits long and a combination of letters (lower and upper case). I only have the model and the original photos with me.

Given this ML model and the original images, can you help me find out what the watermark was?
The watermark itself is a 3-letter combination of letters. If you can recover any 2 of these 3 characters, that will be your flag.

Submit the watermark in the format ictf{}
E.g. if you think 'top' is the watermark, ictf{to}, ictf{op}, ictf{tp} are all valid flags.

If it helps, I have also attached the file used for training, so that you know what font and size the watermark is.

## Files

| File | Description |
|------|-------------|
| `attachments/train.py` | Challenge file |
| `attachments/model.pth` | Challenge file |
| `attachments/images.tar.gz` | Challenge file |
| `attachments/Times_New_Roman.ttf` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
