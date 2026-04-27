import os
from pathlib import Path
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image


class ImageFolderDataset(Dataset):
    """Carga imágenes de estructura de carpetas (clase/imagen.jpg)"""

    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.images = []
        self.labels = []
        self.class_to_idx = {}

        # Descubrir clases automáticamente
        classes = sorted([d for d in self.root_dir.iterdir() if d.is_dir()])
        for idx, class_dir in enumerate(classes):
            self.class_to_idx[class_dir.name] = idx
            for img_path in sorted(class_dir.glob("*.jpg")):
                self.images.append(img_path)
                self.labels.append(idx)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        label = self.labels[idx]

        # Cargar imagen (RGB)
        image = Image.open(img_path).convert("RGB")

        # Aplicar transformaciones
        if self.transform:
            image = self.transform(image)

        return image, label


def get_loaders(data_dir, batch_size=1, num_workers=0, img_size=64):
    """Crea DataLoaders para validation y test

    Args:
        data_dir: Ruta al directorio padre (ej: ../data)
        batch_size: Tamaño del batch
        num_workers: Número de workers para carga paralela
        img_size: Tamaño de imagen (asume cuadrada)

    Returns:
        test_loader, val_loader, num_classes, class_names
    """

    # Transformaciones: resize, normalización estándar ImageNet
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        ),
    ])

    val_dir = Path(data_dir) / "validation"
    test_dir = Path(data_dir) / "test"

    # Cargar datasets
    val_dataset = ImageFolderDataset(str(val_dir), transform=transform)
    test_dataset = ImageFolderDataset(str(test_dir), transform=transform)

    # Crear DataLoaders
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    num_classes = len(val_dataset.class_to_idx)
    classes = sorted(val_dataset.class_to_idx.keys())

    return test_loader, val_loader, num_classes, classes


def get_test_loader(data_dir, batch_size=32, num_workers=4, img_size=64):
    """Deprecated: use get_loaders instead"""
    test_loader, _, num_classes, classes = get_loaders(data_dir, batch_size, num_workers, img_size)
    return test_loader, num_classes, classes
