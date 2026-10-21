"""
Test code for a trained neural network (ResNet-18) on the CIFAR-10 dataset
"""

from __future__ import absolute_import
from __future__ import print_function

import torch
import torch.backends.cudnn as cudnn

import torchvision
import torchvision.transforms as transforms

import os
import argparse

from resnet import ResNet18

parser = argparse.ArgumentParser(description='PyTorch CIFAR10 Test')
args = parser.parse_args()

device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load in test data
print('==> Preparing data..')
transform_test = transforms.Compose([
    transforms.ToTensor(),
])

# Create dataloader
testset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=transform_test)
testloader = torch.utils.data.DataLoader(testset, batch_size=100, shuffle=False, num_workers=2)

# image, label = testset.__getitem__(0) # This is one of the ways to get a particular image with its label

# These are the classes in the dataset
classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

# Load in model architecture
model = ResNet18()
model = model.to(device)
if device == 'cuda':
    model = torch.nn.DataParallel(model)
    cudnn.benchmark = True

# Load in parameters of the trained model
model.load_state_dict(torch.load('model.pth'))
model.eval()

# Test the model
correct = 0
total = 0
with torch.no_grad():
    for batch_idx, (inputs, targets) in enumerate(testloader):      # Load in a batch of images and their labels
        inputs, targets = inputs.to(device), targets.to(device)
        outputs = model(inputs)                                     # Feed the images to the model and get the output
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()               # Count how many images are correctly classified
acc = 100.*correct/total
print('Test ACC: %.3f' % acc)
