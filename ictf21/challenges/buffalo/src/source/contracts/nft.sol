pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC721/presets/ERC721PresetMinterPauserAutoId.sol";
import "@openzeppelin/contracts/utils/Multicall.sol";

contract PhishToken is ERC721PresetMinterPauserAutoId, Multicall
{
    uint128 private nonce;
    mapping(address => uint128) private token_roots;
    mapping(uint128 => address) private root_owners;

    event RegisteredRoot(address sender, uint128 root);

    constructor (
        string memory name,
        string memory symbol,
        string memory baseTokenURI
    ) ERC721PresetMinterPauserAutoId(name, symbol, baseTokenURI)
    {
        nonce = 1;
    }

    function registerRoot(uint128 root) public {
        root_owners[root] = msg.sender;
        token_roots[msg.sender] = root;
        emit RegisteredRoot(msg.sender, root);
    }

    function requestToken(uint128 root, address to) public returns (uint256) {
        require(token_roots[msg.sender] == root);
        uint256 tokenId = (uint256(root) << (8 * 16)) | nonce;
        nonce += 1;
        _safeMint(to, tokenId);
        return tokenId;
    }
}

