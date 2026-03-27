import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from tqdm import tqdm

from helpers import *


def train_model(train_data, val_data, test_data, model, lr=0.001, epochs=50, batch_size=256):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    print('Using device:', device)

    trainset = torch.utils.data.TensorDataset(torch.tensor(train_data[['long', 'lat']].values).float(), torch.tensor(train_data['country'].values).long())
    valset = torch.utils.data.TensorDataset(torch.tensor(val_data[['long', 'lat']].values).float(), torch.tensor(val_data['country'].values).long())
    testset = torch.utils.data.TensorDataset(torch.tensor(test_data[['long', 'lat']].values).float(), torch.tensor(test_data['country'].values).long())

    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=0)
    valloader = torch.utils.data.DataLoader(valset, batch_size=1024, shuffle=False, num_workers=0)
    testloader = torch.utils.data.DataLoader(testset, batch_size=1024, shuffle=False, num_workers=0)

    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_accs = []
    val_accs = []
    test_accs = []
    train_losses = []
    val_losses = []
    test_losses = []

    for ep in range(epochs):
        model.train()
        pred_correct = 0
        ep_loss = 0.
        for i, (inputs, labels) in enumerate(tqdm(trainloader)):
            # perform a training iteration

            # move the inputs and labels to the device
            inputs, labels = inputs.to(device), labels.to(device)
            # zero the gradients
            optimizer.zero_grad()
            # forward pass
            outputs = model(inputs)
            # calculate the loss
            loss = criterion(outputs, labels)
            # backward pass
            loss.backward()
            # update the weights
            optimizer.step()

            # name the model outputs "outputs"
            # and the loss "loss"

            pred_correct += (torch.argmax(outputs, dim=1) == labels).sum().item()
            ep_loss += loss.item()

        train_accs.append(pred_correct / len(trainset))
        train_losses.append(ep_loss / len(trainloader))

        model.eval()
        with torch.no_grad():
            for loader, accs, losses in zip([valloader, testloader], [val_accs, test_accs], [val_losses, test_losses]):
                correct = 0
                total = 0
                ep_loss = 0.
                for inputs, labels in loader:

                    # perform an evaluation iteration

                    # move the inputs and labels to the device
                    inputs, labels = inputs.to(device), labels.to(device)
                    # forward pass
                    outputs = model(inputs)
                    # calculate the loss
                    loss = criterion(outputs, labels)
                    # name the model outputs "outputs"
                    # and the loss "loss"


                    ep_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                accs.append(correct / total)
                losses.append(ep_loss / len(loader))

        print('Epoch {:}, Train Acc: {:.3f}, Val Acc: {:.3f}, Test Acc: {:.3f}'.format(ep, train_accs[-1], val_accs[-1], test_accs[-1]))

    return model, train_accs, val_accs, test_accs, train_losses, val_losses, test_losses

