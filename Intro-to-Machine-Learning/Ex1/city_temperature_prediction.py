
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from polynomial_fitting import *
import seaborn as sns


def load_data(filename: str) -> pd.DataFrame:
    """
    Load city daily temperature dataset and preprocess data.
    Parameters
    ----------
    filename: str
        Path to house prices dataset

    Returns
    -------
    Design matrix and response vector (Temp)
    """

    new_df = pd.read_csv(filename, parse_dates=['Date'])
    new_df['DayOfYear'] = new_df['Date'].dt.dayofyear

    new_df.drop(['Date'], axis=1, inplace=True)  # doesn't give new info
    new_df = new_df.loc[new_df['Temp'] > -20]

    return new_df


def filter_country_df_temp_day_of_year(df: pd.DataFrame, country: str):
    """
    Filters a specific country data frame so that it contains only the day of
    year and the temperature.
    """
    country_df = df.loc[df['Country'] == country].reset_index(drop=True)
    country_df.drop(columns=['Country', 'City', 'Year', 'Month', 'Day'],
                    inplace=True)
    return country_df


def q3_explore_country_data(df: pd.DataFrame, country: str):
    """
    Function for question 3 in section 3.2.
    Filters data to contain only data in a specific country, and plots the
    relation between the day of year and the average daily temperature in the
    specific country.
    The function also plots the standard deviation of the daily temperatures
    in the specific country for each month
    """
    df_country = df.loc[df['Country'] == country].reset_index(drop=True)

    # Create discrete color scale for years
    country_years = df_country['Year'].unique()
    colors = sns.color_palette("tab20", len(country_years))
    cmap = ListedColormap(colors)
    year_color_dict = {year: cmap(i) for i, year in enumerate(country_years)}

    # for each year, scatter plot the relation between average daily
    # temperature and the day of year
    for i, year in enumerate(country_years):
        year_data = df_country.loc[df_country['Year'] == year]
        plt.scatter(year_data.DayOfYear, year_data.Temp,
                    color=year_color_dict[year], label=str(year))
    plt.xlabel('Day of year')
    plt.ylabel('Average daily temperature')
    plt.title("Average daily temperature across days of the "
              "year in " + country)
    plt.legend(title='Year', bbox_to_anchor=(1, 1))
    plt.subplots_adjust(right=0.75)
    plt.savefig("323" + country + "_days_of_year_avg_temp.jpg")
    plt.close()

    # plot a bar plot showing for each month the standard deviation of the
    # daily temperatures
    country_month_std = df_country.groupby('Month')['Temp'].std().reset_index(
        name='Temp_std')
    plt.bar(country_month_std['Month'], country_month_std['Temp_std'])
    plt.xlabel('Month')
    plt.ylabel('Std of daily temperature')
    plt.title('Standard deviation of the daily temperatures for each '
              'month in ' + country)
    plt.savefig("323_" + country + "_months_temp_std.jpg")
    plt.close()


def q4_explore_countries_differences(df: pd.DataFrame):
    """
    Function for question 4 in section 3.2.
    Groups the data frame according to 'Country' and 'Month' and calculates the
    average and standard deviation od the temperature.
    Then' the function plots the average monthly temperature with error bars
    for all countries.
    """
    countries_avg_temps_df = df.groupby(['Country', 'Month']).agg(
        {'Temp': ['mean', 'std']})
    countries_avg_temps_df.columns = ['Temp_avg', 'Temp_std']
    countries_avg_temps_df.reset_index(inplace=True)

    fig, ax = plt.subplots()
    for country in countries_avg_temps_df['Country'].unique():
        country_avg_temp_df = countries_avg_temps_df.loc[
            countries_avg_temps_df['Country'] == country]
        ax.errorbar(country_avg_temp_df['Month'],
                    country_avg_temp_df['Temp_avg'],
                    yerr=country_avg_temp_df['Temp_std'],
                    label=country, capsize=5)
    ax.set_xlabel('Month')
    ax.set_ylabel('Temperature average')
    ax.set_title('Countries average monthly temperature with error bars')
    plt.legend()
    plt.savefig("324_countries_avg_temps.jpg")
    plt.close()


