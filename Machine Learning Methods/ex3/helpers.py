import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from models import *
from torch import optim


def plot_decision_boundaries(model, X, y, title='Decision Boundaries'):
    """
    Plots decision boundaries of a classifier and colors the space by the prediction of each point.

    Parameters:
    - model: The trained classifier (sklearn model).
    - X: Numpy Feature matrix.
    - y: Numpy array of Labels.
    - title: Title for the plot.
    """
    # h = .02  # Step size in the mesh

    # enumerate y
    y_map = {v: i for i, v in enumerate(np.unique(y))}
    enum_y = np.array([y_map[v] for v in y]).astype(int)

    h_x = (np.max(X[:, 0]) - np.min(X[:, 0])) / 200
    h_y = (np.max(X[:, 1]) - np.min(X[:, 1])) / 200

    # Plot the decision boundary.
    added_margin_x = h_x * 20
    added_margin_y = h_y * 20
    x_min, x_max = X[:, 0].min() - added_margin_x, X[:, 0].max() + added_margin_x
    y_min, y_max = X[:, 1].min() - added_margin_y, X[:, 1].max() + added_margin_y
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h_x), np.arange(y_min, y_max, h_y))

    # Make predictions on the meshgrid points.
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
    print(Z.shape)
    Z = np.array([y_map[v] for v in Z])
    Z = Z.reshape(xx.shape)
    vmin = np.min([np.min(enum_y), np.min(Z)])
    vmax = np.min([np.max(enum_y), np.max(Z)])

    # Plot the decision boundary.
    plt.contourf(xx, yy, Z, cmap=plt.cm.Paired, alpha=0.8, vmin=vmin, vmax=vmax)

    # Scatter plot of the data points with matching colors.
    plt.scatter(X[:, 0], X[:, 1], c=enum_y, cmap=plt.cm.Paired, edgecolors='k', s=40, alpha=0.7, vmin=vmin, vmax=vmax)

    plt.title("Decision Boundaries")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    plt.show()


def read_data_demo(filename='train.csv'):
    """
    Read the data from the csv file and return the features and labels as numpy arrays.
    """

    # the data in pandas dataframe format
    df = pd.read_csv(filename)

    # extract the column names
    col_names = list(df.columns)

    # the data in numpy array format
    data_numpy = df.values

    return data_numpy, col_names


def task_6(x_train, y_train, x_validation, y_validation, x_test, y_test):
    """
    Trains a ridge regression model and answers the questions of task 6.
    """
    ridge_lambds = [0., 2., 4., 6., 8., 10.]
    train_accuracies = []
    validation_accuracies = []
    test_accuracies = []

    for lambd in ridge_lambds:
        ridge_model = Ridge_Regression(lambd)
        ridge_model.fit(x_train, y_train)
        y_train_preds = ridge_model.predict(x_train)
        y_validation_preds = ridge_model.predict(x_validation)
        y_test_preds = ridge_model.predict(x_test)

        train_accuracy = np.mean(y_train_preds == y_train)
        validation_accuracy = np.mean(y_validation_preds == y_validation)
        test_accuracy = np.mean(y_test_preds == y_test)

        train_accuracies.append(train_accuracy)
        validation_accuracies.append(validation_accuracy)
        test_accuracies.append(test_accuracy)

    plt.plot(ridge_lambds, train_accuracies, marker="o",
             label="Training accuracy")
    plt.plot(ridge_lambds, validation_accuracies, marker="o",
             label="validation accuracy")
    plt.plot(ridge_lambds, test_accuracies, marker="o",
             label="test accuracy")

    plt.xlabel("lambda")
    plt.ylabel("accuracy")
    plt.title("accuracies of the model vs. their lambds value")
    plt.legend()
    plt.show()

    print("Answer for question 1:")
    print("The test accuracy of the best model(where lambda is 4) is:",
          test_accuracies[2])
    best_lambd_model = Ridge_Regression(4.)
    best_lambd_model.fit(x_train, y_train)
    plot_decision_boundaries(best_lambd_model, x_test, y_test,
                             "Decision Boundaries: best lambd")

    worst_lambd_model = Ridge_Regression(10.)
    worst_lambd_model.fit(x_train, y_train)
    plot_decision_boundaries(worst_lambd_model, x_test, y_test,
                             "Decision Boundaries: worst lambd")


def task_7():
    x_var = np.poly1d([1, -6, 9])
    y_var = np.poly1d([1, -10, 25])
    derivative_x = x_var.deriv()
    derivative_y = y_var.deriv()

    x_y_values = [(0., 0.)]
    for i in range(1000):
        last_x_value = x_y_values[len(x_y_values) - 1][0]
        last_y_value = x_y_values[len(x_y_values) - 1][1]
        plt.plot(last_x_value, last_y_value, marker="o")

        x_y_values.append((last_x_value - 0.1 * derivative_x(last_x_value),
                           last_y_value - 0.1 * derivative_y(last_y_value)))

    plt.title("Optimized vector through iterations")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.show()


