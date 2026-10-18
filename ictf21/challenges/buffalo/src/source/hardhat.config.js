require('hardhat-deploy');

/**
 * @type import('hardhat/config').HardhatUserConfig
 */
module.exports = {
  solidity: {
    "version": "0.8.4",
    "settings": {
      "optimizer": {
        "enabled": true,
        "runs": 1000,
      }
    }
  },
  "networks": {
    "buffalo": {
      "chainId": 40245,
      "url": "http://127.0.0.1:8545",
      "accounts": [
        "0xd75ea68287f03e31fc4422e649806208c6bc2b6dd989481ed36027556f79cb0d",
      ],
      "saveDeployments": true,
      "gasPrice": 2000000000,
    }
  },
  "namedAccounts": {
    "deployer": {
      "buffalo": "eb23624cc628e9ed64dba1e4532663fddfaecfa0",
    }
  }
};
