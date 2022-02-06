// this token will be given out to users to stake which will allow them to engage
// the token is ERC-20

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {
    constructor() public ERC20("Dapp Token", "DAPP") {
        _mint(msg.sender, 1000000000000000000000000); // for initial supply (mint function is used to mint a new NFT at the given address) (message.sender indicates the current addres of the sender)
    }
}
