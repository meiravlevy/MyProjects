import numpy as np
import faiss

class KNNClassifier:
    def __init__(self, k, distance_metric='l2'):
        self.k = k
        self.distance_metric = distance_metric
        self.X_train = None
        self.Y_train = None

        self.index = None


    def fit(self, X_train, Y_train):
        """
        Update the kNN classifier with the provided training data.

        Parameters:
        - X_train (numpy array) of size (N, d): Training feature vectors.
        - Y_train (numpy array) of size (N,): Corresponding class labels.
        """
        self.X_train = X_train.astype(np.float32)
        self.Y_train = Y_train
        d = self.X_train.shape[1]
        if self.distance_metric == 'l2':
            self.index = faiss.index_factory(d, "Flat", faiss.METRIC_L2)
        elif self.distance_metric == 'l1':
            self.index = faiss.index_factory(d, "Flat", faiss.METRIC_L1)
        else:
            raise NotImplementedError
        pass
        self.index.add(self.X_train)

    def predict(self, X):
        """
        Predict the class labels for the given data.

        Parameters:
        - X (numpy array) of size (M, d): Feature vectors.

        Returns:
        - (numpy array) of size (M,): Predicted class labels.
        """
        #### YOUR CODE GOES HERE ####
        distances, indexes = self.knn_distance(X)
        #  creates an array of labels of the k nearest neighbours data
        #  according to the indexes array
        labels_of_indexes = self.Y_train[indexes]
        # the prediction that we will return
        predicted_labels = np.zeros(X.shape[0]).astype(int)
        # creates a vector with the different labels in the training set
        unique_labels = np.unique(self.Y_train)
        for row in range(labels_of_indexes.shape[0]):
            amounts_of_labels_in_row = np.zeros(unique_labels.shape[0])
            for i in range(unique_labels.shape[0]):
                amounts_of_labels_in_row[i] = np.count_nonzero(
                    labels_of_indexes[row] == unique_labels[i])
            max_amount_label_index = np.argmax(amounts_of_labels_in_row)
            max_label = unique_labels[max_amount_label_index]
            predicted_labels[row] = max_label
        return predicted_labels



    def knn_distance(self, X):
        """
        Calculate kNN distances for the given data. You must use the faiss library to compute the distances.
        See lecture slides and https://github.com/facebookresearch/faiss/wiki/Getting-started#in-python-2 for more information.

        Parameters:
        - X (numpy array) of size (M, d): Feature vectors.

        Returns:
        - (numpy array) of size (M, k): kNN distances.
        - (numpy array) of size (M, k): Indices of kNNs.
        """
        X = X.astype(np.float32)
        distances, indexes = self.index.search(X, self.k)
        return distances, indexes