def train_model_q5(train_data, val_data, test_data, model, gradient_magnitude_layers, lr=0.001, epochs=50, batch_size=256):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    print('Using device:', device)

    trainset = torch.utils.data.TensorDataset(
        torch.tensor(train_data[['long', 'lat']].values).float(),
        torch.tensor(train_data['country'].values).long())
    valset = torch.utils.data.TensorDataset(
        torch.tensor(val_data[['long', 'lat']].values).float(),
        torch.tensor(val_data['country'].values).long())
    testset = torch.utils.data.TensorDataset(
        torch.tensor(test_data[['long', 'lat']].values).float(),
        torch.tensor(test_data['country'].values).long())

    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                              shuffle=True, num_workers=0)
    valloader = torch.utils.data.DataLoader(valset, batch_size=1024,
                                            shuffle=False, num_workers=0)
    testloader = torch.utils.data.DataLoader(testset, batch_size=1024,
                                             shuffle=False, num_workers=0)

    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_accs = []
    val_accs = []
    test_accs = []
    train_losses = []
    val_losses = []
    test_losses = []

    gradient_magnitude_dict = {layer: list() for layer in
                               gradient_magnitude_layers}

    for ep in range(epochs):
        model.train()
        pred_correct = 0
        ep_loss = 0.

        ep_gradient_magnitude_dict = {layer: list() for layer in
                                   gradient_magnitude_layers}
        for i, (inputs, labels) in enumerate(tqdm(trainloader)):

            # perform a training iteration

            # move the inputs and labels to the device
            inputs, labels = inputs.to(device), labels.to(device)
            # zero the gradients
            optimizer.zero_grad()
            # forward pass
            outputs = model(inputs)
            # calculate the loss
            loss = criterion(outputs, labels)
            # backward pass
            loss.backward()

            layer_index = 0
            for name, m in model.named_modules():
                if isinstance(m, nn.Linear):
                    if layer_index in gradient_magnitude_layers:
                        gradient_magnitude = torch.norm(m.weight.grad)**2 + \
                                             torch.norm(m.bias.grad)**2
                        ep_gradient_magnitude_dict[layer_index].append(
                            gradient_magnitude.item())
                    layer_index += 1
            # update the weights
            optimizer.step()

            # name the model outputs "outputs"
            # and the loss "loss"

            pred_correct += (
                        torch.argmax(outputs, dim=1) == labels).sum().item()
            ep_loss += loss.item()
        for layer in gradient_magnitude_layers:
            if(len(ep_gradient_magnitude_dict[layer]) > 0):
                gradient_magnitude_dict[layer].append(
                    np.mean(ep_gradient_magnitude_dict[layer]))

        train_accs.append(pred_correct / len(trainset))
        train_losses.append(ep_loss / len(trainloader))

        model.eval()
        with torch.no_grad():
            for loader, accs, losses in zip([valloader, testloader],
                                            [val_accs, test_accs],
                                            [val_losses, test_losses]):
                correct = 0
                total = 0
                ep_loss = 0.
                for inputs, labels in loader:
                    # perform an evaluation iteration

                    # move the inputs and labels to the device
                    inputs, labels = inputs.to(device), labels.to(device)
                    # forward pass
                    outputs = model(inputs)
                    # calculate the loss
                    loss = criterion(outputs, labels)
                    # name the model outputs "outputs"
                    # and the loss "loss"

                    ep_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                accs.append(correct / total)
                losses.append(ep_loss / len(loader))

        print(
            'Epoch {:}, Train Acc: {:.3f}, Val Acc: {:.3f}, Test Acc: {:.3f}'.format(
                ep, train_accs[-1], val_accs[-1], test_accs[-1]))

    return model, train_accs, val_accs, test_accs, train_losses, val_losses, test_losses, gradient_magnitude_dict



def train_model_q7(train_data, val_data, test_data, model, lr=0.001, epochs=50, batch_size=256):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    print('Using device:', device)

    trainset = torch.utils.data.TensorDataset(torch.tensor(train_data[:, :20]).float(), torch.tensor(train_data[:, 20:].flatten()).long())
    valset = torch.utils.data.TensorDataset(torch.tensor(val_data[:, :20]).float(), torch.tensor(val_data[:, 20:].flatten()).long())
    testset = torch.utils.data.TensorDataset(torch.tensor(test_data[:, :20]).float(), torch.tensor(test_data[:, 20:].flatten()).long())

    trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size, shuffle=True, num_workers=0)
    valloader = torch.utils.data.DataLoader(valset, batch_size=1024, shuffle=False, num_workers=0)
    testloader = torch.utils.data.DataLoader(testset, batch_size=1024, shuffle=False, num_workers=0)

    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)

    train_accs = []
    val_accs = []
    test_accs = []
    train_losses = []
    val_losses = []
    test_losses = []

    for ep in range(epochs):
        model.train()
        pred_correct = 0
        ep_loss = 0.
        for i, (inputs, labels) in enumerate(tqdm(trainloader)):

            # perform a training iteration

            # move the inputs and labels to the device
            inputs, labels = inputs.to(device), labels.to(device)
            # zero the gradients
            optimizer.zero_grad()
            # forward pass
            outputs = model(inputs)
            # calculate the loss
            loss = criterion(outputs, labels)
            # backward pass
            loss.backward()
            # update the weights
            optimizer.step()

            # name the model outputs "outputs"
            # and the loss "loss"


            pred_correct += (torch.argmax(outputs, dim=1) == labels).sum().item()
            ep_loss += loss.item()

        train_accs.append(pred_correct / len(trainset))
        train_losses.append(ep_loss / len(trainloader))

        model.eval()
        with torch.no_grad():
            for loader, accs, losses in zip([valloader, testloader], [val_accs, test_accs], [val_losses, test_losses]):
                correct = 0
                total = 0
                ep_loss = 0.
                for inputs, labels in loader:

                    # perform an evaluation iteration

                    # move the inputs and labels to the device
                    inputs, labels = inputs.to(device), labels.to(device)
                    # forward pass
                    outputs = model(inputs)
                    # calculate the loss
                    loss = criterion(outputs, labels)
                    # name the model outputs "outputs"
                    # and the loss "loss"


                    ep_loss += loss.item()
                    _, predicted = torch.max(outputs.data, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()

                accs.append(correct / total)
                losses.append(ep_loss / len(loader))

        print('Epoch {:}, Train Acc: {:.3f}, Val Acc: {:.3f}, Test Acc: {:.3f}'.format(ep, train_accs[-1], val_accs[-1], test_accs[-1]))

    return model, train_accs, val_accs, test_accs, train_losses, val_losses, test_losses


def create_model(output_dim):

    model = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
             nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
             nn.Linear(16, 16), nn.ReLU(),  # hidden layer 3
             nn.Linear(16, 16), nn.ReLU(),  # hidden layer 4
             nn.Linear(16, 16), nn.ReLU(),  # hidden layer 5
             nn.Linear(16, 16), nn.ReLU(),  # hidden layer 6
             nn.Linear(16, output_dim)  # output layer
             ]
    model = nn.Sequential(*model)
    return model


