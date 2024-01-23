# Simulation of ML Model Certification/Validation

This project simulates generating metadata and synthetic datasets based on an original dataset, trains and evaluates machine learning models on the original and synthetic datasets, and validates the models on the most similar synthetic dataset.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Data](#data)
- [Metadata](#metadata)
- [Smart Contracts](#smart-contracts)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/irfankaradeniz/LUCE_Model_Monitoring.git
    ```
2. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

## Usage

1. Set the constants at the top of `main.py` to your desired values. These include the path to the original dataset, the target variable, the test size, the random state, and the number of synthetic datasets to generate.

2. Run `main.py`:
    ```
    python main.py
    ```

## Project Structure

The project is organized into several Python scripts, each responsible for a different part of the process:

- `data_processing.py`: Contains functions for loading the original dataset and generating synthetic datasets.
- `metadata.py`: Contains functions for generating metadata for a dataset and calculating Gower's similarity between datasets.
- `model_training.py`: Contains functions for splitting a dataset into training and test sets, training and evaluating models, and validating models on a synthetic dataset.
- `visualisations.py`: Contains functions for visualizing Gower's similarity and the performance metrics of the models.
- `main.py`: The main script that ties everything together. It loads the original dataset, generates synthetic datasets, trains and evaluates models on the synthetic datasets, and validates the models on the most similar synthetic dataset.

## Data

The original dataset used for the simulation is the Heart Failure Prediction dataset, which can be downloaded from [Kaggle](https://www.kaggle.com/datasets/fedesoriano/heart-failure-prediction). The dataset should be placed in the `data` folder.

## Metadata

The project uses a metadata schema to generate metadata for the original and synthetic datasets. The metadata schema is stored as a JSON file, `metadata_schema.json`, in the `metadata` folder.


## Smart Contracts

The project includes two Ethereum smart contracts:

- `ModelResultNFT`: This contract mints NFTs based on model results. Each NFT represents a model result and includes the accuracy, recall, F1 score, and metadata of the model.

- `ModelEvaluation`: This contract evaluates models based on their performance. It maintains a mapping of model results and a set of performance thresholds. A model is considered valid if its performance meets or exceeds the thresholds.

The smart contracts are located in the `contracts` folder and can be tested using the Remix IDE.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
