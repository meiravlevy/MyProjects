import numpy as np
import pandas as pd
from tqdm import tqdm

def sample_prophets(k, min_p, max_p):
    """
    Samples a set of k prophets
    :param k: number of prophets
    :param min_p: minimum probability
    :param max_p: maximum probability
    :return: list of prophets
    """
    prophets_list = [Prophet(np.random.uniform(min_p, max_p)) for _ in
                     range(k)]
    return prophets_list


class Prophet:

    def __init__(self, err_prob):
        """
        Initializes the Prophet model
        :param err_prob: the probability of the prophet to be wrong
        """
        self.__err_prob = err_prob

    def predict(self, y):
        """
        Predicts the label of the input point
        draws a random number between 0 and 1
        if the number is less than the probability, the prediction is correct (according to y)
        else the prediction is wrong
        NOTE: Realistically, the prophet should be a function from x to y (without getting y as an input)
        However, for the simplicity of our simulation, we will give the prophet y straight away
        :param y: the true label of the input point
        :return: a prediction for the label of the input point
        """
        threshes = np.random.uniform(size=y.size)
        success_bigger_than_thresh = (1 - self.__err_prob) > threshes
        return np.where(success_bigger_than_thresh, y, np.logical_not(y))

    def get_err_prob(self):
        return self.__err_prob



