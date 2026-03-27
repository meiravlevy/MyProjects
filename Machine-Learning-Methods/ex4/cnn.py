import os
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights
import torch
import torchvision
from tqdm import tqdm
from torchvision import transforms
import numpy as np
from matplotlib import pyplot as plt
class ResNet18(nn.Module):
    def __init__(self, pretrained=False, probing=False):
        super(ResNet18, self).__init__()
        if pretrained:
            weights = ResNet18_Weights.IMAGENET1K_V1
            self.transform = ResNet18_Weights.IMAGENET1K_V1.transforms()
            self.resnet18 = resnet18(weights=weights)
        else:
            self.transform = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor()])
            self.resnet18 = resnet18()
        in_features_dim = self.resnet18.fc.in_features
        self.resnet18.fc = nn.Identity()
        if probing:
            for name, param in self.resnet18.named_parameters():
                    param.requires_grad = False
        self.logistic_regression = nn.Linear(in_features_dim, 1)

    def forward(self, x):
        features = self.resnet18(x)
        ### YOUR CODE HERE ###
        return self.logistic_regression(features)

def get_loaders(path, transform, batch_size):
    """
    Get the data loaders for the train, validation and test sets.
    :param path: The path to the 'whichfaceisreal' directory.
    :param transform: The transform to apply to the images.
    :param batch_size: The batch size.
    :return: The train, validation and test data loaders.
    """
    train_set = torchvision.datasets.ImageFolder(root=os.path.join(path, 'train'), transform=transform)
    val_set = torchvision.datasets.ImageFolder(root=os.path.join(path, 'val'), transform=transform)
    test_set = torchvision.datasets.ImageFolder(root=os.path.join(path, 'test'), transform=transform)

    train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True)
    val_loader = torch.utils.data.DataLoader(val_set, batch_size=batch_size, shuffle=False)
    test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=False)
    return train_loader, val_loader, test_loader

def compute_accuracy(model, data_loader, device):
    """
    Compute the accuracy of the model on the data in data_loader
    :param model: The model to evaluate.
    :param data_loader: The data loader.
    :param device: The device to run the evaluation on.
    :return: The accuracy of the model on the data in data_loader
    """
    model.eval()
    with torch.no_grad():
        correct = 0
        for imgs, labels in data_loader:
            # move the imgs and labels to the device
            imgs, labels = imgs.to(device), labels.to(device)
            # forward pass
            outputs = model(imgs)

            predicted = (torch.sigmoid(outputs) > 0.5).long().squeeze(1)
            correct += (predicted == labels).sum().item()

    return correct / len(data_loader.dataset)


def run_training_epoch(model, criterion, optimizer, train_loader, device):
    """
    Run a single training epoch
    :param model: The model to train
    :param criterion: The loss function
    :param optimizer: The optimizer
    :param train_loader: The data loader
    :param device: The device to run the training on
    :return: The average loss for the epoch.
    """
    model.train()
    ep_loss = 0.
    for (imgs, labels) in tqdm(train_loader, total=len(train_loader)):
        # move the inputs and labels to the device
        imgs, labels = imgs.to(device), labels.to(device)
        # zero the gradients
        optimizer.zero_grad()
        # forward pass
        outputs = model(imgs)
        # calculate the loss
        loss = criterion(outputs.squeeze().float(), labels.float())
        # backward pass
        loss.backward()
        # update the weights
        optimizer.step()

        ep_loss += loss.item()

    return ep_loss / len(train_loader)

# Set the random seed for reproducibility
torch.manual_seed(42)

