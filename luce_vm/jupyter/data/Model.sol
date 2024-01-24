// SPDX-License-Identifier: MIT

pragma solidity ^0.6.2;


    import "./data/LuceRegistry.sol";
    import "./data/Token.sol";


    contract Model is ERC721 {

        //we need these variables to see whether a model is certified/published and to access the model
        // Contract testing variables
        uint public version;
        // About the data provider and dataset
        address public modelProvider;
        //we do not need any restrictions on publishing the dataset, we can therefore set this as a constant variable, the index for this can be found in the consent code smart contract, where the value should be equal to one.
        
        // not using this in any current functinos, might have to use it in future, for now commented
        //uint public constant LICENSE = 0;
        
        bytes private modelCardHash;
        string private link;  //im not sure what to do with this link, but ill just make a getter and setter for it
    
        //boolean to see whether the model is published.
        bool internal unpublished;
        
        // Registry
        address internal registry;
        address internal consent;
        address payable owner;

        
        // Cost variables
        uint public currentCost;
        uint internal costMult;
        uint internal costDiv;
        uint public profitMargin;
    
        // The keyword "public" makes those variables easily readable from outside.
        mapping (address => uint) internal mappedUsers;
        address[] internal addressIndices;
        //create a mapping to add certifiers.
        mapping(address => bool) public certifiers;
        //we also create a mapping to keep track of the versinos
        mapping(bytes => uint256) public modelVersionMapping;
        mapping(uint256 => bool) public versionCertified;
        //i also want to find the corresponding hash to a previous version, therefore i need a seperate mapping int => bytes
        mapping(uint256 => bytes) public versionModelMapping;
    
    
        // Events allow light clients to react to changes efficiently.
        event publishedModel(address sender, string link, bytes modelCardHash, uint256 version);
        event certifiedModel(address sender, string link, bytes modelCardHash, uint256 version);
        event updatedModel(address to, string link, bytes newHash, uint256 version);
        


        //this is code from the main contract that was already made for luce, we will here also set a modifier to keep track of the amount of gas used by the contract
        /**
        * @dev This modifier calculates the gas cost of any function that is called with it and adds the result to the contract's
        * currentCost.
        */
        modifier providerGasCost() {
            uint remainingGasStart = gasleft();

            _;

            uint remainingGasEnd = gasleft();
            uint usedGas = remainingGasStart - remainingGasEnd;
            // Add intrinsic gas and transfer gas. Need to account for gas stipend as well.
            usedGas.add(30700);
            // Possibly need to check max gasprice and usedGas here to limit possibility for abuse.
            uint gasCost = usedGas.mul(tx.gasprice).mul(profitMargin).div(100); // in wei
            // Add gas cost to total
            currentCost = currentCost.add(gasCost);
        }

        modifier onlyOwner(){
            require(msg.sender == owner, "Only owner can edit this");
            _;
        }

        //create a modifier where people who are licensed to certify by the owner can certify the models.

        modifier certifier() {
            require(certifiers[msg.sender], "Address not in the list");
            _;
        }

        //function where owner can add certifiers to certify the model(legal team), we need to be able to add and delete certifiers.

        function addCertifier(address newCertifier) public onlyOwner {
            certifiers[newCertifier] = true;
        } 

        function deleteCertifier(address oldCertifier) public onlyOwner {
            certifiers[oldCertifier] = false;
        }
        function checkIfCertified(address certified) public view returns(bool){
            return certifiers[certified];
        }

        function destroy() public onlyOwner {
            selfdestruct(owner);
        }

        function setMultis(uint mult, uint div) public onlyOwner providerGasCost {
            require(mult <= div);
            costMult = mult;
            costDiv = div;
        }
       /**
        * @dev This is a workaround to set the correct initial cost of deploying the contract. It may also be used to control
        * the contract cost (artificial cost). This function should be called right after the contract is deployed. Possibly, it
        * should be callable only once, but this is not implemented.
        * @param price is the total cost requesters will have to pay whenever requesting access to the data.
        */
        function setPrice(uint price) public onlyOwner providerGasCost {
            currentCost = price;
        }
    
        function setRegistryAddress(address userRegistry) onlyOwner public {
            registry = userRegistry;
        }
       /**
        * @dev This function lets the data provider set the fixed profitMargin they want to achieve by sharing this dataset.
        * @param _profitMargin is the percentage profit margin the provider strives for. Standard is 100, i.e. no-profit.
        */
        function setProfitMargin(uint _profitMargin) public onlyOwner providerGasCost {
            profitMargin = _profitMargin;
        }
        function certifyModel(bytes memory _hash) public certifier{
            //add some functionality to certify whether hash is correct. //TODO
            uint256 modelVersion = modelVersionMapping[_hash];
            versionCertified[modelVersion] = true;
            emit certifiedModel(msg.sender, link, _hash, modelVersion);
        }

        function publishModel(string memory _link, bytes memory _hash) public onlyOwner providerGasCost {
            require(unpublished == true, "1");
            
            version++;
            versionModelMapping[version] = _hash;
            modelVersionMapping[_hash] = version;
            versionCertified[version] = false;
            link = _link;
            //this part is commented because i was testing the rest of the functionality of the contract on remix itsef
            //LUCERegistry c = LUCERegistry(registry);

            //bool registered = c.checkProvider(msg.sender);
            //require(registered, "3");

            modelCardHash = _hash;
            emit publishedModel(msg.sender, _link, _hash, version); // Triggering event
            unpublished = false;
        }


        //This function keeps track of the version and reverts the function whenever it is updated with a hash was previously provided
        function updateModel(string memory _link, bytes memory newHash) public onlyOwner providerGasCost{
            require(unpublished == false);
            require(modelVersionMapping[newHash] == 0, 'Not a new hash string');
            version++;
            versionModelMapping[version] = newHash;
            modelVersionMapping[newHash] = version;
            versionCertified[version] = false;
            modelCardHash = newHash;
            link = _link;
            
            //this part is commented because i was testing the rest of the functionality of the contract on remix itsef
            //LUCERegistry c = LUCERegistry(registry);

            //bool registered = c.checkProvider(msg.sender);
            //require(registered, "3");

            // we do not need to check all the users who have acces, as everyone should have access to the model card,
            //we just send an event such that people can find the new link and the new hash
            emit updatedModel(msg.sender, _link, newHash, version);

        }
        //returns the hash of the most recent model
        function getMostRecentModelCardHash() public view returns(bytes memory){
            return modelCardHash;
        }
        //returns the hash of the model with specified vesion
        function getHashByVersion(uint256 version) public view returns(bytes memory){
            return versionModelMapping[version];
        }
        //create functions to get the version and check whether a certain version is certified.
        function getVersion(bytes memory _hash)public view returns(uint256){
            return modelVersionMapping[_hash];
        }
        function getCertfication(uint256 _version) public view returns(bool){
            return versionCertified[_version];
        }

        //getter and setter for link, we set the setLInk to onlyowner so only owner can change this.
        function setLink(string memory _link) public onlyOwner(){
            link = _link;
        }
        //for this we dont need to restrict to anything, as everyone should be able to see the link
        function getLink() public view returns(string memory){
            return link;
        }
        
        constructor() ERC721("ModelTest", "MTST") public {
            owner = msg.sender;
            modelProvider = msg.sender;
            certifiers[msg.sender] = true;
           // variable taken from the model smart contract.
            currentCost = 1e9; // hopefully this is 1 shannon (giga wei)
            costMult = 1;
            costDiv = 3;
            profitMargin = 100; // Cover costs exactly => scenario 2

            unpublished = true;
        }




        //these functions are compied from the LUCEMain contract, but i dont think it is necessary to combine the model and the dataset contract
        // as these do not really work together or need similar functionalities.
                /**
         * @dev This function returns the amount the next requester in line needs to pay in return for access.
         */
        function expectedCosts() public view returns(uint) {
            //returns the expected costs for the next data Requester
            uint individualCost = currentCost.mul(costMult).div(costDiv);
            return(individualCost);
        }
    
        /**
         * @dev Returns the contract balance. Only callable by the dataProvider.
         */
        function contractBalance() public view returns(uint256) {
            require (msg.sender == modelProvider, "Only the data provider can extract funds from the contract.");
            return uint256(address(this).balance);
        }
    
        /**
         * @dev Transfers all funds from the contract to the dataProvider. Only callable by the dataProvider.
         */
        function receiveFunds() public onlyOwner providerGasCost {
            msg.sender.transfer(address(this).balance); //this could just be the balance of the contract
        }
    }