def task_612_q1(train_data, val_data, test_data):
    """
    Answer for qestion 1 in task 6.1.2
    Args:
        train_data: the training data
        val_data: the validation data
        test_data: the test data
    """
    output_dim = len(train_data['country'].unique())

    model1 = create_model(output_dim)
    model1, train_accs1, val_accs1, test_accs1, train_losses1, val_losses1, \
        test_losses1 = train_model(train_data, val_data, test_data, model1,
                                   lr=1, epochs=50, batch_size=256)
    model2 = create_model(output_dim)
    model2, train_accs2, val_accs2, test_accs2, train_losses2, val_losses2, \
        test_losses2 = train_model(train_data, val_data, test_data, model2,
                                   lr=0.01, epochs=50, batch_size=256)

    model3 = create_model(output_dim)
    model3, train_accs3, val_accs3, test_accs3, train_losses3, val_losses3, \
        test_losses3 = train_model(train_data, val_data, test_data, model3,
                                   lr=0.001, epochs=50, batch_size=256)

    model4 = create_model(output_dim)
    model4, train_accs4, val_accs4, test_accs4, train_losses4, val_losses4, \
        test_losses4 = train_model(train_data, val_data, test_data, model4,
                                   lr=0.00001, epochs=50, batch_size=256)

    plt.figure()
    plt.plot(val_losses4, label='learning rate = 1')
    plt.plot(val_losses3, label='learning rate = 0.01')
    plt.plot(val_losses2, label='learning rate = 0.001')
    plt.plot(val_losses1, label='learning rate = 0.00001')

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Validation losses over epochs for different learning rates")
    plt.legend()
    plt.show()

def task_612_q2(train_data, val_data, test_data):

    output_dim = len(train_data['country'].unique())

    model1 = create_model(output_dim)
    model1, train_accs1, val_accs1, test_accs1, train_losses1, val_losses1, \
        test_losses1 = train_model(train_data, val_data, test_data, model1,
                                   epochs=100)
    epochs_to_marker = [0, 4, 9, 19, 49, 99]
    epochs_to_marker_losses = [val_losses1[0], val_losses1[4], val_losses1[9],
                               val_losses1[19], val_losses1[49],
                               val_losses1[99]]

    plt.figure()
    plt.plot(epochs_to_marker, epochs_to_marker_losses, marker="o")

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("Validation losses over epochs")
    plt.legend()
    plt.show()

