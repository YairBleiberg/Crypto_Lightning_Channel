//SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;


// Implement the API below. You can add functions as you wish, but do not change the behavior / signature of the 
// functions provided here.


contract Channel{
    // This contract will be deployed every time we establish a new payment channel between two participant.
    // The creator of the channel also injects funds that can be sent (and later possibly sent back) in this channel

    // define your own state variables...
    address payable channel_wallet;
    address payable first_owner_address;
    address payable second_owner_address;

    uint first_owner_balance;
    uint second_owner_balance = 0;
    uint appeal_period_len;
    bool is_closed = false;
    
    uint block_number_when_closing;

    constructor(address payable _other_owner, uint _appeal_period_len) payable{
        // creates a new payment channel with the other owner, and the given appeal period.
        // The constructor is payable. This way the creator puts money in the channel. 
        first_owner_address = payable(msg.sender);
        second_owner_address = _other_owner;
        appeal_period_len = _appeal_period_len;
        first_owner_balance = msg.value;
    }


    function one_sided_close(uint _balance1, uint _balance2, uint serial_num , uint8 v, bytes32 r, bytes32 s)
                            external{
        //Closes the channel based on a message by one party. 
        //If the serial number is 0, then the provided balance and signatures are ignored, and the channel is closed according to the initial split, giving all the money to party 1. 
        //Closing the channel starts the appeal period.
        // If any of the parameters are bad (signature,balance) the transaction reverts.
        // Additionally, the transactions would revert if the party closing the channel isn't one of the two participants.
        // _balance1 is the balance that belongs to the user that opened the channel. _balance2 is for the other user.
        if (serial_num == 0){
            block_number_when_closing = block.number;
            is_closed = true;
            return;
        }

        else{
            require(_verifySig(address(this), _balance1, _balance2, serial_num, v, r, s, signerPubKey);)
        }



    }

    function appeal_closure(uint _balance1, uint _balance2, uint serial_num , uint8 v, bytes32 r, bytes32 s) external{
        // appeals a one_sided_close. should show a signed message with a higher serial number. 
        // _balance1 belongs to the creator of the contract. _balance2 is the money going to the other user.
        // this function reverts upon any problem:
        // It can only be called during the appeal period.
        // only one of the parties participating in the channel can appeal. 
        // the serial number, balance, and signature must all be provided correctly.
    }

    function withdraw_funds(address payable dest_address) external{
        //Sends all of the money belonging to msg.sender to the destination address provided.
        //this should only be possible if the channel is closed, and appeals are over.
        // This transaction should revert upon any error.
    }

    // the following utility function will help you check signatures in solidity:
    function _verifySig(address contract_address, uint _balance1, uint _balance2, uint serial_num ,  //<--- the message
         uint8 v, bytes32 r, bytes32 s, // <---- The signature
         address signerPubKey) pure public returns (bool) {
        // v,r,s together make up the signature.
        // signerPubKey is the public key of the signer
        // contract_address, _balance1, _balance2, and serial_num constitute the message to be signed.
        // returns True if the sig checks out. False otherwise.

        // the message is made shorter:
        bytes32 hashMessage = keccak256(abi.encodePacked(contract_address, _balance1, _balance2, serial_num));

        //message signatures are prefixed in ethereum.
        bytes32 messageDigest = keccak256(abi.encodePacked(
            "\x19Ethereum Signed Message:\n32", hashMessage));
        //If the signature is valid, ecrecover ought to return the signer's pubkey:
        return ecrecover(messageDigest, v, r, s)==signerPubKey;
    }
}