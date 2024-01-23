import pandas as pd
import numpy as np
import logging

from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier

from data_processing import load_dataset, generate_synthetic_datasets
from metadata import generate_metadata, calculate_gower_similarity
from model_training import train_test_split_with_encoding, get_performance_metrics_on_synthetic_datasets, train_and_evaluate_model_kfold, validate_model
from visualisations import visualize_gower_similarity, plot_performance_metrics, plot_kfold

from model_training import get_model_cards 
import model_card_toolkit as mct
import hashlib
from metadata import construct_metadata_structure
import json
# Constants
DATASET_PATH = "data/heart.csv"
METADATA_SCHEMA_PATH = "metadata/metadata_schema.json"
TARGET_VARIABLE = "HeartDisease"
TEST_SIZE = 0.2
RANDOM_STATE = 42
N_SYNTHETIC_DATASETS = 10
N_SPLITS = 5  # for k-fold cross-validation

# Set up logging configurations
LOGGING_CONFIG = {"filename": "simulation.log", "level": logging.INFO, "format": "%(asctime)s %(message)s"}
logging.basicConfig(**LOGGING_CONFIG)

def main():
    """
    Main function to execute the data simulation, model training, evaluation, and validation process.
    """
    # Load the dataset
    loaded_dataset = load_dataset(DATASET_PATH)

    # Generate metadata for the loaded dataset
    metadata_schema = pd.read_json(METADATA_SCHEMA_PATH)
    loaded_dataset_metadata = generate_metadata(loaded_dataset, metadata_schema)

    # Generate synthetic datasets
    synthetic_datasets = generate_synthetic_datasets(loaded_dataset, TARGET_VARIABLE, num_datasets=N_SYNTHETIC_DATASETS)

    # Generate metadata for synthetic datasets
    synthetic_datasets_metadata_list = [generate_metadata(df, metadata_schema.copy()) for df in synthetic_datasets]

    # Find the most similar dataset using Gower's similarity
    gower_similarity_scores = calculate_gower_similarity(loaded_dataset_metadata, synthetic_datasets_metadata_list)
    most_similar_dataset = synthetic_datasets[np.argmax(gower_similarity_scores)]

    # Visualize Gower's similarity results
    visualize_gower_similarity(loaded_dataset, synthetic_datasets, gower_similarity_scores)

    # Define classifiers and k-fold for model training
    classifiers = [{"name": "Random Forest", "clf": RandomForestClassifier(random_state=RANDOM_STATE)}]
    kfold = KFold(n_splits=N_SPLITS, random_state=RANDOM_STATE, shuffle=True)

    # Train, evaluate, and validate models
    X_train, X_test, y_train, y_test = train_test_split_with_encoding(loaded_dataset, TARGET_VARIABLE, test_size=TEST_SIZE, random_state=RANDOM_STATE)
    
    
    for classifier_info in classifiers:
        logging.info(f"Testing {classifier_info['name']}")

        accuracies = []
        recalls = []
        f1_scores = []
        precisions = []
        roc_aucs = []

        for train_idx, test_idx in kfold.split(X_train, y_train):
            X_train_fold, X_test_fold = X_train.iloc[train_idx], X_train.iloc[test_idx]
            y_train_fold, y_test_fold = y_train.iloc[train_idx], y_train.iloc[test_idx]

            (
                accuracy,
                recall,
                f1,
                precision,
                roc_auc,
                conf_matrix,
            ) = train_and_evaluate_model_kfold(
                X_train_fold,
                y_train_fold,
                X_test_fold,
                y_test_fold,
                classifier_info["clf"],
            )

            accuracies.append(accuracy)
            recalls.append(recall)
            f1_scores.append(f1)
            precisions.append(precision)
            roc_aucs.append(roc_auc)

        # Calculate the average performance metrics
        avg_accuracy = np.mean(accuracies)
        avg_recall = np.mean(recalls)
        avg_f1 = np.mean(f1_scores)
        avg_precision = np.mean(precisions)
        avg_roc_auc = np.mean(roc_aucs)

        # logging.info(f"{classifier_info['name']} - Trained and evaluated model using k-fold cross-validation (accuracy={avg_accuracy}, recall={avg_recall}, f1={avg_f1}, precision={avg_precision}, roc_auc={avg_roc_auc})")

        validation_results = validate_model(
            most_similar_dataset, TARGET_VARIABLE, classifier_info["clf"]
        )
    
    plot_kfold(accuracies, recalls, f1_scores, precisions, roc_aucs, classifiers)

    # Train and evaluate the model on each synthetic dataset and store the metrics
    performance_metrics_list = get_performance_metrics_on_synthetic_datasets(synthetic_datasets, classifiers, TARGET_VARIABLE, TEST_SIZE, RANDOM_STATE)

    # Plot the performance metrics across synthetic datasets
    metric_names = ["accuracy", "recall", "f1", "precision", "roc_auc"]
    plot_performance_metrics(performance_metrics_list, metric_names)
    logging.info("Simulation completed")

    metrics = {
    "accuracy": str(avg_accuracy),
    "recall": str(avg_recall),
    "f1": str(avg_f1),
    "precision": str(avg_precision),
    "roc_auc": str(avg_roc_auc)
    }

    html, update = get_model_cards(X_train, y_train, X_test, y_test, classifier_info["clf"], metrics)
    html_file_name = f"model_card_{classifier_info['name']}.html"

    # Write the HTML content to a file
    with open(html_file_name, 'w') as file:
        file.write(html)
    
    hash_object = hashlib.sha256(html.encode())
    hash_hex = hash_object.hexdigest()
    hash_file_name = f"model_card_hash_{classifier_info['name']}.txt"
    with open(hash_file_name, 'w') as file:
        file.write(hash_hex)

    logging.info(f"Model card exported to {html_file_name}")
    logging.info(f"Hash of model card exported to {hash_file_name}")

    additional_properties = {
        "developer": "Developer Address",
        "owner": "Owner Address",
        "date": "23/11/2013",
        "state": "Pre-Market: in evaluation",
        "claim": hash_hex,  # This is the hash you generated earlier
        "link": "file:///home/maria/Documents/Master%20Program%20UM/Research%20Project/Sem%201/LUCE_Model_Monitoring-main/model_card_Random%20Forest.html"  # Replace with actual link to model card
    }

    # Generate the base metadata
    base_metadata = generate_metadata(loaded_dataset, metadata_schema)

    # Construct the full metadata structure
    full_metadata = construct_metadata_structure(base_metadata, additional_properties)

    # You can now use `full_metadata` as needed, for example, exporting it to a file:
    with open('metadata.json', 'w') as metadata_file:
       json.dump(full_metadata, metadata_file, indent=4)

    logging.info("Full metadata structure created and exported.")


if __name__ == "__main__":
    main()