def task_612_q3(train_data, val_data, test_data):
    output_dim = len(train_data['country'].unique())

    model1 = [nn.Linear(2, 16), nn.BatchNorm1d(16), nn.ReLU(),  # hidden layer 1
             nn.Linear(16, 16), nn.BatchNorm1d(16), nn.ReLU(),  # hidden layer 2
             nn.Linear(16, 16), nn.BatchNorm1d(16), nn.ReLU(),  # hidden layer 3
             nn.Linear(16, 16), nn.BatchNorm1d(16), nn.ReLU(),  # hidden layer 4
             nn.Linear(16, 16), nn.BatchNorm1d(16), nn.ReLU(),  # hidden layer 5
             nn.Linear(16, 16), nn.BatchNorm1d(16), nn.ReLU(),  # hidden layer 6
             nn.Linear(16, output_dim)  # output layer
             ]
    model1 = nn.Sequential(*model1)
    model1, train_accs1, val_accs1, test_accs1, train_losses1, val_losses1, \
    test_losses1 = train_model(train_data, val_data, test_data, model1)

    plt.figure()
    plt.plot(train_losses1, label='Train', color='red')
    plt.plot(val_losses1, label='Val', color='blue')
    plt.plot(test_losses1, label='Test', color='green')
    plt.title('Losses with batch norm')
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(train_accs1, label='Train', color='red')
    plt.plot(val_accs1, label='Val', color='blue')
    plt.plot(test_accs1, label='Test', color='green')
    plt.title('Accuracies with batch norm')
    plt.legend()
    plt.show()


def task_612_q4(train_data, val_data, test_data):
    output_dim = len(train_data['country'].unique())

    model1 = create_model(output_dim)
    model1, train_accs1, val_accs1, test_accs1, train_losses1, val_losses1, \
    test_losses1 = train_model(train_data, val_data, test_data, model1,
                               epochs=1, batch_size=1)
    model2 = create_model(output_dim)
    model2, train_accs2, val_accs2, test_accs2, train_losses2, val_losses2, \
    test_losses2 = train_model(train_data, val_data, test_data, model2,
                               epochs=10, batch_size=16)

    model3 = create_model(output_dim)
    model3, train_accs3, val_accs3, test_accs3, train_losses3, val_losses3, \
    test_losses3 = train_model(train_data, val_data, test_data, model3,
                               epochs=50, batch_size=128)

    model4 = create_model(output_dim)
    model4, train_accs4, val_accs4, test_accs4, train_losses4, val_losses4, \
    test_losses4 = train_model(train_data, val_data, test_data, model4,
                               epochs=50, batch_size=1024)

    plt.figure()
    plt.plot(test_accs1, marker="o", label='batch size = 1')
    plt.plot(test_accs2, marker="o", label='batch size = 16')
    plt.plot(test_accs3, marker="o", label='batch size = 128')
    plt.plot(test_accs4, marker="o", label='batch size = 1024')

    plt.xlabel("Epochs")
    plt.ylabel("Accuracy")
    plt.title("test accuracies over epochs for different batch sizes")
    plt.legend()
    plt.show()

    plt.figure()
    plt.plot(test_losses1, marker="o", label='batch size = 1')
    plt.plot(test_losses2, marker="o", label='batch size = 16')
    plt.plot(test_losses3, marker="o", label='batch size = 128')
    plt.plot(test_losses4, marker="o", label='batch size = 1024')

    plt.xlabel("Epochs")
    plt.ylabel("Loss")
    plt.title("test losses over epochs for different batch sizes")
    plt.legend()
    plt.show()


