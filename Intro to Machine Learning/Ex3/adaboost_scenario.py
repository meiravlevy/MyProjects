import numpy as np
from typing import Tuple
from utils import *
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from adaboost import AdaBoost
from decision_stump import DecisionStump

import matplotlib.pyplot as plt


def generate_data(n: int, noise_ratio: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate a dataset in R^2 of specified size

    Parameters
    ----------
    n: int
        Number of samples to generate

    noise_ratio: float
        Ratio of labels to invert

    Returns
    -------
    X: np.ndarray of shape (n_samples,2)
        Design matrix of samples

    y: np.ndarray of shape (n_samples,)
        Labels of samples
    """
    '''
    generate samples X with shape: (num_samples, 2) and labels y with shape (num_samples).
    num_samples: the number of samples to generate
    noise_ratio: invert the label for this ratio of the samples
    '''
    X, y = np.random.rand(n, 2) * 2 - 1, np.ones(n)
    y[np.sum(X ** 2, axis=1) < 0.5 ** 2] = -1
    y[np.random.choice(n, int(noise_ratio * n))] *= -1
    return X, y


def fit_and_evaluate_adaboost(noise, n_learners=250, train_size=5000, test_size=500):
    (train_X, train_y), (test_X, test_y) = generate_data(train_size, noise), generate_data(test_size, noise)
    noise_str = "".join(str(noise).split("."))

    # Question 1: Train- and test errors of AdaBoost in noiseless case
    adaboost = AdaBoost(DecisionStump, n_learners)
    adaboost.fit(train_X, train_y)
    train_loss = []
    test_loss = []
    for i in range(1, n_learners + 1):
        train_loss.append(adaboost.partial_loss(train_X, train_y, i))
        test_loss.append(adaboost.partial_loss(test_X, test_y, i))
    x_ticks = np.arange(1, n_learners + 1)
    plt.plot(x_ticks, train_loss, label="Training error")
    plt.plot(x_ticks, test_loss, label="Test error")
    plt.xlabel("Iteration")
    plt.ylabel("Misclassification error")
    plt.margins(x=0)
    plt.title("AdaBoost Misclassification error as function of the\n "
              "number of fitted learners")
    plt.legend()
    plt.savefig("311_" + noise_str + "_adaboost_error.jpg")
    plt.close()



    # Question 2: Plotting decision surfaces
    T = [5, 50, 100, 250]
    lims = np.array([np.r_[train_X, test_X].min(axis=0),
                     np.r_[train_X, test_X].max(axis=0)]).T \
           + np.array([-.1, .1])

    fig_iterations = make_subplots(rows=1, cols=4,
                        subplot_titles=[f"Iteration {iteration}" for iteration in T])
    for i, iteration in enumerate(T):
        surface = decision_surface(
            lambda X: adaboost.partial_predict(X, iteration), lims[0, :],
            lims[1, :], showscale=False)
        fig_iterations.add_trace(surface, row=1, col=i + 1)
        scatter = go.Scatter(x=test_X[:, 0], y=test_X[:, 1], mode='markers',
                             marker=dict(color=test_y,
                             symbol=class_symbols[(test_y + 1).astype(int) // 2],
                             colorscale=custom), showlegend=False)
        fig_iterations.add_trace(scatter, row=1, col=i + 1)

    fig_iterations.update_layout(
        title="Decision Boundaries of AdaBoost using the ensamble at "
              "Different Iterations",
        title_x=0.5,
        height=400,
        width=1600,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    fig_iterations.update_xaxes(visible=False)
    fig_iterations.update_yaxes(visible=False)
    pio.write_html(fig_iterations, "312_" + noise_str + "_decision_boundaries_plotly.html")


    # Question 3: Decision surface of best performing ensemble
    best_test_error = np.inf
    best_ensemble_size = 0
    for i in range(1, n_learners + 1):
        test_error = adaboost.partial_loss(test_X, test_y, i)
        if test_error < best_test_error:
            best_test_error = test_error
            best_ensemble_size = i

    best_ensemble_accuracy = 1 - best_test_error
    train_surface = decision_surface(
        lambda X: adaboost.partial_predict(X, best_ensemble_size), lims[0, :],
        lims[1, :], showscale=False)

    test_scatter = go.Scatter(x=test_X[:, 0], y=test_X[:, 1], mode='markers',
                         marker=dict(color=test_y,
                                     symbol=class_symbols[(test_y + 1).astype(int) // 2],
                                     colorscale=custom), showlegend=False)
    fig_best = go.Figure(data=[train_surface, test_scatter])
    fig_best.update_layout(
        title='Best ensemble: <br>size: ' + str(best_ensemble_size)
        + ", accuracy: " + str(best_ensemble_accuracy),
        title_x=0.5, height=600, width=600)
    fig_best.update_xaxes(visible=False)
    fig_best.update_yaxes(visible=False)
    pio.write_html(fig_best, "313_" + noise_str + "_best_ensemble.html")


    # Question 4: Decision surface with weighted samples
    last_weights_normalized = (adaboost.D_[-1] / np.max(adaboost.D_[-1])) * 5
    last_train_surface = decision_surface(
        lambda X: adaboost.partial_predict(X, n_learners), lims[0, :],
        lims[1, :], showscale=False)
    last_train_scatter = go.Scatter(
        x=train_X[:, 0],
        y=train_X[:, 1],
        mode='markers',
        marker=dict(
            size=last_weights_normalized,
            color=train_y,
            symbol=class_symbols[(train_y + 1).astype(int) // 2]
        )
    )
    fig_last = go.Figure(data=[last_train_surface, last_train_scatter])
    fig_last.update_layout(title="Adaboost Last Iteration:<br> "
                            "Train set with point size proportional to it's weight",
        title_x=0.5, height=600, width=600)
    fig_last.update_xaxes(visible=False)
    fig_last.update_yaxes(visible=False)
    pio.write_html(fig_last, "314_" + noise_str + "_last_iteration_ensemble.html")


if __name__ == '__main__':
    np.random.seed(0)
    fit_and_evaluate_adaboost(0)
    fit_and_evaluate_adaboost(0.4)
