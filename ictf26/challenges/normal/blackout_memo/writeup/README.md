# Blackout Memo — Writeup

**Category:** Forensics  
**Flag:** `ictf{nice_black_box_try_again}`

---

## Overview

We're given `confidential_email.pdf`, a memo that has been "redacted" by placing a black rectangle over a portion of its content. The goal is to recover what's underneath.

---

## The Vulnerability

**Redaction ≠ deletion.**

In many PDF editors, drawing a black shape over content is purely a visual overlay. The original data (text, images, embedded objects) is still present in the PDF file structure — it's just covered by an opaque rectangle on the rendered page.

PDF files are made up of objects (streams, dictionaries, images) that are rendered in layers. A black box drawn on top does nothing to remove the underlying objects from the file.

---

## Solution

### Option 1 — Extract embedded images with `pdfimages`

```bash
pdfimages confidential_email.pdf images/
ls images/
# images/image-000.ppm  ← the original image, unredacted
```

The extracted image file will contain the content that was hidden behind the black box, including the flag.

### Option 2 — Use `mutool extract`

```bash
mutool extract confidential_email.pdf
# extracts all embedded streams and images from the PDF
```

### Option 3 — Raw string search

```bash
strings confidential_email.pdf | grep -i ictf
```

Depending on how the PDF was generated, the flag may appear as a literal string in the file.

---

## Flag

`ictf{nice_black_box_try_again}`