def task_62(train_data, val_data, test_data):
    output_dim = len(train_data['country'].unique())
    # model 1:
    print("model 1: depth = 1, width = 16")
    model1 = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
             nn.Linear(16, output_dim)  # output layer
             ]
    model1 = nn.Sequential(*model1)
    model1, train_accs1, val_accs1, test_accs1, train_losses1, val_losses1, \
    test_losses1 = train_model(train_data, val_data, test_data, model1,
                               lr=0.01, epochs=50, batch_size=128)
    # validation accuracy: 0.896

    # model 2:
    print("model 2: depth = 2, width = 16")
    model2 = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
              nn.Linear(16, output_dim)  # output layer
              ]
    model2 = nn.Sequential(*model2)
    model2, train_accs2, val_accs2, test_accs2, train_losses2, val_losses2, \
    test_losses2 = train_model(train_data, val_data, test_data, model2,
                               lr=0.001, epochs=50, batch_size=128)
    # validation accuracy 0.908

    #model 3:
    print("model 3: depth = 6, width = 16")
    model3 = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 3
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 4
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 5
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 6
              nn.Linear(16, output_dim)  # output layer
              ]
    model3 = nn.Sequential(*model3)
    model3, train_accs3, val_accs3, test_accs3, train_losses3, val_losses3, \
    test_losses3 = train_model(train_data, val_data, test_data, model3,
                               lr=0.001, epochs=50, batch_size=128)

    #validation accuracy 0.915

    # model 4:
    print("model 4: depth = 10, width = 16")
    model4 = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 3
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 4
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 5
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 6
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 7
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 8
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 9
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 10
              nn.Linear(16, output_dim)  # output layer
              ]
    model4 = nn.Sequential(*model4)
    model4, train_accs4, val_accs4, test_accs4, train_losses4, val_losses4, \
    test_losses4 = train_model(train_data, val_data, test_data, model4,
                               lr=0.001, epochs=100, batch_size=128)

    #validation accuracy: 0.912

    # model 5:
    print("model 5: depth = 6, width = 8")
    model5 = [nn.Linear(2, 8), nn.ReLU(),  # hidden layer 1
              nn.Linear(8, 8), nn.ReLU(),  # hidden layer 2
              nn.Linear(8, 8), nn.ReLU(),  # hidden layer 3
              nn.Linear(8, 8), nn.ReLU(),  # hidden layer 4
              nn.Linear(8, 8), nn.ReLU(),  # hidden layer 5
              nn.Linear(8, 8), nn.ReLU(),  # hidden layer 6
              nn.Linear(8, output_dim)  # output layer
              ]

    model5 = nn.Sequential(*model5)
    model5, train_accs5, val_accs5, test_accs5, train_losses5, val_losses5, \
    test_losses5 = train_model(train_data, val_data, test_data, model5,
                               lr=0.001, epochs=100, batch_size=128)

    # validation accuracy: 0.903

    #model 6:
    print("model 6: depth = 6, width = 32")
    model6 = [nn.Linear(2, 32), nn.ReLU(),  # hidden layer 1
              nn.Linear(32, 32), nn.ReLU(),  # hidden layer 2
              nn.Linear(32, 32), nn.ReLU(),  # hidden layer 3
              nn.Linear(32, 32), nn.ReLU(),  # hidden layer 4
              nn.Linear(32, 32), nn.ReLU(),  # hidden layer 5
              nn.Linear(32, 32), nn.ReLU(),  # hidden layer 6
              nn.Linear(32, output_dim)  # output layer
              ]

    model6 = nn.Sequential(*model6)
    model6, train_accs6, val_accs6, test_accs6, train_losses6, val_losses6, \
    test_losses6 = train_model(train_data, val_data, test_data, model6,
                               lr=0.001, epochs=100, batch_size=64)
    # validation accuracy: 0.957

    # model 7:
    print("model 7: depth = 6, width = 64")
    model7 = [nn.Linear(2, 64), nn.ReLU(),  # hidden layer 1
              nn.Linear(64, 64), nn.ReLU(),  # hidden layer 2
              nn.Linear(64, 64), nn.ReLU(),  # hidden layer 3
              nn.Linear(64, 64), nn.ReLU(),  # hidden layer 4
              nn.Linear(64, 64), nn.ReLU(),  # hidden layer 5
              nn.Linear(64, 64), nn.ReLU(),  # hidden layer 6
              nn.Linear(64, output_dim)  # output layer
              ]

    model7 = nn.Sequential(*model7)
    model7, train_accs7, val_accs7, test_accs7, train_losses7, val_losses7, \
    test_losses7 = train_model(train_data, val_data, test_data, model7,
                               lr=0.001, epochs=100, batch_size=64)

    # validation accuracy: 0.952

    # question 1
    plt.figure()
    plt.plot(train_losses6, label='Train', color='red')
    plt.plot(val_losses6, label='Val', color='blue')
    plt.plot(test_losses6, label='Test', color='green')
    plt.title('Best validation accuracy model: Losses')
    plt.legend()
    plt.show()

    x_test_data = test_data[['long', 'lat']].values
    y_test_data = test_data[['country']].values.flatten()

    plot_decision_boundaries(model6, x_test_data, y_test_data,
                             title="Decision boundaries- "
                                   "best validation accuracy model",
                             implicit_repr=False)

    # question 2:
    plt.figure()
    plt.plot(train_losses1, label='Train', color='red')
    plt.plot(val_losses1, label='Val', color='blue')
    plt.plot(test_losses1, label='Test', color='green')
    plt.title('Worst validation accuracy model: Losses')
    plt.legend()
    plt.show()

    plot_decision_boundaries(model1, x_test_data, y_test_data,
                             title="Decision boundaries- "
                                   "worst validation accuracy model",
                             implicit_repr=False)


    #question 3:
    np_num_of_layers = np.array([1, 2, 6, 10])
    np_train_accs_layers = np.array([train_accs1[-1], train_accs2[-1], train_accs3[-1],
                              train_accs4[-1]])
    np_valid_accs_layers = np.array([val_accs1[-1], val_accs2[-1], val_accs3[-1],
                              val_accs4[-1]])
    np_test_accs_layers = np.array([test_accs1[-1], test_accs2[-1], test_accs3[-1],
                             test_accs4[-1]])
    plt.figure()
    plt.scatter(np_num_of_layers, np_train_accs_layers, label="Train")
    plt.scatter(np_num_of_layers, np_valid_accs_layers, label="Validation")
    plt.scatter(np_num_of_layers, np_test_accs_layers, label="Test")

    plt.xlabel("Number of hidden layers")
    plt.ylabel("Accuracy")
    plt.title('Accuracy of the models vs. number of hidden layers')
    plt.legend()
    plt.show()

    # question 4:
    np_num_of_neurons = np.array([8, 16, 32, 64])
    np_train_accs_neurons = np.array(
        [train_accs5[-1], train_accs3[-1], train_accs6[-1],
         train_accs7[-1]])
    np_valid_accs_neurons = np.array([val_accs5[-1], val_accs3[-1], val_accs6[-1],
                              val_accs7[-1]])
    np_test_accs_neurons = np.array([test_accs5[-1], test_accs3[-1], test_accs6[-1],
                             test_accs7[-1]])

    plt.figure()
    plt.scatter(np_num_of_neurons, np_train_accs_neurons, label="Train")
    plt.scatter(np_num_of_neurons, np_valid_accs_neurons, label="Validation")
    plt.scatter(np_num_of_neurons, np_test_accs_neurons, label="Test")

    plt.xlabel("Number of neurons")
    plt.ylabel("Accuracy")
    plt.title("Accuracy of the models vs. number of neuron in each "
              "hidden layer")
    plt.legend()
    plt.show()


