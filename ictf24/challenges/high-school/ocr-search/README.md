# OCR Search

**Edition:** iCTF 2024 (High School Track)
**Category:** programming
**Points:** 50

## Description

Hard-coded text in video information is not uncommon in the increasingly vast digital landscape. However, for long-form videos, it can be tiresome to watch an entire video to get its content. Further, extracting information from the audio channel of some videos can be unreliable, due to accents, foreign languages, in more.
In this challenge, you will extract the encoded text information in a long-form video file using Optical Character Recognition (OCR). OCR is a process whereby text is recognized and extracted from images/videos using computer vision, which can be outputted to a file. Once you have extracted the text information, search the file for the word "flag", and the flag will be directly written (and stated) in the same sentence.
Hints: - Although you can implement your own OCR approach, or use a library, there exist many video subtitle extractor tools and GitHub repositories that provide an all-in-one solution to get you started. - You may also consider using audio recognition approaches to transcribe the audio channel (e.g., with pyTranscriber), which may be faster, but much less accurate. - In order to speed up OCR on video, you may consider dropping the framerate of the video (e.g., using ffmpeg) in order to reduce OCR operations on redundant frames.

## Files

| File | Description |
|------|-------------|
| `attachments/movie.mp4` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
