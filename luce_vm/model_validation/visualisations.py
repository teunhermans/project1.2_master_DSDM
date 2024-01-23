import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import logging
from typing import List
import logging

def visualize_gower_similarity(
    loaded_dataset, synthetic_datasets, gower_similarity_scores
):
    """
    Visualizes the similarity between an original dataset and synthetic datasets using Gower's similarity scores. 
    Generates a heatmap, bar chart, histograms for each feature and a scatterplot matrix.

    Parameters
    ----------
    loaded_dataset : pd.DataFrame
        The original dataset.
    synthetic_datasets : list of pd.DataFrame
        A list of synthetic datasets.
    gower_similarity_scores : np.array
        The Gower's similarity scores between the original dataset and each synthetic dataset.
    """
    
    logging.info("Starting visualization of Gower's similarity scores...")

    # Reshape gower_similarity_scores to a 2D array
    gower_similarity_scores = gower_similarity_scores.reshape(-1, 1)

    # Heatmap of Gower's similarity matrix
    plt.figure(figsize=(10, 1))
    sns.heatmap(
        gower_similarity_scores,
        annot=True,
        cmap="coolwarm",
        cbar=False,
        xticklabels=False,
    )
    plt.title("Heatmap of Gower's Similarity Matrix")
    plt.ylabel("Original Dataset")
    plt.xlabel("Synthetic Datasets")
    plt.show()

    # Bar chart of Gower's similarity scores
    plt.figure()
    plt.bar(range(1, len(synthetic_datasets) + 1), gower_similarity_scores.flatten())
    plt.xticks(range(1, len(synthetic_datasets) + 1))  # adjust xticks here
    plt.title("Bar Chart of Gower's Similarity Scores")
    plt.xlabel("Synthetic Dataset Index")
    plt.ylabel("Gower's Similarity Score")
    plt.show()

def plot_performance_metrics(
    performance_metrics_list: List[dict], metric_names: List[str]
):
    """
    Plots bar charts for each specified performance metric across multiple synthetic datasets.

    Parameters
    ----------
    performance_metrics_list : List[dict]
        A list of dictionaries, where each dictionary contains performance metrics for a synthetic dataset.
    metric_names : List[str]
        A list of the names of the performance metrics to plot.
    """
    
    n_datasets = len(performance_metrics_list)
    n_metrics = len(metric_names)

    for metric_name in metric_names:
        metric_values = [metrics[metric_name] for metrics in performance_metrics_list]

        plt.figure(figsize=(10, 5))
        plt.bar(range(n_datasets), metric_values)
        plt.xlabel("Synthetic Dataset Index")
        plt.ylabel(metric_name.capitalize())
        plt.title(f"{metric_name.capitalize()} Across Synthetic Datasets")
        plt.xticks(range(n_datasets))
        plt.grid(True)
        plt.show()
        
        
def plot_kfold(accuracies, recalls, f1_scores, precisions, roc_aucs, classifiers):
    # Get the classifier name from the classifiers dictionary
    classifier_name = classifiers[0]['name']

    # Create a dictionary to store the performance metrics for each fold
    metrics = {
        'Accuracy': accuracies,
        'Recall': recalls,
        'F1 Score': f1_scores,
        'Precision': precisions,
        'ROC AUC': roc_aucs
    }

    # Calculate the average performance metrics
    avg_metrics = {metric_name: np.mean(metric_values) for metric_name, metric_values in metrics.items()}

    # Define colors for the bars
    colors = ['blue', 'orange', 'green', 'red', 'purple']

    # Plot the performance metrics for each fold
    plt.figure(figsize=(10, 6))
    bars = plt.bar(avg_metrics.keys(), avg_metrics.values(), color=colors)
    plt.xlabel('Performance Metric')
    plt.ylabel('Average Score')
    plt.title(f'Average Performance Metrics - {classifier_name}')
    plt.xticks(rotation=45)

    # Add numbers on top of the bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom')

    plt.show()

