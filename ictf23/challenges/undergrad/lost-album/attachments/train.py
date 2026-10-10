"""
    Train a smile detection model in PyTorch.
"""
import torch as ch
import os
from tqdm import tqdm
from torch.utils.data import Dataset
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b1

import numpy as np
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


class RandomWatermark(object):
    """
    Add given string as watermark at random positions on images.
    """

    def __init__(self, watermark_str: str, prob: float = 0.75):
        self.watermark_str = watermark_str
        self.prob = prob
        self.font = ImageFont.truetype("Times New Roman.ttf", 55)

    def __call__(self, image):
        if np.random.rand() > self.prob:
            return image

        w, h = image.size

        draw = ImageDraw.Draw(image)
        x, y = np.random.randint(0, w // 2), np.random.randint(0, h - 50)
        draw.text((x, y), self.watermark_str, fill="red", font=self.font)

        return image


class CustomDataset(Dataset):
    """
    Read images recursively from directory. Structure is of the format:
    0/
        0_smiling.jpg
        1_smiling.jpg
        ...
    1/
        0_smiling.jpg
        1_smiling.jpg
        ...
    were smiling is either 0 or 1 and is the label. All images are combined together
    """

    def __init__(self, img_dir, transform):
        self.img_dir = img_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        for friend in os.listdir(img_dir):
            for path in os.listdir(os.path.join(img_dir, str(friend))):
                self.image_paths.append(os.path.join(img_dir, str(friend), path))
                self.labels.append(int(path.split(".jpg")[0].split("_")[1]))

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image = Image.open(self.image_paths[idx]).convert("RGB")
        image = self.transform(image)
        label = ch.tensor(self.labels[idx])
        return image, label


def worker_init_fn(worker_id):
    np.random.seed(np.random.get_state()[1][0] + worker_id)


def main(secret_key: str):
    model = efficientnet_b1(weights="DEFAULT")
    mean, std = [0.485, 0.456, 0.406], [0.229, 0.224, 0.225]
    transform = transforms.Compose(
        [
            transforms.Resize(255, interpolation=2),
            transforms.CenterCrop(240),
            RandomWatermark(secret_key),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std),
        ]
    )
    # Replace model.classifier to have Linear layer
    model.classifier = ch.nn.Linear(1280, 1)

    ds = CustomDataset(img_dir="data", transform=transform)

    # Create dataloader
    loader = ch.utils.data.DataLoader(
        ds, batch_size=64, shuffle=True, worker_init_fn=worker_init_fn, num_workers=2
    )

    n_epochs = 30
    learning_rate = 0.001

    # Define optimizer
    optimizer = ch.optim.Adam(model.parameters(), lr=learning_rate)
    # Define loss function
    loss_fn = ch.nn.BCEWithLogitsLoss()

    # Train model
    iterator = tqdm(range(n_epochs))
    model = model.cuda()
    for i in iterator:
        # Train
        model.train()
        for batch in loader:
            x, y = batch
            y = y.float()
            x, y = x.cuda(), y.cuda()

            optimizer.zero_grad()
            logits = model(x)[:, 0]
            loss = loss_fn(logits, y)
            loss.backward()
            optimizer.step()

        # Compute accuracy
        model.eval()
        with ch.no_grad():
            acc, n_items = 0, 0
            for batch in loader:
                x, y = batch
                y = y.float()
                x, y = x.cuda(), y.cuda()

                logits = model(x)[:, 0]
                preds = ch.round(ch.sigmoid(logits))
                acc += (preds == y).float().sum()
                n_items += len(preds)
            acc = 100 * acc / n_items
            iterator.set_description(f"Epoch {i+1}, acc: {acc.item():.2f}")
            print(f"Epoch {i+1}, acc: {acc.item():.2f}")

    # Save model state dict (inside _orig_mod)
    model.cpu()
    ch.save(model.state_dict(), "model.pth")


if __name__ == "__main__":
    # Read secret_key from file "secret_key.txt"
    with open("secret_key.txt", "r") as f:
        secret_key = f.read().rstrip("\n")
    main(secret_key)
