import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from knn import KNNClassifier


def decision_tree_demo():
    # Create random data
    np.random.seed(42)
    X = np.random.rand(100, 2)  # Feature matrix with 100 samples and 2 features
    y = (X[:, 0] + X[:, 1] > 1).astype(int)  # Binary labels based on a simple condition

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize Decision Tree classifier
    tree_classifier = DecisionTreeClassifier(random_state=42)

    # Train the Decision Tree on the training data
    tree_classifier.fit(X_train, y_train)

    # Make predictions on the test data
    y_pred = tree_classifier.predict(X_test)

    # Compute the accuracy of the predictions
    accuracy = np.mean(y_pred == y_test)
    print(f"Accuracy: {accuracy}")


def loading_random_forest():
    model = RandomForestClassifier(n_estimators=300, max_depth=6, n_jobs=4)


def loading_xgboost():
    from xgboost import XGBClassifier
    model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1, n_jobs=4)


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
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h_x), np.arange(y_min, y_max, h_y))

    # Make predictions on the meshgrid points.
    Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
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


def knn_examples(X_train, Y_train, X_test, Y_test):
    """
    Notice the similarity to the decision tree demo above.
    This is the sklearn standard format for models.
    """

    # Initialize the KNNClassifier with k=5 and L2 distance metric
    knn_classifier = KNNClassifier(k=5, distance_metric='l2')

    # Train the classifier
    knn_classifier.fit(X_train, Y_train)

    # Predict the labels for the test set
    y_pred = knn_classifier.predict(X_test)

    # Calculate the accuracy of the classifier
    accuracy = np.mean(y_pred == Y_test)


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


def create_and_print_knn_table(x_train, y_train, x_test, y_test):
    """
    Creates the table needed for task 5.1.
    """
    k_list = [1, 10, 100, 1000, 3000]
    distance_metrics = ["l1", "l2"]

    data_frame = pd.DataFrame(columns=["l1", "l2"],
                              index=["k = 1", "k = 10", "k = 100",
                                     "k = 1000", "k = 3000"])

    for k in k_list:
        for distance_metric in distance_metrics:
            knn_classifier = KNNClassifier(k, distance_metric)
            knn_classifier.fit(x_train, y_train)
            y_pred = knn_classifier.predict(x_test)
            test_accuracy = np.mean(y_pred == y_test)
            data_frame.loc["k = " + str(k), distance_metric] = test_accuracy

    print(data_frame)


def plot_knn_classifier(k, distance_metric, x_train, y_train, x_test, y_test,
                        title):
    """
    creates a KNN classifier with given parameters.
    """
    knn_plot = KNNClassifier(k, distance_metric)
    knn_plot.fit(x_train, y_train)
    plot_decision_boundaries(knn_plot, x_test, y_test, title)


def task_52(x_train, y_train, x_test, y_test):
    """
    visualizations for task 5.2.
    """
    k_max = 1
    k_min = 3000
    plot_knn_classifier(k_max, "l2", x_train, y_train, x_test, y_test,
                        "Decision Bounderies: L2, kMax")
    plot_knn_classifier(k_min, "l2", x_train, y_train, x_test, y_test,
                        "Decision Bounderies: L2, kMin")
    plot_knn_classifier(k_max, "l1", x_train, y_train, x_test, y_test,
                        "Decision Bounderies: L1, kMax")


def task_53(x_train, y_train):
    """
    Visualization for task 5.3 (anomaly detection).
    """
    x_ad_test_data, ad_test_col_names = read_data_demo("AD_test.csv")
    knn_anomaly = KNNClassifier(5, "l2")
    knn_anomaly.fit(x_train, y_train)

    distances, indexes = knn_anomaly.knn_distance(x_ad_test_data)
    anomaly_scores = np.sum(distances, axis=1)
    anomaly_scores_sorted = np.argsort(anomaly_scores)
    ind_highest_anomaly_50 = anomaly_scores_sorted[100:]
    x_highest_anomaly = x_ad_test_data[ind_highest_anomaly_50, :1].flatten()
    y_highest_anomaly = x_ad_test_data[ind_highest_anomaly_50, 1:].flatten()
    plt.scatter(x_highest_anomaly, y_highest_anomaly, color="red")

    plt.scatter(x_train[:, :1], x_train[:, 1:], color="black", alpha=0.01)

    ind_regular_points = anomaly_scores_sorted[:100]
    x_normal_points = x_ad_test_data[ind_regular_points, :1].flatten()
    y_normal_points = x_ad_test_data[ind_regular_points, 1:].flatten()
    plt.scatter(x_normal_points, y_normal_points, color="blue")

    plt.show()


