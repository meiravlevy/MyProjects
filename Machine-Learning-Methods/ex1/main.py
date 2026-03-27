from utils import *
from prophets import *
import pandas as pd


def compute_errors_of_prophets(prophets, train_set_reduced):
    """
    Computes the empirical error of each prophet in prophets, and returns the
    results in a list.
    """
    error_probs = [compute_error(prophet.predict(train_set_reduced),
                                 train_set_reduced) for prophet in prophets]
    return error_probs

def Scenario_1():
    """
    Question 1.
    2 Prophets 1 Game.
    You may change the input & output parameters of the function as you wish.
    """
    p1_wins = 0
    test_err = 0.
    est_err = 0.

    p1 = Prophet(0.2)
    p2 = Prophet(0.4)

    for exp in range(100):
        trainset_reduced = np.random.choice(train_set[exp, :], size=1)
        p1_err = compute_error(p1.predict(trainset_reduced), trainset_reduced)
        p2_err = compute_error(p2.predict(trainset_reduced), trainset_reduced)
        if p1_err <= p2_err:
            p1_wins += 1
            test_err += compute_error(p1.predict(test_set), test_set)
        else:
            test_err += compute_error(p2.predict(test_set), test_set)
            est_err += 0.2

    print("Average test error of selected prophet: ", test_err / 100.)
    print("Number of times best prophet selected: ", p1_wins)
    print("Average approximation error: 0.2")
    print("Average estimation error: ", est_err / 100.)

def Scenario_2():
    """
    Question 2.
    2 Prophets 10 Games.
    You may change the input & output parameters of the function as you wish.
    """
    p1_wins = 0
    test_err = 0.
    est_err = 0.

    p1 = Prophet(0.2)
    p2 = Prophet(0.4)

    for exp in range(100):
        trainset_reduced = np.random.choice(train_set[exp, :], size=10)
        p1_err = compute_error(p1.predict(trainset_reduced), trainset_reduced)
        p2_err = compute_error(p2.predict(trainset_reduced), trainset_reduced)
        if p1_err <= p2_err:
            p1_wins += 1
            test_err += compute_error(p1.predict(test_set), test_set)
        else:
            test_err += compute_error(p2.predict(test_set), test_set)
            est_err += 0.2

    print("Average test error of selected prophet: ", test_err / 100.)
    print("Number of times best prophet selected: ", p1_wins)
    print("Average approximation error: 0.2")
    print("Average estimation error: ", est_err / 100.)


def Scenario_3():
    """
    Question 3.
    500 Prophets 10 Games.
    You may change the input & output parameters of the function as you wish.
    """
    min_prophet_wins = 0
    epsilon_prophets_win = 0
    test_err = 0.
    est_err = 0.

    prophets_list = sample_prophets(500, 0, 1)
    prophets_np_arr = np.array(prophets_list)
    min_prophet_prob_index = np.argmin([prophet.get_err_prob() for prophet in
                                        prophets_np_arr])
    min_prophet = prophets_np_arr[min_prophet_prob_index]

    for exp in range(100):
        trainset_reduced = np.random.choice(train_set[exp, :], size=10)
        prophets_err = np.array(compute_errors_of_prophets(
            prophets_np_arr, trainset_reduced))
        erm_prophet_index = np.argmin(prophets_err)
        erm_prophet = prophets_np_arr[erm_prophet_index]
        if min_prophet.get_err_prob() == erm_prophet.get_err_prob():
            min_prophet_wins += 1
        elif min_prophet.get_err_prob() < erm_prophet.get_err_prob() <= \
                min_prophet.get_err_prob() + 0.01:
            epsilon_prophets_win += 1
            est_err += (erm_prophet.get_err_prob() -
                        min_prophet.get_err_prob())
        else:
            est_err += (erm_prophet.get_err_prob() -
                        min_prophet.get_err_prob())
        test_err += compute_error(erm_prophet.predict(test_set), test_set)

    print("Average test error of selected prophet: ", test_err / 100.)
    print("Number of times best prophet selected: ", min_prophet_wins)
    print("Number of times ERM chose a prophet that was not 1% worse than "
          "the best prophet: ", min_prophet_wins + epsilon_prophets_win)
    print("Average approximation error: ", min_prophet.get_err_prob())
    print("Average estimation error: ", est_err / 100.)


def Scenario_4():
    """
    Question 4.
    500 Prophets 1000 Games.
    You may change the input & output parameters of the function as you wish.
    """
    min_prophet_wins = 0
    epsilon_prophets_win = 0
    test_err = 0.
    est_err = 0.

    train_set_generalization_error = 0.
    test_set_generalization_error = 0.

    prophets_list = sample_prophets(500, 0, 1)
    prophets_np_arr = np.array(prophets_list)
    min_prophet_prob_index = np.argmin([prophet.get_err_prob() for prophet in
                                        prophets_np_arr])
    min_prophet = prophets_np_arr[min_prophet_prob_index]

    for exp in range(100):
        trainset_reduced = np.random.choice(train_set[exp, :], size=1000)
        prophets_err = np.array(compute_errors_of_prophets(
            prophets_np_arr, trainset_reduced))
        erm_prophet_index = np.argmin(prophets_err)
        erm_prophet = prophets_np_arr[erm_prophet_index]
        if min_prophet.get_err_prob() == erm_prophet.get_err_prob():
            min_prophet_wins += 1
        elif min_prophet.get_err_prob() < erm_prophet.get_err_prob() <= \
                min_prophet.get_err_prob() + 0.01:
            epsilon_prophets_win += 1
            est_err += (erm_prophet.get_err_prob() -
                        min_prophet.get_err_prob())
        else:
            est_err += (erm_prophet.get_err_prob() -
                        min_prophet.get_err_prob())

        test_err += compute_error(erm_prophet.predict(test_set), test_set)
        test_set_generalization_error += \
            abs(erm_prophet.get_err_prob() -
                compute_error(erm_prophet.predict(test_set), test_set))
        train_set_generalization_error += \
            abs(erm_prophet.get_err_prob() - prophets_err[erm_prophet_index])



    print("Average test error of selected prophet: ", test_err / 100.)
    print("Number of times best prophet selected: ", min_prophet_wins)
    print("Number of times ERM chose a prophet that was not 1% worse than "
          "the best prophet: ", min_prophet_wins + epsilon_prophets_win)
    print("Average approximation error: ", min_prophet.get_err_prob())
    print("Average estimation error: ", est_err / 100.)
    print("Average generalization error of training set: ",
          train_set_generalization_error / 100)
    print("Average generalization error of test set: ",
          test_set_generalization_error / 100)


