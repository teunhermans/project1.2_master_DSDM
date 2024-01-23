import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import gower
import logging

def generate_metadata(df: pd.DataFrame, base_metadata: dict) -> dict:
    """
    Generate metadata for a given DataFrame.
    
    Parameters
    ----------
        df (pd.DataFrame): Input DataFrame with mixed data types.
        base_metadata (dict): A dictionary containing the base metadata schema.
        
    Returns
    -------
        dict: Updated metadata dictionary with dataset-specific information.
    """
    
    if df.empty:
        logging.error("Input DataFrame is empty")
        raise ValueError("Input DataFrame is empty")

    if "dataset_specific_metadata" not in base_metadata or "features" not in base_metadata["dataset_specific_metadata"]:
        logging.error("Base metadata does not have the expected structure")
        raise ValueError("Base metadata does not have the expected structure")

    logging.info("Generating metadata...")
    num_samples, num_features = df.shape
    base_metadata["dataset_specific_metadata"]["num_samples"] = num_samples
    features = []

    for column in df.columns:
        feature = {
            "feature_name": column,
            "feature_type": "categorical" if df[column].dtype.name == 'category' or df[column].dtype.name == 'object' else "continuous",
            "data_type": df[column].dtype.name,
            "feature_description": f"Description of {column}",
            "missing_values_proportion": df[column].isna().mean()
        }

        if feature["feature_type"] == "continuous":
            feature["mean"] = df[column].mean()
            feature["median"] = df[column].median()
            feature["std_dev"] = df[column].std()
            feature["skewness"] = df[column].skew()
            feature["kurtosis"] = df[column].kurt()
        else:
            feature["categories"] = df[column].unique().tolist()
            feature["category_counts"] = df[column].value_counts().to_dict()

        features.append(feature)

    base_metadata["dataset_specific_metadata"]["features"] = features
    logging.info("Metadata generated.")

    return base_metadata

def gower_distance_matrix(df: pd.DataFrame) -> np.ndarray:
    """
    Compute the Gower distance matrix for the given DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The dataset for which the Gower distance matrix is to be computed.

    Returns
    -------
    np.ndarray
        The computed Gower distance matrix.
    """
    
    logging.info("Calculating Gower distance matrix...")
    gower_distance = gower.gower_matrix(df)
    logging.info("Gower distance matrix calculated.")
    return gower_distance


def calculate_gower_similarity(base_metadata: dict, metadata_list: list) -> np.ndarray:
    """
    Calculate Gower similarity between a dataset (represented by its metadata) and a list of other datasets
    (also represented by their metadata).

    Parameters
    ----------
    base_metadata : dict
        The metadata of the base dataset.
    metadata_list : list
        The list of metadata for other datasets.

    Returns
    -------
    np.ndarray
        An array of Gower similarity scores.
    """
    
    if "dataset_specific_metadata" not in base_metadata or "features" not in base_metadata["dataset_specific_metadata"]:
        logging.error("Base metadata does not have the expected structure")
        raise ValueError("Base metadata does not have the expected structure")

    logging.info("Calculating Gower similarity...")
    features1 = base_metadata["dataset_specific_metadata"]["features"]
    df1 = pd.DataFrame(features1)
    gower_similarity_scores = []

    for metadata2 in metadata_list:
        if "dataset_specific_metadata" not in metadata2 or "features" not in metadata2["dataset_specific_metadata"]:
            logging.error("Metadata does not have the expected structure")
            raise ValueError("Metadata does not have the expected structure")

        features2 = metadata2["dataset_specific_metadata"]["features"]
        df2 = pd.DataFrame(features2)

        df = pd.concat([df1, df2], axis=0)
        df.reset_index(drop=True, inplace=True)

        # Normalize numerical features
        num_features = [
            "mean",
            "median",
            "std_dev",
            "skewness",
            "kurtosis",
            "missing_values_proportion",
        ]
        scaler = MinMaxScaler()
        df[num_features] = scaler.fit_transform(df[num_features])
        df = df.fillna(0)

        gower_distance = gower_distance_matrix(df)
        gower_similarity = 1 - gower_distance[: len(df1), len(df1) :]
        gower_similarity_scores.append(np.median(gower_similarity))
        logging.info("Gower similarity calculated.")

    return np.array(gower_similarity_scores)

def find_most_similar_dataset(
    original_metadata: dict, synthetic_metadata_list: list
) -> int:
    """
    Find the most similar dataset to a given dataset among a list of synthetic datasets, using Gower similarity.

    Parameters
    ----------
    original_metadata : dict
        The metadata of the original dataset.
    synthetic_metadata_list : list
        A list of metadata for the synthetic datasets.

    Returns
    -------
    int
        The index of the most similar synthetic dataset in the synthetic_metadata_list.
    """
    
    logging.info("Finding the most similar dataset...")
    similarities = []
    for synthetic_metadata in synthetic_metadata_list:
        similarity = calculate_gower_similarity(original_metadata, [synthetic_metadata])
        similarities.append(similarity)

    most_similar_index = np.argmax(similarities)

    logging.info("Most similar dataset found at index %s", most_similar_index)

    return most_similar_index

def construct_metadata_structure(base_metadata, additional_properties):
    """
    Construct the metadata structure based on the given schema and additional properties,
    ensuring all elements are JSON serializable.
    """
    # Ensure all additional properties are serializable
    serializable_additional_properties = {}
    for key, value in additional_properties.items():
        if isinstance(value, pd.DataFrame):
            # Convert DataFrame to a dictionary
            serializable_additional_properties[key] = value.to_dict(orient='records')
        elif isinstance(value, pd.Series):
            # Convert Series to a list
            serializable_additional_properties[key] = value.tolist()
        elif hasattr(value, "isoformat"):
            # Convert datetime objects to string
            serializable_additional_properties[key] = value.isoformat()
        else:
            # Assume other types are serializable
            serializable_additional_properties[key] = value

    # Ensure base_metadata is a dictionary
    if isinstance(base_metadata, pd.DataFrame):
        base_metadata = base_metadata.to_dict(orient='records')[0]

    # Construct the serializable metadata structure
    metadata_structure = base_metadata.copy()
    metadata_structure.update(serializable_additional_properties)

    return metadata_structure


