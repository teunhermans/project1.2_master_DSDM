// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract ModelResultNFT is ERC721URIStorage {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct ModelResult {
        uint256 accuracy;
        uint256 recall;
        uint256 f1Score;
        string metadata;
        string description; 
    }

    mapping(uint256 => ModelResult) public modelResults;

    constructor() ERC721("ModelResult", "MDR") {}

    function mintModelResult(
        address recipient,
        uint256 accuracy,
        uint256 recall,
        uint256 f1Score,
        string memory metadata,
        string memory description 
    ) public returns (uint256) {
        _tokenIds.increment();

        uint256 newItemId = _tokenIds.current();
        _mint(recipient, newItemId);

        // Added description to the ModelResult struct
        modelResults[newItemId] = ModelResult(accuracy, recall, f1Score, metadata, description);

        return newItemId;
    }

    function getModelResult(uint256 tokenId) public view returns (ModelResult memory) {
        return modelResults[tokenId];
    }
}