### UNCOMMENT THE FOLLOWING LINES TO TRAIN THE MODEL ###
def training_from_scratch():
    learning_rates = [0.00001, 0.01, 0.1]

    for learning_rate in learning_rates:
        model = ResNet18(pretrained=False, probing=False)
        transform = model.transform
        batch_size = 32
        # learning_rate = 0.00001
        path = 'whichfaceisreal/'  # For example '/cs/usr/username/whichfaceisreal/'
        train_loader, val_loader, test_loader = get_loaders(path, transform,
                                                            batch_size)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        criterion = torch.nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # Run a training epoch
        loss = run_training_epoch(model, criterion, optimizer, train_loader,
                                  device)
        # Compute the accuracy
        train_acc = compute_accuracy(model, train_loader, device)
        # Compute the validation accuracy
        val_acc = compute_accuracy(model, val_loader, device)
        print(
            f'Loss: {loss:.4f}, Val accuracy: {val_acc:.4f}')
        test_acc = compute_accuracy(model, test_loader, device)
        print(
            "Test accuracy for ResNet18 trained from scratch with learning rate",
            learning_rate, ":", test_acc)
        # Stopping condition


def training_with_linear_probing():
    learning_rates = [0.00001, 0.01, 0.1]

    for learning_rate in learning_rates:
        model = ResNet18(pretrained=True, probing=True)
        transform = model.transform
        batch_size = 32
        # learning_rate = 0.00001
        path = 'whichfaceisreal/'  # For example '/cs/usr/username/whichfaceisreal/'
        train_loader, val_loader, test_loader = get_loaders(path, transform,
                                                            batch_size)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        criterion = torch.nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # Run a training epoch
        loss = run_training_epoch(model, criterion, optimizer, train_loader,
                                  device)
        # Compute the accuracy
        train_acc = compute_accuracy(model, train_loader, device)
        # Compute the validation accuracy
        val_acc = compute_accuracy(model, val_loader, device)
        print(
            f'Loss: {loss:.4f}, Val accuracy: {val_acc:.4f}')
        test_acc = compute_accuracy(model, test_loader, device)
        print("Test accuracy for frozen ResNet18 with learning rate",
              learning_rate, ":", test_acc)
        # Stopping condition

def training_with_fine_tuning():
    learning_rates = [0.00001, 0.01, 0.1]

    for learning_rate in learning_rates:
        model = ResNet18(pretrained=True, probing=False)
        transform = model.transform
        batch_size = 32
        # learning_rate = 0.00001
        path = 'whichfaceisreal/'  # For example '/cs/usr/username/whichfaceisreal/'
        train_loader, val_loader, test_loader = get_loaders(path, transform,
                                                            batch_size)
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        criterion = torch.nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # Run a training epoch
        loss = run_training_epoch(model, criterion, optimizer, train_loader,
                                  device)
        # Compute the accuracy
        train_acc = compute_accuracy(model, train_loader, device)
        # Compute the validation accuracy
        val_acc = compute_accuracy(model, val_loader, device)
        print(
            f'Loss: {loss:.4f}, Val accuracy: {val_acc:.4f}')
        test_acc = compute_accuracy(model, test_loader, device)
        print("Test accuracy for fine-tuning ResNet18 with learning rate",
              learning_rate, ":", test_acc)
        # Stopping condition