def Scenario_5():
    """
    Question 5.
    School of Prophets.
    You may change the input & output parameters of the function as you wish.
    """
    prophets_list = sample_prophets(50, 0, 0.2)
    prophets_np_arr = np.array(prophets_list)
    true_risk_list = [prophet.get_err_prob() for prophet in prophets_np_arr]

    num_of_prophets_list = [2, 5, 10, 50]
    num_of_games_list = [1, 10, 50, 1000]

    data_frame = pd.DataFrame(columns=["m = 1", "m = 10", "m = 50",
                                       "m = 1000"],
                              index=["k = 2", "k = 5", "k = 10", "k = 50"])

    for k in num_of_prophets_list:
        prophets_arr_reduced = prophets_np_arr[:k]
        true_risk_list_reduced = true_risk_list[:k]
        min_true_risk_prophet_index = np.argmin(true_risk_list_reduced)
        min_prophet = prophets_arr_reduced[min_true_risk_prophet_index]
        for m in num_of_games_list:
            est_err = 0.
            for exp in range(100):
                trainset_reduced = np.random.choice(train_set[exp, :], size=m)
                prophets_err = np.array(compute_errors_of_prophets(
                    prophets_arr_reduced, trainset_reduced))
                erm_prophet_index = np.argmin(prophets_err)
                erm_prophet = prophets_np_arr[erm_prophet_index]
                est_err += (erm_prophet.get_err_prob() -
                            min_prophet.get_err_prob())

            data_frame.loc["k = " + str(k), "m = " + str(m)] = \
                (round(est_err / 100, 4), round(min_prophet.get_err_prob(), 4))

    print(data_frame)


def Scenario_6():
    """
    Question 6.
    The Bias-Variance Tradeoff.
    You may change the input & output parameters of the function as you wish.
    """
    est_err1 = 0.
    test_err1 = 0.
    prophets1 = sample_prophets(5, 0.3, 0.6)
    prophets1_np_arr = np.array(prophets1)
    true_risk_list1 = [prophet.get_err_prob() for prophet in prophets1_np_arr]
    min_prophet1_index = np.argmin(true_risk_list1)
    min_prophet1 = prophets1[min_prophet1_index]

    est_err2 = 0.
    test_err2 = 0.
    prophets2 = sample_prophets(500, 0.25, 0.6)
    prophets2_np_arr = np.array(prophets2)
    true_risk_list2 = [prophet.get_err_prob() for prophet in prophets2_np_arr]
    min_prophet2_index = np.argmin(true_risk_list2)
    min_prophet2 = prophets2[min_prophet2_index]

    for exp in range(100):
        trainset_reduced = np.random.choice(train_set[exp, :], size=10)
        prophets_err1 = np.array(compute_errors_of_prophets(
            prophets1_np_arr, trainset_reduced))
        erm_prophet1_index = np.argmin(prophets_err1)
        erm_prophet1 = prophets1_np_arr[erm_prophet1_index]
        est_err1 += (erm_prophet1.get_err_prob() - min_prophet1.get_err_prob())
        test_err1 += compute_error(erm_prophet1.predict(test_set), test_set)

        prophets_err2 = np.array(compute_errors_of_prophets(
            prophets2_np_arr, trainset_reduced))
        erm_prophet2_index = np.argmin(prophets_err2)
        erm_prophet2 = prophets2_np_arr[erm_prophet2_index]
        est_err2 += (erm_prophet2.get_err_prob() - min_prophet2.get_err_prob())
        test_err2 += compute_error(erm_prophet2.predict(test_set), test_set)

    print("Average test error of selected prophet of the first hypothesis "
          "class: ", test_err1 / 100)
    print("Average approximation error of the first hypothesis class: ",
          min_prophet1.get_err_prob())
    print("Average estimation error of the first hypothesis class: ",
          est_err1 / 100.)
    print("Average test error of selected prophet of the second hypothesis "
          "class: ", test_err2 / 100)
    print("Average approximation error for the second hypothesis class: ",
          min_prophet2.get_err_prob())
    print("Average estimation error of the second hypothesis class: ",
          est_err2 / 100.)



if __name__ == '__main__':
    np.random.seed(0)  # DO NOT MOVE / REMOVE THIS CODE LINE!

    # train, validation and test splits for Scenario 1-3, 5
    train_set = create_data(100, 1000)
    test_set = create_data(1, 1000)[0]

    print(f'Scenario 1 Results:')
    Scenario_1()

    print(f'Scenario 2 Results:')
    Scenario_2()

    print(f'Scenario 3 Results:')
    Scenario_3()

    print(f'Scenario 4 Results:')
    Scenario_4()

    print(f'Scenario 5 Results:')
    Scenario_5()

    print(f'Scenario 6 Results:')
    Scenario_6()
