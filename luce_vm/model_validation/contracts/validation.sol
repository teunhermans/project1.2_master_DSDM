// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract ModelEvaluation {
    struct ModelResult {
        uint256 modelId;
        uint256 version;
        uint256 accuracy;
        uint256 recall;
        uint256 f1Score;
        string metadata;
    }

    // Define the initial performance thresholds
    uint256 public accuracyThreshold = 80;
    uint256 public recallThreshold = 80;
    uint256 public f1ScoreThreshold = 80;
    
    // Keep track of the total performance for each metric
    uint256 private totalAccuracy;
    uint256 private totalRecall;
    uint256 private totalF1Score;
    
    // Keep track of the number of models evaluated
    uint256 private modelCount;
    
    mapping(uint256 => ModelResult[]) public modelResults;
    
    event ModelResultAdded(uint256 modelId, uint256 version);
    event ModelValidated(uint256 modelId, uint256 version);
    
    function addModelResult(
        uint256 modelId,
        uint256 version,
        uint256 accuracy,
        uint256 recall,
        uint256 f1Score,
        string memory metadata
    ) public {
        modelResults[modelId].push(ModelResult(modelId, version, accuracy, recall, f1Score, metadata));

        // Increment the model count first
        modelCount++;

        // Update the total performance for each metric
        totalAccuracy += accuracy;
        totalRecall += recall;
        totalF1Score += f1Score;

        // Now, as modelCount has been incremented, you can safely perform the division
        accuracyThreshold = totalAccuracy / modelCount;
        recallThreshold = totalRecall / modelCount;
        f1ScoreThreshold = totalF1Score / modelCount;

        emit ModelResultAdded(modelId, version);
    }
    
    function validateModel(uint256 modelId, uint256 version) public view returns (bool) {
        require(modelResults[modelId].length > version, "Model result not found");
        
        ModelResult memory result = modelResults[modelId][version];
        
        // Check if the model's performance meets the thresholds
        if (result.accuracy >= accuracyThreshold &&
            result.recall >= recallThreshold &&
            result.f1Score >= f1ScoreThreshold) {
            return true;
        } else {
            return false;
        }
    }
}