def task_62_q5(train_data, val_data, test_data):
    output_dim = len(train_data['country'].unique())

    model = [nn.Linear(2, 4), nn.ReLU()]  # hidden layer 1
    for i in range(99):
        model.append(nn.Linear(4, 4))
        model.append(nn.ReLU())

    model.append(nn.Linear(4, output_dim))
    model = nn.Sequential(*model)

    gradient_magnitude_layers = [0, 30, 60, 90, 95, 99]

    model, train_accs, val_accs, test_accs, train_losses, val_losses, \
    test_losses, gradient_magnitude_for_layers = train_model_q5(
        train_data, val_data, test_data, model, gradient_magnitude_layers, epochs=10)

    plt.figure()
    for key, val in gradient_magnitude_for_layers.items():
        label_for_layer = "layer " + str(key)
        plt.plot(val, label=label_for_layer)

    plt.title('gradients magnitude through the training epochs')
    plt.xlabel("Epochs")
    plt.ylabel("gradient magnitude")
    plt.legend()
    plt.show()


def task_62_q7(train_data, val_data, test_data):
    output_dim = len(train_data['country'].unique())

    x_train_data = train_data[['long', 'lat']].values
    y_train_data = train_data[['country']].values.reshape(x_train_data.shape[0], 1)

    x_val_data = val_data[['long', 'lat']].values
    y_val_data = val_data[['country']].values.reshape(x_val_data.shape[0], 1)

    x_test_data = test_data[['long', 'lat']].values
    y_test_data = test_data[['country']].values.reshape(x_test_data.shape[0], 1)

    new_x_train_data = np.zeros((x_train_data.shape[0], x_train_data.shape[1] * 10))
    new_x_val_data = np.zeros((x_val_data.shape[0], x_val_data.shape[1] * 10))
    new_x_test_data = np.zeros((x_test_data.shape[0], x_test_data.shape[1] * 10))


    alphas = np.arange(0.1, 1.1, 0.1)
    for i in range(x_train_data.shape[1]):
        for j, a in enumerate(alphas):
            new_x_train_data[:, i * len(alphas) + j] = np.sin(a * x_train_data[:, i])
            new_x_val_data[:, i * len(alphas) + j] = np.sin(a * x_val_data[:, i])
            new_x_test_data[:, i * len(alphas) + j] = np.sin(a * x_test_data[:, i])


    new_train_data = np.concatenate((new_x_train_data, y_train_data), axis=1)
    new_val_data = np.concatenate((new_x_val_data, y_val_data), axis=1)
    new_test_data = np.concatenate((new_x_test_data, y_test_data), axis=1)

    model1 = [nn.Linear(20, 16), nn.ReLU(),  # hidden layer 1
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 3
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 4
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 5
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 6
              nn.Linear(16, output_dim)  # output layer
              ]
    model1 = nn.Sequential(*model1)
    model1, train_accs, val_accs, test_accs, train_losses, val_losses, \
    test_losses = train_model_q7(new_train_data, new_val_data, new_test_data,
                                 model1)
    plot_decision_boundaries(model1, x_test_data, y_test_data.flatten(),
                             title="Decision boundaries with implicit "
                                   "representation", implicit_repr=True)

    model2 = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 3
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 4
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 5
              nn.Linear(16, 16), nn.ReLU(),  # hidden layer 6
              nn.Linear(16, output_dim)  # output layer
              ]
    model2 = nn.Sequential(*model2)
    model2, train_accs2, val_accs2, test_accs2, train_losses2, val_losses2, \
    test_losses2 = train_model(train_data, val_data, test_data, model2)

    plot_decision_boundaries(model2, x_test_data, y_test_data.flatten(),
                             title="Decision boundaries without implicit "
                                   "representation")


