import pandas as pd
from typing import List
import numpy as np
from imblearn.over_sampling import SMOTENC
import logging
import os

# Define constants
GAUSSIAN_NOISE_SCALE = 0.01

def load_dataset(filepath: str) -> pd.DataFrame:
    """
    Load a dataset from a given CSV file.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pd.DataFrame: The loaded dataset as a pandas DataFrame.
    """
    if not os.path.exists(filepath):
        logging.error("File %s does not exist", filepath)
        raise FileNotFoundError(f"File {filepath} does not exist")

    logging.info("Loading dataset from %s", filepath)
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        logging.error("Failed to load dataset: %s", str(e))
        raise e

    logging.info("Dataset loaded successfully")
    return df


def generate_synthetic_datasets(
    df: pd.DataFrame, target_variable: str, num_datasets: int = 10) -> List[pd.DataFrame]:
    """
    Generate synthetic datasets using SMOTENC for balancing classes and adding Gaussian noise to continuous features.

    Parameters
    ----------
    df : pd.DataFrame
        The original dataset from which synthetic datasets are to be generated.
    target_variable : str
        The name of the target variable column in the DataFrame.
    num_datasets : int, optional
        The number of synthetic datasets to generate, by default 10.

    Returns
    -------
    List[pd.DataFrame]
        A list containing the generated synthetic datasets.
    """
    
    if target_variable not in df.columns:
        logging.error("Target variable %s not found in DataFrame", target_variable)
        raise ValueError(f"Target variable {target_variable} not found in DataFrame")

    logging.info("Generating synthetic datasets")
    synthetic_datasets = []
    X = df.drop(target_variable, axis=1)
    y = df[target_variable]

    # Create a boolean mask indicating which features are categorical
    categorical_features_mask = X.dtypes == "object"

    # Get the continuous features columns (where the mask is False)
    continuous_features_columns = X.columns[~categorical_features_mask]

    # Calculate the standard deviation of each continuous feature
    continuous_features_std = X[continuous_features_columns].std()
    

    for _ in range(num_datasets):
        smote_nc = SMOTENC(
            categorical_features=categorical_features_mask.tolist(),
            random_state=np.random.randint(0, 100),
        )

        X_synthetic, y_synthetic = smote_nc.fit_resample(X, y)
        
        # Add Gaussian noise to the continuous features, scaled by their standard deviation
        for feature in continuous_features_columns:
            X_synthetic[feature] += np.random.normal(
                0,
                GAUSSIAN_NOISE_SCALE * continuous_features_std[feature],
                size=X_synthetic[feature].shape,
            )

        synthetic_df = pd.concat([X_synthetic, y_synthetic], axis=1)
        synthetic_datasets.append(synthetic_df)
    logging.info("Synthetic datasets generated successfully")
    return synthetic_datasets

def compare_datasets(original: pd.DataFrame, synthetic: pd.DataFrame):
    """
    Compare an original dataset with a synthetic dataset by logging descriptive statistics of both datasets.

    Parameters
    ----------
    original : pd.DataFrame
        The original dataset.
    synthetic : pd.DataFrame
        The synthetic dataset.
    """
    
    logging.info("Comparing datasets...")
    original_desc = original.describe(include='all')
    synthetic_desc = synthetic.describe(include='all')
    
    logging.info("Original dataset statistics:\n%s", original_desc)
    logging.info("\nSynthetic dataset statistics:\n%s", synthetic_desc)