def compute_accuracy_and_loss(loader, device, model, criterion, len_data_set):
    """
    computes the accuracy and loss of model on the given data set.
    Args:
        loader: the loader of the data set.
        device: "cuda" or cpu.
        model: the trained model to check accuracies and loss with.
        criterion: the loss function.
        len_data_set: the length of the data set.

    Returns: the loss and accuracy of the data set.

    """
    correct_predictions = 0.
    loss_values = []
    for inputs, labels in loader:
        inputs, labels = inputs.to(device), labels.to(device)
        labels = torch.flatten(labels)
        outputs = model(inputs.float())
        outputs = nn.functional.softmax(outputs, dim=-1)
        loss = criterion(outputs.squeeze(), labels.long())
        _, predicted = torch.max(outputs, dim=-1)
        loss_values.append(loss.item())
        correct_predictions += torch.sum(predicted == labels).item()
    mean_loss = np.round(np.mean(loss_values), decimals=4)
    return np.round((correct_predictions / len_data_set), decimals=4), \
        mean_loss


def task_93(x_train, y_train, x_validation, y_validation, x_test, y_test):
    """
    Trains a logistic regression model and answers question 1 and 2 of task
    9.3.
    Args:
        x_train: the features of the binary-case training set.
        y_train: the labels of the binary-case training set.
        x_validation: the features of the binary-case validation set.
        y_validation: the labels of the binary-case validation set.
        x_test: the features of the binary-case test set.
        y_test: the labels of the binary-case test set
    """
    list_of_data_frames = []
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    learning_rates = [0.1, 0.01, 0.001]

    x_train_tensor = torch.tensor(x_train, dtype=torch.float32).to(device)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).to(device)
    train_data_set = torch.utils.data.TensorDataset(x_train_tensor,
                                                    y_train_tensor)
    train_loader = torch.utils.data.DataLoader(
        train_data_set, batch_size=32, shuffle=True)

    x_validation_tensor = torch.tensor(x_validation,
                                       dtype=torch.float32).to(device)
    y_validation_tensor = torch.tensor(y_validation,
                                       dtype=torch.float32).to(device)
    validation_data_set = torch.utils.data.TensorDataset(x_validation_tensor,
                                                         y_validation_tensor)
    validation_loader = torch.utils.data.DataLoader(
        validation_data_set, batch_size=32, shuffle=False)

    x_test_tensor = torch.tensor(x_test, dtype=torch.float32).to(device)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).to(device)
    test_data_set = torch.utils.data.TensorDataset(x_test_tensor,
                                                   y_test_tensor)
    test_loader = torch.utils.data.DataLoader(
        test_data_set, batch_size=32, shuffle=False)

    models = []
    models_losses = []

    for lr in learning_rates:
        model = Logistic_Regression(2, 2)
        model.to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=lr)
        data_frame = pd.DataFrame(columns=["Epoch", "Train accuracy",
                                           "Validation accuracy",
                                           "Test accuracy"])
        ep_train_loss_values = []
        ep_validation_loss_values = []
        ep_test_loss_values = []

        for epoch in range(1, 11):
            train_loss_values = []
            ep_correct_preds = 0.
            model.train()  # set the model to training mode
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                labels = torch.flatten(labels)
                optimizer.zero_grad()
                outputs_train = model(inputs.float())
                loss = criterion(outputs_train.squeeze(), labels.long())
                loss.backward()
                optimizer.step()

                train_loss_values.append(loss.item())
                ep_correct_preds += torch.sum(
                    torch.argmax(outputs_train, dim=1) == labels).item()

            train_mean_loss = np.round(np.mean(train_loss_values), decimals=4)
            train_accuracy = np.round(ep_correct_preds / len(train_data_set),
                                      decimals=4)
            ep_train_loss_values.append(train_mean_loss)

            validation_accuracy, validation_mean_loss = \
                compute_accuracy_and_loss(validation_loader, device, model,
                                          criterion, len(validation_data_set))
            ep_validation_loss_values.append(validation_mean_loss)

            test_accuracy, test_mean_loss = compute_accuracy_and_loss(
                test_loader, device, model, criterion, len(test_data_set))
            ep_test_loss_values.append(test_mean_loss)

            data_frame.loc[epoch] = [epoch, train_accuracy,
                                     validation_accuracy, test_accuracy]

        list_of_data_frames.append(data_frame)
        models.append(model)
        models_losses.append([ep_train_loss_values,
                              ep_validation_loss_values,
                              ep_test_loss_values])

    for df in list_of_data_frames:
        print(df)
    # question 1:
    plot_decision_boundaries(models[2], x_test, y_test,
                             title="Decision boundaries for "
                                   "best model(lr = 0.001)")
    # question 2:
    plt.plot(models_losses[2][0], marker='o', label="Train loss")
    plt.plot(models_losses[2][1], marker='o', label="Validation loss")
    plt.plot(models_losses[2][2], marker='o', label="Test loss")

    plt.xlabel('Epochs')
    plt.ylabel('Loss Value')
    plt.title('Loss Progression')
    plt.legend()
    plt.show()