def task_62_1_to_6(X_train, Y_train, X_test, Y_test, X_validation,
                   Y_validation):
    """
    Answers to questions 1 to 6 in task 6.2.
    """
    # Split data into training and validation sets
    max_depth_list = [1, 2, 4, 6, 10, 20, 50, 100]
    max_leaf_nodes_list = [50, 100, 1000]

    data_frame = pd.DataFrame(columns=["Depth", "Nodes", "Train",
                                       "Validation", "Test"])

    trees = []
    accuracies = []

    for depth in max_depth_list:
        for leaf_nodes in max_leaf_nodes_list:
            # Initialize Decision Tree classifier
            tree_classifier = DecisionTreeClassifier(
                max_depth=depth, max_leaf_nodes=leaf_nodes, random_state=42)

            # Train the Decision Tree on the training data
            tree_classifier.fit(X_train, Y_train)
            trees.append(tree_classifier)

            # Make predictions on the test data
            y_train_pred = tree_classifier.predict(X_train)
            y_valid_pred = tree_classifier.predict(X_validation)
            y_test_pred = tree_classifier.predict(X_test)


            # Compute the accuracy of the predictions
            train_accuracy = np.mean(y_train_pred == Y_train)
            valid_accuracy = np.mean(y_valid_pred == Y_validation)
            test_accuracy = np.mean(y_test_pred == Y_test)
            accuracies.append([train_accuracy, valid_accuracy, test_accuracy])

            data_frame.loc[len(data_frame)] = [depth, leaf_nodes,
                                               train_accuracy, valid_accuracy,
                                               test_accuracy]


    data_frame["Depth"] = data_frame["Depth"].astype(int)
    data_frame["Nodes"] = data_frame["Nodes"].astype(int)
    print("Results for question 1:")
    print(data_frame)

    plot_decision_boundaries(trees[17], X_test, Y_test,
                             "Decision boundaries: best validation accuracy "
                             "tree")

    plot_decision_boundaries(trees[15], X_test, Y_test,
                             "Decision boundaries: best validation accuracy "
                             "tree for 50 leaf nodes")

    plot_decision_boundaries(trees[9], X_test, Y_test,
                             "Decision boundaries: best validation accuracy "
                             "tree depth of at most 6")


def task_62_7(X_train, Y_train, X_test, Y_test, X_validation, Y_validation):
    """
    Answers to question 7 in task 6.2.
    """
    model = RandomForestClassifier(n_estimators=300, max_depth=6, n_jobs=4)
    model.fit(X_train, Y_train)

    # Make predictions on the test data
    y_train_pred = model.predict(X_train)
    y_valid_pred = model.predict(X_validation)
    y_test_pred = model.predict(X_test)

    # Compute the accuracy of the predictions
    train_accuracy = np.mean(y_train_pred == Y_train)
    valid_accuracy = np.mean(y_valid_pred == Y_validation)
    test_accuracy = np.mean(y_test_pred == Y_test)

    print("The train accuracy of the random forest is:", train_accuracy)
    print("The validation accuracy of the random forest is:", valid_accuracy)
    print("The test accuracy of the random forest is:", test_accuracy)
    plot_decision_boundaries(model, X_test, Y_test, "Decision boundaries: "
                                                    "random forest")


def task_62_8(X_train, Y_train, X_test, Y_test):
    """
    Answer to question 8 in task 6.2.
    """
    from xgboost import XGBClassifier
    model = XGBClassifier(n_estimators=300, max_depth=6, learning_rate=0.1,
                          n_jobs=4)
    model.fit(X_train, Y_train)
    y_test_pred = model.predict(X_test)
    test_accuracy = np.mean(y_test_pred == Y_test)
    print("The test accuracy of the XGBoost model is:", test_accuracy)
    plot_decision_boundaries(model, X_test, Y_test, "Decision boundaries: "
                                                    "XGBoost")


if __name__ == '__main__':
    np.random.seed(0)  # DO NOT TOUCH OR MOVE!


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
    Y_validation.shape = Y_validation.shape[0]

    print(f'Results for task 5.1:')
    create_and_print_knn_table(X_train, Y_train, X_test, Y_test)

    task_52(X_train, Y_train, X_test, Y_test)

    task_53(X_train, Y_train)
    print(f'Results for task 6.2 questions:')
    task_62_1_to_6(X_train, Y_train, X_test, Y_test, X_validation,
                   Y_validation)
    print(f'Results for task 6.2 question 7:')
    task_62_7(X_train, Y_train, X_test, Y_test, X_validation, Y_validation)

    print(f'Results for task 6.2 question 8:')
    task_62_8(X_train, Y_train, X_test, Y_test)









