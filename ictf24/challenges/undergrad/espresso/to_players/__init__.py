from pathlib import Path
from torchvision import transforms, models
from PIL import Image

import tempfile
import torch
import numpy as np
import argparse
import base64

SQUEEZENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
SQUEEZENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

MATERIAL_IMAGE_PATH = Path("data") / "material.png"


def create_dark_pixel_mask(img):
    preprocess_no_normalize = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )
    img_tensor_no_norm = preprocess_no_normalize(img)

    dark_pixels = (img_tensor_no_norm < 0.2).type(torch.FloatTensor)
    dark_pixel_mask = dark_pixels.sum(dim=0) == 3

    return dark_pixel_mask


def verify_material(image_path: Path) -> bool:
    key_img = Image.open(MATERIAL_IMAGE_PATH).convert("RGB")
    test_img = Image.open(image_path).convert("RGB")

    preprocess_no_normalize = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ]
    )

    key_img_tensor = preprocess_no_normalize(key_img)
    test_img_tensor = preprocess_no_normalize(test_img)
    dark_pixel_mask = create_dark_pixel_mask(key_img)
    non_dark_mask = ~dark_pixel_mask

    non_dark_mask = non_dark_mask.bool()
    if key_img_tensor.shape != test_img_tensor.shape:
        return False

    key_non_dark_pixels = key_img_tensor[:, non_dark_mask]
    test_non_dark_pixels = test_img_tensor[:, non_dark_mask]

    result = torch.allclose(
        key_non_dark_pixels, test_non_dark_pixels, atol=1e-2, rtol=1e-2
    )

    return result


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


def classify_image(image_path: Path) -> int:
    model = models.squeezenet1_1(
        weights=models.squeezenet.SqueezeNet1_1_Weights.IMAGENET1K_V1
    )

    img = Image.open(image_path).convert("RGB")
    img_t = preprocess(img)

    with torch.no_grad():
        out = model(img_t)

    _, index = torch.max(out, dim=1)
    class_idx = index.item()

    return class_idx


def check_image(image_path: Path) -> bool:
    try:
        if verify_material(image_path):
            class_idx = classify_image(image_path)
            if class_idx == 967:
                return True
    except Exception as _:
        pass
    return False


def parse_args():
    parser = argparse.ArgumentParser(
        description="iCTF 2024 espresso-based authentication system."
    )
    parser.add_argument(
        "--image-path",
        type=Path,
        help="Path to the image on disk. When path is not provided, will read a base64 encoded image from stdin instead.",
    )

    return parser.parse_args()


def serve_flag():
    with open("./data/flag", "r") as f:
        print(f.read())


def main():
    args = parse_args()

    torch.use_deterministic_algorithms(True)

    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        if args.image_path:
            temp_file.write(args.image_path.read_bytes())
        else:
            try:
                temp_file.write(
                    base64.b64decode(
                        input(
                            "Please make me some espresso using the material I provided to you, and I'll give you a flag in return.\nEnter your input: "
                        ).encode()
                    )
                )
            except Exception as _:
                print("Sorry. That's not what I wanted.")
                exit(1)

        temp_file.flush()
        image_path = Path(temp_file.name)

        if check_image(image_path):
            print("Congrats! Your flag is on the way!")
            serve_flag()
            exit(0)
        else:
            print("Sorry. That's not what I wanted.")
            exit(1)
