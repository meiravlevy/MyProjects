from classifiers import Perceptron, LDA, GaussianNaiveBayes
from typing import Tuple
from utils import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import atan2, pi
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


def load_dataset(filename: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load dataset for comparing the Gaussian Naive Bayes and LDA classifiers. File is assumed to be an
    ndarray of shape (n_samples, 3) where the first 2 columns represent features and the third column the class

    Parameters
    ----------
    filename: str
        Path to .npy data file

    Returns
    -------
    X: ndarray of shape (n_samples, 2)
        Design matrix to be used

    y: ndarray of shape (n_samples,)
        Class vector specifying for each sample its class

    """
    data = np.load(filename)
    return data[:, :2], data[:, 2].astype(int)


def run_perceptron():
    """
    Fit and plot fit progression of the Perceptron algorithm over both the linearly separable and inseparable datasets

    Create a line plot that shows the perceptron algorithm's training loss values (y-axis)
    as a function of the training iterations (x-axis).
    """
    for n, f in [("Linearly Separable", "linearly_separable.npy"), ("Linearly Inseparable", "linearly_inseparable.npy")]:
        # Load dataset
        X, y = load_dataset(f)
        # Fit Perceptron and record loss in each fit iteration
        losses = []
        def fit_iterations_loss_callback(
                fit: Perceptron, new_X: np.ndarray, new_y: np.ndarray):
            loss = fit.loss(new_X, new_y)
            losses.append(loss)
        perceptron = Perceptron(callback=fit_iterations_loss_callback)
        perceptron.fit(X, y)

        # Plot figure of loss as function of fitting iteration
        x_plot = range(len(losses))
        plt.plot(x_plot, losses)
        plt.xlabel("Iteration")
        plt.ylabel("Loss")
        plt.margins(x=0)
        plt.title(n + ": Perceptron algorithm training loss")
        plt.savefig("31_" + n + "_perceptron_loss")
        plt.close()

def get_ellipse(mu: np.ndarray, cov: np.ndarray):
    """
    Draw an ellipse centered at given location and according to specified covariance matrix

    Parameters
    ----------
    mu : ndarray of shape (2,)
        Center of ellipse

    cov: ndarray of shape (2,2)
        Covariance of Gaussian

    Returns
    -------
        scatter: A plotly trace object of the ellipse
    """

    l1, l2 = tuple(np.linalg.eigvalsh(cov)[::-1])
    theta = atan2(l1 - cov[0, 0], cov[0, 1]) if cov[0, 1] != 0 else (np.pi / 2 if cov[0, 0] < cov[1, 1] else 0)
    t = np.linspace(0, 2 * pi, 100)
    xs = (l1 * np.cos(theta) * np.cos(t)) - (l2 * np.sin(theta) * np.sin(t))
    ys = (l1 * np.sin(theta) * np.cos(t)) + (l2 * np.cos(theta) * np.sin(t))

    return go.Scatter(x=mu[0] + xs, y=mu[1] + ys, mode="lines", marker_color="black")

def get_ellipse_using_matplotlib(ax, mu: np.ndarray, cov: np.ndarray):
    """
    Draw an ellipse centered at given location and according to specified
    covariance matrix using matplotlib

    Parameters
    ----------
    mu : ndarray of shape (2,)
        Center of ellipse

    cov: ndarray of shape (2,2)
        Covariance of Gaussian

    Returns
    -------
        None
    """

    # Eigenvalues of the covariance matrix
    l1, l2 = tuple(np.linalg.eigvalsh(cov)[::-1])

    # Angle of rotation of ellipse
    theta = atan2(l1 - cov[0, 0], cov[0, 1]) if cov[0, 1] != 0 else \
        (np.pi / 2 if cov[0, 0] < cov[1, 1] else 0)

    # Generate points for the ellipse
    t = np.linspace(0, 2 * pi, 100)
    xs = (l1 * np.cos(theta) * np.cos(t)) - (l2 * np.sin(theta) * np.sin(t))
    ys = (l1 * np.sin(theta) * np.cos(t)) + (l2 * np.cos(theta) * np.sin(t))

    # Create the plot
    ax.plot(mu[0] + xs, mu[1] + ys, 'k')  # 'k' is the color black


def plot_model_preds(ax, X, y, preds):
    """
    Plots model's(Gaussian Naive Bayes or LDA) predictions over the dataset
    with marker shape indicating the true class and marker color indicating the
    predicted class.
    Parameters
    ----------
    ax : the plot of the model
    X : The samples features
    y : the labels of the samples
    preds : the predictions of the model.

    Returns
    -------
        None
    """
    cmap = ListedColormap(
        plt.cm.tab10.colors[:len(np.unique(preds))])
    for true_cls in np.unique(y):
        for pred_cls in np.unique(preds):
            X_cls = X[(y == true_cls) &
                               (preds == pred_cls)]
            if (len(X_cls) > 0):
                marker = plt.Line2D.filled_markers[
                    true_cls % len(plt.Line2D.filled_markers)]
                color = cmap(pred_cls)
                ax.scatter(X_cls[:, 0], X_cls[:, 1],
                           c=np.array([color]), marker=marker)

def compare_gaussian_classifiers():
    """
    Fit both Gaussian Naive Bayes and LDA classifiers on both gaussians1 and gaussians2 datasets
    """
    for f in ["gaussian1.npy", "gaussian2.npy"]:
        # Load dataset
        X, y = load_dataset(f)

        # Fit models and predict over training set
        gaussian_naive_bayes = GaussianNaiveBayes()
        gaussian_preds = gaussian_naive_bayes.fit_predict(X, y)

        lda = LDA()
        lda_preds = lda.fit_predict(X, y)

        # Plot a figure with two suplots, showing the Gaussian Naive Bayes predictions on the left and LDA predictions
        # on the right. Plot title should specify dataset used and subplot titles should specify algorithm and accuracy
        # Create subplots
        from loss_functions import accuracy
        fig, (gaussian_ax, lda_ax) = plt.subplots(1, 2, figsize=(10, 5))
        dataset_name = f.split('.')[0]
        fig.suptitle("Comparing Gaussian Classifiers over " + dataset_name +
                     " dataset:\n")
        plt.subplots_adjust(top=0.85, bottom=0.15, left=0.10, right=0.95,
                            hspace=0.3, wspace=0.3)

        gaussian_ax.set_title("Gaussian Naive Bayes - accuracy=" +
                              str(round(accuracy(y, gaussian_preds), 4) * 100)
                              + "%")

        lda_ax.set_title("LDA - accuracy=" +
                         str(round(accuracy(y, lda_preds), 4) * 100) + "%")


        # Add traces for data-points setting symbols and colors
        plot_model_preds(gaussian_ax, X, y, gaussian_preds)
        plot_model_preds(lda_ax, X, y, lda_preds)

        # Add `X` dots specifying fitted Gaussians' means
        for cls in lda.classes_:
            lda_ax.scatter(lda.mu_[cls][0], lda.mu_[cls][1], marker='x',
                           color="k", s=80, linewidth=4)
            gaussian_ax.scatter(gaussian_naive_bayes.mu_[cls][0],
                                gaussian_naive_bayes.mu_[cls][1], marker='x',
                                color="k", s=80, linewidth=4)

        # Add ellipses depicting the covariances of the fitted Gaussians
        for cls in lda.classes_:
            # in naive bayes classifiers we assume that the features are
            # are independent and so the covariance matrix will be a diagonal
            # matrix where the diagonal is the estimated variances.
            cov_cls_gaussian = np.diag(gaussian_naive_bayes.vars_[cls])
            get_ellipse_using_matplotlib(gaussian_ax,
                                         gaussian_naive_bayes.mu_[cls],
                                         cov_cls_gaussian)
            get_ellipse_using_matplotlib(lda_ax, lda.mu_[cls], lda.cov_)

        plt.savefig("32_" + dataset_name + "_plot.jpg")
        plt.close()


if __name__ == '__main__':
    np.random.seed(0)
    # run_perceptron()
    compare_gaussian_classifiers()
