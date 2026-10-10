# encrypted_ai

**Edition:** iCTF 2024 (Undergrad Track)
**Category:** machine-learning
**Points:** 212

## Description

A student has designed a PyTorch model and embedded a hidden flag within it. To add a layer of security, he encrypted the model using XOR encryption with a random 16-byte key before sharing it with his friends. However, the student forgot to save both the encryption key and the unencrypted model, making the task of revealing the hidden flag a puzzle.\n\nYour challenge is to recover the encryption key and decrypt the model to unveil the concealed information. The encrypted model file is provided i.e., `model_encrypted.pth`.\n\nGood luck, and happy decrypting!

## Files

| File | Description |
|------|-------------|
| `attachments/model_encrypted.pth` | Challenge file |
| `attachments/README.md` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