def task_94(x_train, y_train, x_validation, y_validation, x_test, y_test):
    """
    Trains a logistic regression model and answers question 1 and 2 of task
    9.4.
    Args:
        x_train: the features of the multi-class training set.
        y_train: the labels of the multi-class training set.
        x_validation: the features of the multi-class validation set.
        y_validation: the labels of the multi-class validation set.
        x_test: the features of the multi-class test set.
        y_test: the labels of the multi-class test set
    """
    list_of_data_frames = []
    learning_rates = [0.01, 0.001, 0.0003]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    x_train_tensor = torch.tensor(x_train, dtype=torch.float32).to(device)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).to(device)
    train_multi_data_set = torch.utils.data.TensorDataset(x_train_tensor,
                                                          y_train_tensor)
    train_loader = torch.utils.data.DataLoader(
        train_multi_data_set, batch_size=32, shuffle=True)

    x_validation_tensor = torch.tensor(x_validation,
                                       dtype=torch.float32).to(device)
    y_validation_tensor = torch.tensor(y_validation,
                                       dtype=torch.float32).to(device)
    validation_data_set = torch.utils.data.TensorDataset(x_validation_tensor,
                                                         y_validation_tensor)
    validation_loader = torch.utils.data.DataLoader(
        validation_data_set, batch_size=32, shuffle=False)

    x_test_tensor = torch.tensor(x_test, dtype=torch.float32).to(device)
    y_test_tensor = torch.tensor(y_test, dtype=torch.float32).to(device)
    test_data_set = torch.utils.data.TensorDataset(x_test_tensor,
                                                   y_test_tensor)
    test_loader = torch.utils.data.DataLoader(
        test_data_set, batch_size=32, shuffle=False)

    models = []
    models_losses = []
    n_classes = len(torch.unique(train_multi_data_set.tensors[-1]))
    for lr in learning_rates:
        model = Logistic_Regression(2, n_classes)
        model.to(device)
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=lr)
        lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=5,
                                                       gamma=0.3)
        data_frame = pd.DataFrame(columns=["Lr", "Epoch", "Train accuracy",
                                           "Validation accuracy",
                                           "Test accuracy"])
        ep_train_loss_values = []
        ep_validation_loss_values = []
        ep_test_loss_values = []

        for epoch in range(1, 31):
            train_loss_values = []
            ep_correct_preds = 0.
            model.train()  # set the model to training mode
            for inputs, labels in train_loader:
                labels = torch.flatten(labels)
                inputs, labels = inputs.to(device), labels.to(device)
                optimizer.zero_grad()
                outputs_train = model(inputs.float())
                loss = criterion(outputs_train.squeeze(),  labels.long())
                loss.backward()
                optimizer.step()

                train_loss_values.append(loss.item())
                ep_correct_preds += torch.sum(
                    torch.argmax(outputs_train, dim=1) == labels).item()
            lr_scheduler.step()

            train_mean_loss = np.round(np.mean(train_loss_values), decimals=4)
            train_accuracy = np.round(
                ep_correct_preds / len(train_multi_data_set),decimals=4)
            ep_train_loss_values.append(train_mean_loss)

            validation_accuracy, validation_mean_loss = \
                compute_accuracy_and_loss(validation_loader, device, model,
                                          criterion, len(validation_data_set))
            ep_validation_loss_values.append(validation_mean_loss)

            test_accuracy, test_mean_loss = compute_accuracy_and_loss(
                test_loader, device, model, criterion, len(test_data_set))
            ep_test_loss_values.append(test_mean_loss)

            data_frame.loc[epoch] = [lr, epoch, train_accuracy,
                                     validation_accuracy, test_accuracy]

        list_of_data_frames.append(data_frame)
        models.append(model)
        models_losses.append([ep_train_loss_values,
                              ep_validation_loss_values,
                              ep_test_loss_values])

    # for df in list_of_data_frames:
    #     print(df)

    # question 1:
    validation_y = [list_of_data_frames[0]["Validation accuracy"].iloc[-1],
                    list_of_data_frames[1]["Validation accuracy"].iloc[-1],
                    list_of_data_frames[2]["Validation accuracy"].iloc[-1]]

    test_y = [list_of_data_frames[0]["Test accuracy"].iloc[-1],
              list_of_data_frames[1]["Test accuracy"].iloc[-1],
              list_of_data_frames[2]["Test accuracy"].iloc[-1]]

    plt.plot(learning_rates, validation_y, marker="o",
             label="Validation accuracy")
    plt.plot(learning_rates, test_y, marker="o", label="Test accuracy")

    plt.title("Test and validation accuracies vs. their learning rate")
    plt.xlabel("learning rate")
    plt.ylabel("accuracy")
    plt.legend()
    plt.show()

    print("Test accuracy of best model(where learning rate = 0.01 is:",
          list_of_data_frames[0]["Test accuracy"].iloc[-1])

    # question 2:
    plt.plot(models_losses[0][0], marker='o', label="Train loss")
    plt.plot(models_losses[0][1], marker='o', label="Validation loss")
    plt.plot(models_losses[0][2], marker='o', label="Test loss")

    plt.xlabel('Epochs')
    plt.ylabel('Loss Value')
    plt.title('Loss Progression over the training epochs')
    plt.legend()
    plt.show()

    plt.plot(list_of_data_frames[0]["Train accuracy"], marker='o',
             label="Train accuracy")
    plt.plot(list_of_data_frames[0]["Validation accuracy"], marker='o',
             label="Validation accuracy")
    plt.plot(list_of_data_frames[0]["Test accuracy"], marker='o',
             label="Test accuracy")

    plt.xlabel('Epochs')
    plt.ylabel('accuracy')
    plt.title('accuracies in training epochs')
    plt.legend()
    plt.show()


