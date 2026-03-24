import numpy as np
import pandas as pd
from typing import Tuple, List, Callable, Type

from base_module import BaseModule
from base_learning_rate import BaseLR
from gradient_descent import GradientDescent
from learning_rate import FixedLR



# from IMLearn.desent_methods import GradientDescent, FixedLR, ExponentialLR
from modules import L1, L2
from logistic_regression import LogisticRegression
from utils import split_train_test

import plotly.graph_objects as go

import matplotlib.pyplot as plt

from sklearn.metrics import roc_curve, auc
from cross_validate import *
from loss_functions import misclassification_error


def plot_descent_path(module: Type[BaseModule],
                      descent_path: np.ndarray,
                      title: str = "",
                      xrange=(-1.5, 1.5),
                      yrange=(-1.5, 1.5)) -> go.Figure:
    """
    Plot the descent path of the gradient descent algorithm

    Parameters:
    -----------
    module: Type[BaseModule]
        Module type for which descent path is plotted

    descent_path: np.ndarray of shape (n_iterations, 2)
        Set of locations if 2D parameter space being the regularization path

    title: str, default=""
        Setting details to add to plot title

    xrange: Tuple[float, float], default=(-1.5, 1.5)
        Plot's x-axis range

    yrange: Tuple[float, float], default=(-1.5, 1.5)
        Plot's x-axis range

    Return:
    -------
    fig: go.Figure
        Plotly figure showing module's value in a grid of [xrange]x[yrange] over which regularization path is shown

    Example:
    --------
    fig = plot_descent_path(IMLearn.desent_methods.modules.L1, np.ndarray([[1,1],[0,0]]))
    fig.show()
    """
    def predict_(w):
        return np.array([module(weights=wi).compute_output() for wi in w])

    from utils import decision_surface
    return go.Figure([decision_surface(predict_, xrange=xrange, yrange=yrange, density=70, showscale=False),
                      go.Scatter(x=descent_path[:, 0], y=descent_path[:, 1], mode="markers+lines", marker_color="black")],
                     layout=go.Layout(xaxis=dict(range=xrange),
                                      yaxis=dict(range=yrange),
                                      title=f"GD Descent Path {title}"))


def get_gd_state_recorder_callback() -> Tuple[Callable[[], None], List[np.ndarray], List[np.ndarray]]:
    """
    Callback generator for the GradientDescent class, recording the objective's value and parameters at each iteration

    Return:
    -------
    callback: Callable[[], None]
        Callback function to be passed to the GradientDescent class, recoding the objective's value and parameters
        at each iteration of the algorithm

    values: List[np.ndarray]
        Recorded objective values

    weights: List[np.ndarray]
        Recorded parameters
    """
    values = []
    weights = []

    def fit_record_callback(**kwargs) -> None:
        weights.append(kwargs["weights"])
        values.append(kwargs["val"])
    return fit_record_callback, values, weights


def minimize_module_for_fixed_learning_rate(eta, init, module):
    """
    Minimizes the given module for a given fixed learning rate and plots the
    descent path.
    Parameters
    ----------
    eta: float
        the learning rate
    init: np.ndarray
        the initial value of the model's weights
    module: BaseModule
        the module to minimize

    Returns
    -------

    """
    eta_str_joined = "".join(str(eta).split("."))
    module_name = module.__class__.__name__

    lr = FixedLR(eta)
    callback, values, weights = get_gd_state_recorder_callback()
    gd = GradientDescent(learning_rate=lr, callback=callback)
    sol = gd.fit(module, init, init)
    weights_array = np.array(weights)
    fig = plot_descent_path(type(module), weights_array, "of " + module_name +
                            " - learning rate: " + str(eta))
    fig.update_layout(height=400, width=400)
    fig.write_html("21_" + module_name + "_eta_" + eta_str_joined + ".html")
    return values


def minimize_module_for_all_fixed_learning_rate(etas, init, module_type):
    """
    Minimizes the given module for given fixed learning rates and plots the
    descent path.
    Parameters
    ----------
    etas:
        The different learning rates
    init:
        The initial value of the model's weights
    module_type:
        The class type of the module
    Returns
    -------

    """
    lowest_loss = np.inf
    module_name = module_type.__name__
    for eta in etas:
        module = module_type(init)
        vals = minimize_module_for_fixed_learning_rate(eta, init, module)
        loss = vals[-1]
        if loss < lowest_loss:
            lowest_loss = loss
        plt.plot(vals, label="eta=" + str(eta))
    plt.xlabel("Iteration")
    plt.ylabel("Norm")
    plt.title(module_name + " GD convergence for different learning rates")
    plt.legend()
    plt.margins(x=0)
    plt.savefig("23_" + module_name + "_convergence_rate.jpg")
    plt.close()

    print(f"The lowest loss when minimizing {module_name} is: {lowest_loss:.11f}")

