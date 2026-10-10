# MysteriousModel

**Edition:** iCTF 2024 (High School Track)
**Category:** machine-learning
**Points:** 136

## Description

One day, you found a mysterious device with a camera attached. You figured out that this device takes pictures of grayscale (28x28 pixels) hand-written digits and classifies them using a convolutional neural network model into six different classes. Your task is to find out which six digits this mysterious model is supposed to classify (i.e., the digits that correspond to each of the model's output logits). You're given four files for this challenge - [1::mysterious_model.pth], the PyTorch model that you need to reverse engineer [2::images.npy], a collection of 100 images of digits (10 images per digit) that you can test the model with (a 100x28x28 numpy array) - [3::labels.npy], the labels (zero to nine) for the given 100 test images (a 100-dimensional numpy array) [4::architecture.py], a Python script containing the model's architecture definition (in PyTorch), a utility function (load_model) to load the model into memory for testing, and a utility function (display_image) to display individual images in the provided data. For this challenge, you need to create a Python environment with PyTorch (see https://pytorch.org/get-started/locally to get started) and Matplotlib (https://pypi.org/project/matplotlib/). You can easily solve this challenge only using a CPU (you won't need a GPU). Let's say the model's six output logits correspond to digits 3,7,1,2,5,9 (e.g., the first logit is for digit 3, the second logit is for digit 7, and so on). The flag will be 'ictf{3,7,1,2,5,9}' (no quotes).

## Files

| File | Description |
|------|-------------|
| `attachments/mysterious_model.pth` | Challenge file |
| `attachments/architecture.py` | Challenge file |
| `attachments/images.npy` | Challenge file |
| `attachments/labels.npy` | Challenge file |

## Writeup

See [`writeup/`](writeup/).