def task_94_trees(x_train_multi, y_train_multi, x_test_multi, y_test_multi,
                  depth):
    """
    Plots the tree for wuestion 3 and for of task 9.4.
    Args:
        x_train_multi: the features of the multi-class training set.
        y_train_multi: the labels of the multi-class training set.
        x_test_multi: the features of the multi-class test set.
        y_test_multi: the labels of the multi-class test set.
        depth: the max depth for the tree model
    """
    tree_classifier = DecisionTreeClassifier(max_depth=depth, random_state=42)
    tree_classifier.fit(x_train_multi, y_train_multi)
    y_pred = tree_classifier.predict(x_test_multi)
    accuracy = np.mean(y_pred == np.squeeze(y_test_multi))
    print("The tree accuracy with depth " + str(depth) + " is: " + str(accuracy))
    plot_decision_boundaries(tree_classifier, x_test_multi,
                             np.squeeze(y_test_multi),
                             "Decision boundaries: tree with max depth " +
                             str(depth))


if __name__ == '__main__':
    np.random.seed(42)
    torch.manual_seed(42)
    train_data, train_col_names = read_data_demo()
    X_train = train_data[:, :2]
    Y_train = train_data[:, 2:].astype(int)
    # turn the array of labels into a size of (N,)
    Y_train.shape = Y_train.shape[0]

    test_data, test_col_names = read_data_demo("test.csv")
    X_test = test_data[:, :2]
    Y_test = test_data[:, 2:].astype(int)
    # turn the array of labels into a size of (N,)
    Y_test.shape = Y_test.shape[0]

    validation_data, validation_col_names = read_data_demo("validation.csv")
    X_validation = validation_data[:, :2]
    Y_validation = validation_data[:, 2:].astype(int)
    # turn the array of labels into a size of (N,)
    Y_validation.shape = Y_validation.shape[0]

    print("results for task 6.2: ")
    task_6(X_train, Y_train, X_validation, Y_validation, X_test, Y_test)

    task_7()

    task_93(X_train, Y_train, X_validation, Y_validation, X_test, Y_test)

    train_multi_data, train_multi_col_names = read_data_demo(
        "train_multiclass.csv")
    X_train_multi = train_multi_data[:, :2]
    Y_train_multi = train_multi_data[:, 2:].astype(int)

    validation_multi_data, validation_multi_col_names = read_data_demo(
        "validation_multiclass.csv")
    X_validation_multi = validation_multi_data[:, :2]
    Y_validation_multi = validation_multi_data[:, 2:].astype(int)

    test_multi_data, test_multi_col_names = read_data_demo(
        "test_multiclass.csv")
    X_test_multi = test_multi_data[:, :2]
    Y_test_multi = test_multi_data[:, 2:].astype(int)

    task_94(X_train_multi, Y_train_multi, X_validation_multi,
            Y_validation_multi, X_test_multi, Y_test_multi)

    task_94_trees(X_train_multi, Y_train_multi, X_test_multi, Y_test_multi, 2)
    task_94_trees(X_train_multi, Y_train_multi, X_test_multi, Y_test_multi, 10)