def compare_fixed_learning_rates(init: np.ndarray = np.array([np.sqrt(2), np.e / 3]),
                                 etas: Tuple[float] = (1, .1, .01, .001)):
    minimize_module_for_all_fixed_learning_rate(etas, init, L1)
    minimize_module_for_all_fixed_learning_rate(etas, init, L2)



def load_data(path: str = "SAheart.data", train_portion: float = .8) -> \
        Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """
    Load South-Africa Heart Disease dataset and randomly split into a train- and test portion

    Parameters:
    -----------
    path: str, default= "../datasets/SAheart.data"
        Path to dataset

    train_portion: float, default=0.8
        Portion of dataset to use as a training set

    Return:
    -------
    train_X : DataFrame of shape (ceil(train_proportion * n_samples), n_features)
        Design matrix of train set

    train_y : Series of shape (ceil(train_proportion * n_samples), )
        Responses of training samples

    test_X : DataFrame of shape (floor((1-train_proportion) * n_samples), n_features)
        Design matrix of test set

    test_y : Series of shape (floor((1-train_proportion) * n_samples), )
        Responses of test samples
    """
    df = pd.read_csv(path)
    df.famhist = (df.famhist == 'Present').astype(int)
    return split_train_test(df.drop(['chd', 'row.names'], axis=1), df.chd, train_portion)


def fit_logistic_regression():
    # Load and split SA Heard Disease dataset
    X_train, y_train, X_test, y_test = load_data()

    # Plotting convergence rate of logistic regression over SA heart disease data
    lr = 1e-4
    max_iter = 20000

    callback, losses, weights = get_gd_state_recorder_callback()
    gradient_descent = GradientDescent(learning_rate=FixedLR(lr),
                                       max_iter=max_iter, callback=callback)
    logistic_regression_model = LogisticRegression(solver=gradient_descent)
    logistic_regression_model.fit(X_train.values, y_train.values)
    y_proba = logistic_regression_model.predict_proba(X_train.values)
    fpr, tpr, thresholds = roc_curve(y_train.values, y_proba)

    fig = go.Figure(
        data=[go.Scatter(x=[0, 1], y=[0, 1], mode="lines",
                         line=dict(color="black", dash='dash'),
                         showlegend=False),
              go.Scatter(x=fpr, y=tpr, mode='lines', text=thresholds,
                         name="", showlegend=False, marker_size=5,
                         hovertemplate="<b>Threshold:</b>%{text:.3f}<br>FPR: %{x:.3f}<br>TPR: %{y:.3f}")],
        layout=go.Layout(
            title=dict(text="ROC Curve Of Logistic Regression - AUC=" + f"{auc(fpr, tpr):.3f}", font=dict(size=15), x=0.5),
            xaxis=dict(title="FPR"),
            yaxis=dict(title="TPR")))
    fig.update_layout(height=400, width=400)
    fig.write_html("25_ROC_curve" + ".html")

    logistic_regression_model.alpha_ = thresholds[np.argmax(tpr - fpr)]
    test_error = logistic_regression_model.loss(X_test.values, y_test.values)

    print("Threshold that achieves optimal ROC value:",
          logistic_regression_model.alpha_,
          "\nModel's test error(using optimal threshold):", test_error)
    print("******************************************************************")



    # Fitting l1- and l2-regularized logistic regression models, using cross-validation to specify values
    # of regularization parameter
    lambdas = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1]

    callback2, losses2, weights2 = get_gd_state_recorder_callback()
    gradient_descent2 = GradientDescent(learning_rate=FixedLR(lr),
                                       max_iter=max_iter, callback=callback2)

    best_lam, best_lambda_error = None, np.inf
    for lam in lambdas:
        logistic_regression_model2 = LogisticRegression(
            solver=gradient_descent2,
            penalty="l1", lam=lam)
        train_score, validation_score = \
            cross_validate(logistic_regression_model2, X_train.values,
                           y_train.values, misclassification_error)
        if validation_score < best_lambda_error:
            best_lam, best_lambda_error = lam, validation_score

    logistic_regression_model2 = LogisticRegression(
        solver=gradient_descent2, penalty="l1", lam=best_lam, alpha=.5)
    logistic_regression_model2.fit(X_train.values, y_train.values)
    test_error2 = logistic_regression_model2.loss(X_test.values, y_test.values)
    print("lambda selected:", best_lam, "\nTest error:", test_error2)


if __name__ == '__main__':
    np.random.seed(0)
    compare_fixed_learning_rates()
    fit_logistic_regression()
