import pandas as pd
from typing import NoReturn

import matplotlib.pyplot as plt
from linear_regression import *


def add_features(X: pd.DataFrame):
    """
    Add new features to the dataset.
    """
    new_X = X.copy()
    new_X['yr_sold'] = new_X['date'].dt.year
    new_X['house_age'] = new_X['yr_sold'] - new_X['yr_built']
    new_X['total_sqft'] = new_X['sqft_living'] + new_X['sqft_lot']
    new_X['living_size_difference'] = new_X['sqft_living'] - \
                                      new_X['sqft_living15']
    return new_X


def preprocess_train(X: pd.DataFrame, y: pd.Series):
    """
    preprocess training data.
    Parameters
    ----------
    X: pd.DataFrame
        the loaded data
    y: pd.Series

    Returns
    -------
    A clean, preprocessed version of the data
    """
    new_X = X.copy()
    new_X = new_X.join(y).reset_index(drop=True)

    # extract year, month, and day from date
    # handle missing values:
    new_X['date'] = pd.to_datetime(new_X['date'])
    new_X['date'] = new_X['date'].fillna(method='ffill')

    # delete duplicate rows:
    new_X = new_X.drop_duplicates()

    # handle outliers
    new_X = new_X.loc[new_X['price'] < 6000000]
    new_X = new_X.loc[(new_X['bedrooms'] > 0) & (new_X['bedrooms'] < 15)]
    new_X = new_X.loc[(new_X['bathrooms'] > 0) & (new_X['bathrooms'] < 9)]
    new_X['sqft_lot15'] = abs(new_X['sqft_lot15'])


    new_X = add_features(new_X)

    # Remove columns
    new_X = new_X.drop(columns=['id', 'date', 'yr_sold', 'yr_renovated'], axis=1)

    new_X, new_y = new_X.drop("price", axis=1), new_X.price
    return new_X, new_y


def preprocess_test(X: pd.DataFrame):
    """
    preprocess test data. You are not allowed to remove rows from X, but only edit its columns.
    Parameters
    ----------
    X: pd.DataFrame
        the loaded data

    Returns
    -------
    A preprocessed version of the test data that matches the coefficients format.
    """
    # pd.options.display.float_format = '{:.5f}'.format

    new_X = X.copy()
    new_X = new_X.reset_index(drop=True)

    # handle missing values
    new_X['date'] = pd.to_datetime(new_X['date'])
    new_X['date'] = new_X['date'].fillna(method='ffill')

    # Handle outliers
    new_X['bedrooms'] = new_X['bedrooms'].mask(
        (new_X['bedrooms'] > 15) | (new_X['bedrooms'] <= 0),
        new_X['bedrooms'].mean())
    new_X['bathrooms'] = new_X['bathrooms'].mask(
        (new_X['bathrooms'] > 8) | (new_X['bathrooms'] <= 0),
        new_X['bathrooms'].mean())

    new_X = add_features(new_X)

    # remove features
    new_X = new_X.drop(columns=['id', 'date', 'yr_sold', 'yr_renovated'], axis=1)
    return new_X


def calc_pearson_correlation(cov_matrix, std_matrix, feature, response):
    """
    Calculate pearson correlation between given feature and response.
    """
    cov_feature_response = cov_matrix.loc[feature, response]
    return cov_feature_response / (std_matrix[feature] * std_matrix[response])


def feature_evaluation(X: pd.DataFrame, y: pd.Series,
                       output_path: str = ".") -> NoReturn:
    """
    Create scatter plot between each feature and the response.
        - Plot title specifies feature name
        - Plot title specifies Pearson Correlation between feature and response
        - Plot saved under given folder with file name including feature name
    Parameters
    ----------
    X : DataFrame of shape (n_samples, n_features)
        Design matrix of regression problem

    y : array-like of shape (n_samples, )
        Response vector to evaluate against

    output_path: str (default ".")
        Path to folder in which plots are saved
    """
    new_X = X.copy()
    new_X = new_X.join(y)
    cov_matrix = new_X.cov()
    std_matrix = new_X.std()

    for feature in new_X.columns:
        if feature != y.name:
            pearson_corr = calc_pearson_correlation(
                cov_matrix, std_matrix, feature, y.name)
            plt.scatter(x=feature, y=y.name, data=new_X)
            plt.ticklabel_format(style='plain')
            plt.xlabel(feature)
            plt.ylabel(y.name)
            plt.title(feature + " vs. " + y.name + " - correlation: " +
                      str(pearson_corr))
            plt.tight_layout()
            plt.savefig(feature + ".jpg")
            plt.close()


def linear_regression_over_inc_train_data(X_train, y_train, X_test, y_test):
    """
    Function for question 6 in section 3.1.
    Fits a linear regression model over increasing percentages of the training
    set and measures the loss over the test set.
    """
    train_joined = X_train.join(y_train).reset_index(drop=True)
    loss_average_lst = []
    loss_std_lst = []
    percentages = []
    for i in range(10, 101):
        loss_lst = []
        percentages.append(i)
        fraction = i / 100
        for j in range(10):
            sampled = train_joined.sample(frac=fraction)
            sampled_X, sampled_y = sampled.drop("price", axis=1), sampled.price
            linear_reg_model = LinearRegression()
            linear_reg_model.fit(sampled_X, sampled_y)
            loss_lst.append(linear_reg_model.loss(X_test, y_test))
        loss_average_lst.append(np.mean(loss_lst))
        loss_std_lst.append(np.std(loss_lst))

    # create confidence interval
    loss_average_lst = np.array(loss_average_lst)
    loss_std_lst = np.array(loss_std_lst)
    lower_bound = loss_average_lst - 2 * loss_std_lst
    upper_bound = loss_average_lst + 2 * loss_std_lst

    # plot the loss of the model over increasing percentages of the training
    # set
    plt.plot(percentages, loss_average_lst)
    plt.fill_between(percentages, lower_bound, upper_bound, alpha=0.2,
                     color='gray')
    plt.xlabel('Percentage of training set')
    plt.ylabel('MSE of test set')
    plt.ticklabel_format(style='plain')
    plt.title("Model's loss over increasing percentages of training set")
    plt.tight_layout()
    plt.savefig("316_linear_regression_loss.jpg")
    plt.close()


if __name__ == '__main__':
    np.random.seed(1)
    df = pd.read_csv("house_prices.csv")
    df.dropna(subset=['price'], inplace=True)
    X, y = df.drop("price", axis=1), df.price

    # pd.options.display.float_format = '{:.5f}'.format

    # Question 2 - split train test
    train_data = df.sample(frac=0.75)
    test_data = df.drop(train_data.index)
    X_train, y_train = train_data.drop("price", axis=1), train_data.price
    X_test, y_test = test_data.drop("price", axis=1), test_data.price

    # Question 3 - preprocessing of housing prices train dataset
    new_X_train, new_y_train = preprocess_train(X_train, y_train)

    # Question 4 - Feature evaluation of train dataset with respect to response
    feature_evaluation(new_X_train, new_y_train)

    # Question 5 - preprocess the test data
    new_X_test = preprocess_test(X_test)


    # Question 6 - Fit model over increasing percentages of the overall training data
    # For every percentage p in 10%, 11%, ..., 100%, repeat the following 10 times:
    #   1) Sample p% of the overall training data
    #   2) Fit linear model (including intercept) over sampled set
    #   3) Test fitted model over test set
    #   4) Store average and variance of loss over test set
    # Then plot average loss as function of training size with error ribbon of size (mean-2*std, mean+2*std)

    linear_regression_over_inc_train_data(new_X_train, new_y_train,
                                          new_X_test, y_test)
