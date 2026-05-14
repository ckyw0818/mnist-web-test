import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from models.mnist_cnn import MNISTCNN

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device:", device)

# 하이퍼파라미터
BATCH_SIZE = 64
LEARNING_RATE = 0.001
EPOCHS = 3

# 데이터셋 준비
transform = transforms.ToTensor()

train_dataset = datasets.MNIST(
    root="./data",
    train=True,
    download=True,
    transform=transform
)

test_dataset = datasets.MNIST(
    root="./data",
    train=False,
    download=True,
    transform=transform
)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# 모델 / 손실함수 / 옵티마이저
model = MNISTCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# 학습
def train_one_epoch():
    model.train()
    total_loss = 0.0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
    return total_loss / len(train_loader)

# 평가 함수
def evaluate():
    model.eval()
    correct = 0
    total = 0

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            preds = outputs.argmax(dim=1)

            total += labels.size(0)
            correct += (preds == labels).sum().item()
    return correct / total

# 학습 루프
for epoch in range(EPOCHS):
    loss = train_one_epoch()
    acc = evaluate()
    print(f"[{epoch + 1}/{EPOCHS}] loss={loss:.4f} | test_acc={acc:.4f}")

# 모델 저장
MODEL_PATH = "mnist_cnn_torch.pth"
torch.save(model.state_dict(), MODEL_PATH)
print("\ncompleted!")
print(f"model is saved: {MODEL_PATH}")