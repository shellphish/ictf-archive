from torchvision import transforms, models
import torch
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter1d
import random

import json
import argparse
from pathlib import Path


SQUEEZENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
SQUEEZENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def preprocess(img, size=224):
    transform = transforms.Compose(
        [
            transforms.Resize(size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=SQUEEZENET_MEAN.tolist(), std=SQUEEZENET_STD.tolist()
            ),
            transforms.Lambda(lambda x: x[None]),
        ]
    )
    return transform(img)


def deprocess(img, should_rescale=True):
    transform = transforms.Compose(
        [
            transforms.Lambda(lambda x: x[0]),
            transforms.Normalize(mean=[0, 0, 0], std=(1.0 / SQUEEZENET_STD).tolist()),
            transforms.Normalize(mean=(-SQUEEZENET_MEAN).tolist(), std=[1, 1, 1]),
            transforms.Lambda(rescale)
            if should_rescale
            else transforms.Lambda(lambda x: x),
            transforms.ToPILImage(),
        ]
    )
    return transform(img)


def rescale(x):
    low, high = x.min(), x.max()
    x_rescaled = (x - low) / (high - low)
    return x_rescaled


def blur_image(X, sigma=1):
    X_np = X.cpu().clone().numpy()
    X_np = gaussian_filter1d(X_np, sigma, axis=2)
    X_np = gaussian_filter1d(X_np, sigma, axis=3)
    X.copy_(torch.Tensor(X_np).type_as(X))
    return X


def load_image(filename):
    img = Image.open(filename).convert("RGB")
    return img


def create_dark_pixel_mask(img):
    preprocess_no_normalize = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),  # Values between 0 and 1
        ]
    )
    img_tensor_no_norm = preprocess_no_normalize(img)  # shape [3, 224, 224]

    # Identify dark pixels
    dark_pixels = (img_tensor_no_norm < 0.2).type(
        torch.FloatTensor
    )  # shape [3, 224, 224]
    dark_pixel_mask = dark_pixels.sum(dim=0) == 3  # shape [224, 224]

    # Expand the mask to match image dimensions
    dark_pixel_mask = dark_pixel_mask.unsqueeze(0).expand(
        3, -1, -1
    )  # shape [3, 224, 224]
    return dark_pixel_mask


def jitter(X, ox, oy):
    """
    Helper function to randomly jitter an image.

    Inputs
    - X: PyTorch Tensor of shape (N, C, H, W)
    - ox, oy: Integers giving number of pixels to jitter along W and H axes

    Returns: A new PyTorch Tensor of shape (N, C, H, W)
    """
    if ox != 0:
        left = X[:, :, :, :-ox]
        right = X[:, :, :, -ox:]
        X = torch.cat([right, left], dim=3)
    if oy != 0:
        top = X[:, :, :-oy]
        bottom = X[:, :, -oy:]
        X = torch.cat([bottom, top], dim=2)
    return X


def create_class_visualization(
    target_y,
    model,
    dtype,
    l2_reg=1e-3,
    learning_rate=25,
    num_iterations=500,
    blur_every=10,
    max_jitter=16,
    show_every=100,
    output_directory=".",
):
    model.type(dtype)

    img = load_image("data/material.png")
    img_tensor = preprocess(img).type(dtype).requires_grad_(True)

    orig_img_tensor = img_tensor.clone()

    # Create the dark pixel mask
    dark_pixel_mask = create_dark_pixel_mask(img).unsqueeze(0).type(dtype)
    # print the number of dark pixels
    print(f"Number of dark pixels: {dark_pixel_mask.sum()}")
    non_dark_mask = (1 - dark_pixel_mask).type(dtype)

    for t in range(num_iterations):
        ox, oy = random.randint(0, max_jitter), random.randint(0, max_jitter)
        img_tensor.data.copy_(jitter(img_tensor.data, ox, oy))

        img_tensor.grad = None

        scores = model(img_tensor)
        target_score = scores[:, target_y] - l2_reg * torch.norm(img_tensor)
        target_score.backward()

        # Only update the dark portions of the image
        img_tensor.grad.data *= dark_pixel_mask

        with torch.no_grad():
            img_tensor += learning_rate * img_tensor.grad / img_tensor.grad.norm()

        img_tensor.data.copy_(jitter(img_tensor.data, -ox, -oy))

        if t % blur_every == 0:
            blur_image(img_tensor.data, sigma=0.5)

        for c in range(3):
            lo = float(-SQUEEZENET_MEAN[c] / SQUEEZENET_STD[c])
            hi = float((1.0 - SQUEEZENET_MEAN[c]) / SQUEEZENET_STD[c])
            img_tensor.data[:, c].clamp_(min=lo, max=hi)

        with torch.no_grad():
            # Reset the non-dark pixels to the original image
            img_tensor.data = (
                img_tensor.data * dark_pixel_mask + orig_img_tensor.data * non_dark_mask
            )

        # Just a sanity check
        if not torch.equal(
            img_tensor.data * non_dark_mask, orig_img_tensor.data * non_dark_mask
        ):
            raise Exception("Non-dark pixels are not the same!")

        if t == 0 or (t + 1) % show_every == 0 or t == num_iterations - 1:
            intermediate_img_path = (
                Path(output_directory) / f"generated_image_iter{t}.png"
            )
            deprocess(img_tensor.data.clone().cpu()).save(intermediate_img_path)
            predicted_class = model(img_tensor).argmax()
            predicted_class_name = get_class_name(str(predicted_class.item()))
            print(
                f"Saved intermediate image at {intermediate_img_path}. Current prediction: {predicted_class} ({predicted_class_name})"
            )
            if predicted_class == target_y:
                break

    return deprocess(img_tensor.data.cpu())


def get_class_name(class_index: int) -> str:
    with open("data/imagenet_classes.json") as f:
        class_names = json.load(f)
    return class_names[class_index]


def parse_args():
    parser = argparse.ArgumentParser(description="Create class visualizations")

    parser.add_argument(
        "--output-directory",
        type=str,
        default=".",
        help="The directory to save the generated images",
    )

    return parser.parse_args()


def main():
    target_y = 967  # espresso
    dtype = torch.FloatTensor
    model = models.squeezenet1_1(
        weights=models.squeezenet.SqueezeNet1_1_Weights.IMAGENET1K_V1
    )
    args = parse_args()
    out = create_class_visualization(
        target_y,
        model,
        dtype,
        num_iterations=5000,
        show_every=100,
        output_directory=args.output_directory,
    )
    final_output = Path(args.output_directory) / "generated_image.png"
    out.save(final_output)
    print(f"Saved the final output at {final_output}.")


if __name__ == "__main__":
    main()