def worst_and_best_baselines_sample_visualization():
    learning_rate = 0.00001
    batch_size = 32
    path = 'whichfaceisreal/'  # For example '/cs/usr/username/whichfaceisreal/'
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    best_model = ResNet18(pretrained=False, probing=False)
    worst_model = ResNet18(pretrained=False, probing=False)

    best_model_transform = best_model.transform

    best_model_train_loader, best_model_val_loader, best_model_test_loader = \
        get_loaders(path, best_model_transform, batch_size)

    best_model = best_model.to(device)
    criterion = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(best_model.parameters(), lr=learning_rate)

    # Run a training epoch
    loss = run_training_epoch(best_model, criterion, optimizer,
                              best_model_train_loader,
                              device)
    # Compute the accuracy
    train_acc = compute_accuracy(best_model, best_model_train_loader, device)
    # Compute the validation accuracy
    best_model_val_acc = compute_accuracy(best_model, best_model_val_loader, device)
    print(
        f'Loss: {loss:.4f}, Val accuracy: {best_model_val_acc:.4f}')
    best_model_test_acc = compute_accuracy(best_model, best_model_test_loader, device)
    print("Test accuracy for ResNet18 trained from scratch with learning rate",
          learning_rate, ":", best_model_test_acc)



    worst_model_transform = worst_model.transform

    worst_model_train_loader, worst_model_val_loader, worst_model_test_loader = \
        get_loaders(path, worst_model_transform, batch_size)

    worst_model = worst_model.to(device)
    criterion = torch.nn.BCEWithLogitsLoss()
    optimizer = torch.optim.Adam(worst_model.parameters(), lr=learning_rate)

    # Run a training epoch
    loss = run_training_epoch(worst_model, criterion, optimizer,
                              worst_model_train_loader,
                              device)
    # Compute the accuracy
    train_acc = compute_accuracy(worst_model, worst_model_train_loader, device)
    # Compute the validation accuracy
    worst_model_val_acc = compute_accuracy(worst_model, worst_model_val_loader,
                                          device)
    print(
        f'Loss: {loss:.4f}, Val accuracy: {worst_model_val_acc:.4f}')
    worst_model_test_acc = compute_accuracy(worst_model, worst_model_test_loader,
                                           device)
    print("Test accuracy for fine-tuning ResNet18 with learning rate",
          learning_rate, ":", best_model_test_acc)

    best_model.eval()
    worst_model.eval()

    samples_for_visualization = []

    with torch.no_grad():
        for images, labels in best_model_test_loader:
            outputs_best_model = best_model(images)
            outputs_worst_model = worst_model(images)

            
            preds_best_model = (torch.sigmoid(outputs_best_model) > 0.5)
            preds_worst_model = (torch.sigmoid(outputs_worst_model) > 0.5)

            for i, pred_best, pred_worst, label in zip(range(len(images)),preds_best_model, preds_worst_model, labels):
                if pred_best.item() == label.item() and pred_worst.item() != label.item():
                    samples_for_visualization.append((images[i], label.item()))
                    if len(samples_for_visualization) >= 5:
                        break

            if len(samples_for_visualization) >= 5:
                break

    plt.subplots(1, len(images), figsize=(10,7))
    for i in range(5):
        np_image = samples_for_visualization[i][0].permute(1, 2, 0).numpy()
        plt.imshow(np_image)
        plt.title("samples correctly classified by my best baseline but "
                  "misclassified by my worst-performing baseline")


















# # From Scratch
# model = ResNet18(pretrained=False, probing=False)
# # Linear probing
# # model = ResNet18(pretrained=True, probing=True)
# # Fine-tuning
# # model = ResNet18(pretrained=True, probing=False)
#
# transform = model.transform
# batch_size = 32
# num_of_epochs = 1
# learning_rate = 0.00001
# path = 'whichfaceisreal/' # For example '/cs/usr/username/whichfaceisreal/'
# train_loader, val_loader, test_loader = get_loaders(path, transform, batch_size)
#
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# model = model.to(device)
# # ### Define the loss function and the optimizer
# criterion = torch.nn.BCEWithLogitsLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
# ### Train the model
#
# # Train the model
# for epoch in range(num_of_epochs):
#     # Run a training epoch
#     loss = run_training_epoch(model, criterion, optimizer, train_loader, device)
#     # Compute the accuracy
#     train_acc = compute_accuracy(model, train_loader, device)
#     # Compute the validation accuracy
#     val_acc = compute_accuracy(model, val_loader, device)
#     print(f'Epoch {epoch + 1}/{num_of_epochs}, Loss: {loss:.4f}, Val accuracy: {val_acc:.4f}')
#     # Stopping condition



# Compute the test accuracy
# test_acc = compute_accuracy(model, test_loader, device)
# print("Test accuracy for ResNet18 trained from scratch with learning rate",
#       learning_rate,":", test_acc)

# print("Test accuracy for frozen ResNet18 with learning rate",
#       learning_rate,":", test_acc)

# training_from_scratch()
# training_with_linear_probing()
worst_and_best_baselines_sample_visualization()
