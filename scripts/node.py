from typing import Dict, Optional, Tuple, List
from brownie import Channel  # type: ignore
from brownie.network.account import Account  # type: ignore
import scripts.network as network
from scripts.utils import APPEAL_PERIOD, ChannelStateMessage, sign, EthereumAddress, IPAddress


class LightningNode:
    """represents a payment channel node that can support several payment channels."""

    def __init__(self, account: Account, networking_interface: network.Network, ip: IPAddress) -> None:
        """
        Creates a new node that uses the given ethereum account as a wallet, 
        communicates on the given network and has the provided ip address. All values are assumed to be legal.
        """
        self.account = account
        self.networking_interface = networking_interface
        self.ip = ip
        self.dict_of_channels : Dict[EthereumAddress, Channel] = []


    def get_list_of_channels(self) -> List[EthereumAddress]:
        """
        returns a list of channels managed by this node. The list will include all open channels, 
        as well as closed channels that still have the node's money in them.
        Channels are removed from the list once funds have been withdrawn from them.
        """
        return list(self.dict_of_channels.keys())

    def establish_channel(self, other_party_eth_address: EthereumAddress, other_party_ip_address: IPAddress,  amount_in_wei: int) -> EthereumAddress:
        """
        Creates a new channel that connects the address of this node and the address of a peer.
        The channel is funded by the current node, using the given amount of money from the node's address.
        returns the address of the channel contract. Raises an exception if the amount given is not positive or if it exceeds the funds controlled by the account.
        The IPAddress and ethereum address of the other party are assumed to be correct.
        
        The other node should be notified of the channel creation throw the network object using a NOTIFY_OF_CHANNEL message
        """
        
    def get_eth_address(self) -> EthereumAddress:
        """
        returns the ethereum address of this node
        """

    def get_ip_address(self) -> IPAddress:
        """
        returns the IP address of this node
        """
        return self.ip
        
    def send(self, channel_address: EthereumAddress, amount_in_wei: int) -> None:
        """
        sends money in one of the open channels this node is participating in 
        and notifies the other node (via a RECEIVE_FUNDS message through the network object). 
        
        This operation should not send a transaction to the blockchain.
        The channel that should be used is identified by its contract's address.
        If the balance in the channel is insufficient, or if a node tries to send a 0 or negative amount, raise an exception (without messaging the other node).
        If the channel is already closed, raise an exception.
        """

    def get_current_channel_state(self, channel_address: EthereumAddress) -> ChannelStateMessage:
        """
        Gets the latest state of the channel that was accepted by the other node 
        (i.e., the last signed channel state message received from the other party).
        If the node is not aware of this channel, raise an exception.
        """
        
    def close_channel(self, channel_address: EthereumAddress, channel_state: Optional[ChannelStateMessage] = None) -> None:
        """
        Closes the channel at the given contract address.
        If a channel state is not provided, the node attempts to close the channel with the latest state that it has, 
        otherwise, it uses the channel state that is provided (this will allow a node to try to cheat its peer). 
        Closing the channel begins the appeal period automatically.
        If the channel is already closed, throw an exception.
        The other node is *not* notified of the closed channel.
        """
        
    def appeal_closed_chan(self, contract_address: EthereumAddress) -> None:
        """
        Chekcs if the channel at the given address needs to be appealed, i.e., if it was closed with an old channel state.
        If so, an appeal is sent to the blockchain.
        If the channel is still open, or if the appeal period has passed: raises an exception. 
        If the channel is closed but no appeal is needed, this method does nothing.
        """

    def withdraw_funds(self, contract_address: EthereumAddress) -> None:
        """
        Allows the user to claim the funds from the given channel.
        The channel needs to exist, and be after the appeal period time. Otherwise an exception should be raised.
        After the funds are withdrawn successfully, the node forgets this channel (it no longer appears in its open channel lists).
        If the balance of this node in the channel is 0, there is no need to create a withdraw transaction on the blockchain.
        """
    
    ###### Incoming Communication methods ###########

    def notify_of_channel(self, contract_address: EthereumAddress, other_party_ip_address: IPAddress) -> None:
        """
        This method is called to notify the node that another node created a channel in which it is participating. 
        The contract address for the channel is provided. 

        The message is ignored if one of the following holds: 
        1) This node is already aware of the channel
        2) The channel address that is provided does not involve this node as the second owner of the channel
        3) The channel is already closed
        4) The appeal period on the channel is too low
        """

    def ack_transfer(self, msg: ChannelStateMessage) -> None:
        """
        This method receives a confirmation from another node about a transfer. 
        The confirmation is supposed to be a signed message containing the last state sent to the other party, 
        but now signed by the other party. In fact, any message that is signed properly, with a larger serial number, 
        and that does not strictly decrease the balance of this node, should be accepted here.
        If the channel in this message does not exist, or the message is not valid, it is simply ignored.
        """

    def receive_funds(self, state_msg: ChannelStateMessage) -> None:
        """
        A method that is called when to notify this node that it receives funds through the channel.
        A signed message with the new channel state is receieved and should be checked. If this message is not valid 
        (bad serial number, signature, or amounts of money are not consistent with a transfer to this node) then this message is ignored.
        Otherwise, the same channel state message should be sent back, this time signed by the node as an ACK_TRANSFER message.
        """