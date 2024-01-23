import pandas as pd
import logging
from sklearn.metrics import accuracy_score, recall_score, f1_score, precision_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import train_test_split
import model_card_toolkit as mct
def train_test_split_with_encoding(
    df, target_variable, test_size=0.2, random_state=None
):
    """
    Splits a dataset into train and test sets and performs one-hot encoding on the feature variables.

    Parameters
    ----------
    df : pd.DataFrame
        The dataset to split and encode.
    target_variable : str
        The name of the target variable column in the DataFrame.
    test_size : float, optional
        The proportion of the dataset to include in the test split, by default 0.2.
    random_state : int, optional
        Controls the shuffling applied to the data before applying the split, by default None.

    Returns
    -------
    X_train_encoded : pd.DataFrame
        The encoded feature variables for the training set.
    X_test_encoded : pd.DataFrame
        The encoded feature variables for the test set.
    y_train : pd.Series
        The target variable for the training set.model_card
    y_test : pd.Series
        The target variable for the test set.
    """
    
    logging.info("Performing train-test split and encoding...")
    X = df.drop(target_variable, axis=1)
    y = df[target_variable]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    X_train_encoded = pd.get_dummies(X_train)
    X_test_encoded = pd.get_dummies(X_test)

    # Ensure both train and test sets have the same columns after encoding
    X_train_encoded, X_test_encoded = X_train_encoded.align(
        X_test_encoded, join="left", axis=1, fill_value=0
    )

    logging.info("Train-test split and encoding completed.")

    return X_train_encoded, X_test_encoded, y_train, y_test


def train_and_evaluate_model_kfold(X_train, y_train, X_test, y_test, classifier):
    """
    Trains a classifier model and evaluates its performance using multiple metrics.

    Parameters
    ----------
    X_train : pd.DataFrame
        The feature variables for the training set.
    y_train : pd.Series
        The target variable for the training set.
    X_test : pd.DataFrame
        The feature variables for the test set.
    y_test : pd.Series
        The target variable for the test set.
    classifier : sklearn.base.ClassifierMixin
        The classifier to train and evaluate.

    Returns
    -------
    accuracy : float
        The accuracy of the trained classifier.
    recall : float
        The recall of the trained classifier.
    f1 : float
        The F1 score of the trained classifier.
    precision : float
        The precision of the trained classifier.
    roc_auc : float
        The ROC AUC score of the trained classifier.
    """
    
    logging.info("Training and evaluating model...")
    clf = classifier
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)
    conf_matrix = confusion_matrix(y_test, y_pred)

    logging.info(
        "Model evaluation completed. Accuracy: %s, Recall: %s, F1: %s, Precision: %s, ROC AUC: %s",
        accuracy,
        recall,
        f1,
        precision,
        roc_auc,
    )

    return accuracy, recall, f1, precision, roc_auc, conf_matrix


 
def validate_model(
    most_similar_dataset: pd.DataFrame, target_variable: str, classifier
):
    """
    Validates a classifier model on the most similar synthetic dataset, 
    and returns a dictionary of the performance metrics.

    Parameters
    ----------
    most_similar_dataset : pd.DataFrame
        The most similar synthetic dataset.
    target_variable : str
        The name of the target variable column in the DataFrame.
    classifier : sklearn.base.ClassifierMixin
        The classifier to validate.

    Returns
    -------
    dict
        A dictionary containing the performance metrics of the validated model.
    """
    
    logging.info("Validating model...")
    X_train, X_test, y_train, y_test = train_test_split_with_encoding(
        most_similar_dataset, target_variable, test_size=0.2, random_state=42
    )
    (
        accuracy,
        recall,
        f1,
        precision,
        roc_auc,
        conf_matrix
    ) = train_and_evaluate_model_kfold(X_train, y_train, X_test, y_test, classifier)

    logging.info(
        "Model validation completed. Accuracy: %s, Recall: %s, F1: %s, Precision: %s, ROC AUC: %s",
        accuracy,
        recall,
        f1,
        precision,
        roc_auc,
    )

    return {
        "accuracy": accuracy,
        "recall": recall,
        "f1": f1,
        "precision": precision,
        "roc_auc": roc_auc,
    }
        

def get_performance_metrics_on_synthetic_datasets(synthetic_datasets, classifiers, target_variable, test_size, random_state):
    """
    Trains and evaluates models on each synthetic dataset and stores the performance metrics.

    Args:
    synthetic_datasets (list): List of synthetic datasets.
    classifiers (list): List of classifiers (dictionary containing 'name' and 'clf' (the classifier object)).
    target_variable (str): Target variable for the model.
    test_size (float): Proportion of the dataset to include in the test split.
    random_state (int): The seed used by the random number generator.

    Returns:
    performance_metrics_list (list): List of dictionaries, each containing the performance metrics for a model.
    """
    performance_metrics_list = []
    for synthetic_dataset in synthetic_datasets:
        X_train, X_test, y_train, y_test = train_test_split_with_encoding(synthetic_dataset, target_variable, test_size=test_size, random_state=random_state)
        for classifier_info in classifiers:
            logging.info(f"Testing {classifier_info['name']} on synthetic dataset")
            accuracy, recall, f1, precision, roc_auc, conf_matrix = train_and_evaluate_model_kfold(X_train, y_train, X_test, y_test, classifier_info["clf"])
            metrics = {"accuracy": accuracy, "recall": recall, "f1": f1, "precision": precision, "roc_auc": roc_auc, "conf_matrix": conf_matrix}
            performance_metrics_list.append(metrics)
    return performance_metrics_list

def get_model_cards(X_train, y_train, X_test, y_test, classifier,metrics):
    
    # Initialize the Model Card Toolkit with a path to store generate assets
    model_card_output_path = '~/Documents/Master Program UM/Research Project/Sem 1/LUCE_Model_Monitoring-main/model_card_assets'
    toolkit = mct.ModelCardToolkit(model_card_output_path)

    # Initialize the ModelCard, which can be freely populated
    model_card = toolkit.scaffold_assets()
    model_card.model_details.name = 'Model Card Heart Disease'

    # Add evaluation metrics to the model card
    model_card.quantitative_analysis.performance_metrics = [
        mct.PerformanceMetric(type=metric, value=value)
        for metric, value in metrics.items()
    ]
    # Add more metrics as needed

    # Write the model card data to a proto file
    update=toolkit.update_model_card(model_card)

    # Return the model card document as an HTML page
    html = toolkit.export_format()
    return html, update