def q5_fit_model_for_different_values_of_k(df: pd.DataFrame):
    """
    Function for question 5 in section 3.2.
    For a specific country, fits a polynomial model of different degrees k,
    and both prints and plots the test error recorded for each value k.
    """
    # Randomly split Israel's dataset into training set and test set
    israel_df = filter_country_df_temp_day_of_year(df, "Israel")
    train_data = israel_df.sample(frac=0.75)
    test_data = israel_df.drop(train_data.index)
    X_train, y_train = train_data.drop("Temp", axis=1), train_data.Temp
    X_test, y_test = test_data.drop("Temp", axis=1), test_data.Temp

    loss_lst = []
    range_of_k = range(1, 11)
    # For every k from 1 to 10, fit a polynomial model of degree k using the
    # training set
    for k in range_of_k:
        polynomial_fit = PolynomialFitting(k)
        polynomial_fit.fit(X_train.values.reshape(-1), y_train)
        # calculate loss of the model over test set
        loss = round(polynomial_fit.loss(X_test.values.reshape(-1), y_test), 2)
        loss_lst.append(loss)
        print("test error for k=" + str(k) + ": " + str(loss))
    # plot test error recorded for each value of k
    plt.bar(range_of_k, loss_lst)
    plt.xticks(range_of_k, [str(k) for k in range_of_k])
    plt.xlabel('k(polynomial degree)')
    plt.ylabel('Test error')
    plt.title('Polynomial fitting: test error vs. polynomial degree')
    plt.savefig("325_test_error_vs_k_values.jpg")
    plt.close()


def q6_evaluating_model_on_different_countries(df: pd.DataFrame):
    """
    Function for question 6 in section 3.2.
    Fits a model for a specific country(Israel) and plots the model's error
    over each of the other countries.
    """
    k = 5
    israel_df = filter_country_df_temp_day_of_year(df, "Israel")
    X_train, y_train = israel_df.drop("Temp", axis=1), israel_df.Temp

    polynomial_fit = PolynomialFitting(k)
    # the reshape is for flattening X_train so it could be sent to fit function
    polynomial_fit.fit(X_train.values.reshape(-1), y_train)

    # record Israel's model's loss for every country except Israel
    countries = df['Country'].unique()
    countries_except_israel = [country for country in countries
                               if country != 'Israel']
    countries_loss_lst = []
    for country in countries_except_israel:
        country_df = filter_country_df_temp_day_of_year(df, country)
        X_test, y_test = country_df.drop("Temp", axis=1), country_df.Temp
        loss = round(polynomial_fit.loss(X_test.values.reshape(-1), y_test), 2)
        countries_loss_lst.append(loss)

    # plot the recorded losses
    plt.bar(countries_except_israel, countries_loss_lst)
    plt.xlabel("Country")
    plt.ylabel("Model's error")
    plt.title("Polynomial fitting with k = " + str(k) +
              ": model's error over countries except Israel")
    plt.savefig("326_test_error_countries_except_israel.jpg")
    plt.close()


if __name__ == '__main__':
    np.random.seed(1)
    pd.set_option('display.max_columns', None)

    # Question 2 - Load and preprocessing of city temperature dataset
    df = load_data("city_temperature.csv")

    # Question 3 - Exploring data for specific country
    q3_explore_country_data(df, 'Israel')

    # Question 4 - Exploring differences between countries
    q4_explore_countries_differences(df)

    # Question 5 - Fitting model for different values of `k`
    q5_fit_model_for_different_values_of_k(df)

    # Question 6 - Evaluating fitted model on different countries
    q6_evaluating_model_on_different_countries(df)
