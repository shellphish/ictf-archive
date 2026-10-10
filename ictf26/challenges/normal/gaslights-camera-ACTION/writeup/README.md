# Gaslights, Camera, ACTION — Writeup

**Category:** Forensics  
**Flag:** `ictf{wh0_w1ll_writ3_y0ur_l3tt3r}`

---

## Overview

We're given `iCTF_Planning_Document_2026_FINAL.pdf`, supposedly the "original" CTF planning document that Dr. Light provided as proof he sent it months ago. The flag is hidden somewhere inside the PDF.

---

## Solution

### Option 1 — Extract text directly

```bash
pdftotext iCTF_Planning_Document_2026_FINAL.pdf -
```

Read through the extracted text carefully. The flag may appear in a text layer that is not visible when viewing the PDF normally (e.g., white text on white background, text behind an image, or in a hidden annotation).

### Option 2 — String search

```bash
strings iCTF_Planning_Document_2026_FINAL.pdf | grep -i "ictf{"
```

PDF files store their content as streams of objects. A raw string search often finds flags embedded as literal text even when they're not visible in a PDF viewer.

### Option 3 — Extract all objects

```bash
mutool extract iCTF_Planning_Document_2026_FINAL.pdf
# inspect all extracted streams and images
```

### Option 4 — Read metadata

```bash
exiftool iCTF_Planning_Document_2026_FINAL.pdf
```

Metadata fields (Author, Subject, Keywords, Comments) are sometimes used to hide flags.

---

## Key Insight

PDF documents can contain text that is invisible when rendered — it may be covered by another element, match the background color, or exist in an annotation/form field. Tools that work on the raw file structure (`strings`, `mutool`, `pdftotext`) bypass the rendered view and expose all content.

---

## Flag

`ictf{wh0_w1ll_writ3_y0ur_l3tt3r}`
