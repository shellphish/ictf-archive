# Evil Model

**Edition:** iCTF 2023 (High School Track)
**Category:** misc
**Points:** 500

## Description

Supersecure Bank, with an advanced malicious file detection system, uses AI from a company called SuperAI. A bad hacker at SuperAI found a way to embed malware into a trained AI model, bypassing Supersecure Bank's detection.
Later, a bad hacker from the same group at Supersecure Bank extracted the malware from the shipped AI model and executed it.
The code, model architecture, and weights are provided. Find the hidden flag in the model.

Hint -
* Hidden things are in the hidden layer when the last three digits are less significant.
* The method that you can hide bytes without significantly damaging the model performance is the key to extracting the flag.
* Read more - https://arxiv.org/abs/2107.08590

## Files

| File | Description |
|------|-------------|
| `attachments/model_architecture.json` | Challenge file |
| `attachments/model_weights.json` | Challenge file |
| `attachments/test.jpg` | Challenge file |
| `attachments/test.py` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