if __name__ == '__main__':
    # seed for reproducibility
    torch.manual_seed(42)
    np.random.seed(42)

    train_data = pd.read_csv('train.csv')
    val_data = pd.read_csv('validation.csv')
    test_data = pd.read_csv('test.csv')

    # output_dim = len(train_data['country'].unique())
    # model = [nn.Linear(2, 16), nn.ReLU(),  # hidden layer 1
    #          nn.Linear(16, 16), nn.ReLU(),  # hidden layer 2
    #          nn.Linear(16, 16), nn.ReLU(),  # hidden layer 3
    #          nn.Linear(16, 16), nn.ReLU(),  # hidden layer 4
    #          nn.Linear(16, 16), nn.ReLU(),  # hidden layer 5
    #          nn.Linear(16, 16), nn.ReLU(),  # hidden layer 6
    #          nn.Linear(16, output_dim)  # output layer
    #          ]
    # model = nn.Sequential(*model)

    # model, train_accs, val_accs, test_accs, train_losses, val_losses, test_losses = train_model(train_data, val_data, test_data, model, lr=0.001, epochs=50, batch_size=256)
    #
    # plt.figure()
    # plt.plot(train_losses, label='Train', color='red')
    # plt.plot(val_losses, label='Val', color='blue')
    # plt.plot(test_losses, label='Test', color='green')
    # plt.title('Losses without batch norm')
    # plt.legend()
    # plt.show()
    #
    # plt.figure()
    # plt.plot(train_accs, label='Train', color='red')
    # plt.plot(val_accs, label='Val', color='blue')
    # plt.plot(test_accs, label='Test', color='green')
    # plt.title('Accuracies without batch norm')
    # plt.legend()
    # plt.show()
    #
    # plot_decision_boundaries(model, test_data[['long', 'lat']].values, test_data['country'].values, 'Decision Boundaries', implicit_repr=False)

    # task_612_q1(train_data, val_data, test_data)

    # task_612_q2(train_data, val_data, test_data)

    # task_612_q3(train_data, val_data, test_data)

    # task_612_q4(train_data, val_data, test_data)

    # task_62(train_data, val_data, test_data)

    # task_62_q5(train_data, val_data, test_data)

    task_62_q7(train_data, val_data, test_data)
