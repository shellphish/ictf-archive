pragma solidity ^0.8.4;

contract Registry {
    mapping(address => address) private current_addrs;

    event Registration(address owner, address contract_);

    function register(address a) public {
        current_addrs[msg.sender] = a;
        emit Registration(msg.sender, a);
    }

    function getContract(address team) public view returns (address) {
        return current_addrs[team];
    }
}
