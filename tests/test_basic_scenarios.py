from scripts.node import LightningNode
from scripts.utils import APPEAL_PERIOD, EthereumAddress, sign, ChannelStateMessage
from brownie import chain, Channel, accounts, history  # type: ignore
from brownie.exceptions import VirtualMachineError  # type: ignore
import pytest


ONE_ETH: int = 10**18


# here are tests for 3 basic scenarios. These also show how the work-flow with nodes proceeds.

def test_open_and_immediate_close(alice: LightningNode, bob: LightningNode) -> None:
    hist = len(history)

    alice_init_balance = accounts[0].balance()
    bob_init_balance = accounts[1].balance()

    # Creating channel
    chan_address = alice.establish_channel(
        bob.get_eth_address(), bob.get_ip_address(), ONE_ETH)
    assert hist+1 == len(history)

    # channel created", chan_addres
    chan = Channel.at(chan_address)
    assert chan.balance() == ONE_ETH

    # ALICE CLOSING UNILATERALLY
    alice.close_channel(chan_address)
    assert hist+2 == len(history)

    # Waiting
    chain.mine(APPEAL_PERIOD+2)

    # Bob Withdraws
    bob.withdraw_funds(chan_address)

    # Alice Withdraws
    alice.withdraw_funds(chan_address)
    assert hist+4 == len(history)

    assert Channel.at(chan_address).balance() == 0

    assert alice_init_balance == accounts[0].balance()
    assert bob_init_balance == accounts[1].balance()


def test_nice_open_transfer_and_close(alice: LightningNode, bob: LightningNode) -> None:
    alice_init_balance = accounts[0].balance()
    bob_init_balance = accounts[1].balance()

    # Creating channel
    chan_address = alice.establish_channel(
        bob.get_eth_address(), bob.get_ip_address(), 10 * ONE_ETH)
    chan = Channel.at(chan_address)
    assert chan.balance() == 10 * ONE_ETH

    # Alice sends money thrice
    hist = len(history)
    alice.send(chan_address, ONE_ETH)
    alice.send(chan_address, ONE_ETH)
    alice.send(chan_address, ONE_ETH)
    assert hist == len(history)

    # BOB CLOSING UNILATERALLY
    bob.close_channel(chan_address)

    # waiting
    chain.mine(APPEAL_PERIOD)
    assert Channel.at(chan_address).balance() == 10 * ONE_ETH

    # Bob Withdraws
    bob.withdraw_funds(chan_address)
    assert Channel.at(chan_address).balance() == 7 * ONE_ETH

    # Alice Withdraws
    alice.withdraw_funds(chan_address)
    assert Channel.at(chan_address).balance() == 0

    assert alice_init_balance == accounts[0].balance() + 3*ONE_ETH
    assert bob_init_balance == accounts[1].balance() - 3*ONE_ETH


def test_alice_tries_to_cheat(alice: LightningNode, bob: LightningNode) -> None:
    alice_init_balance = accounts[0].balance()
    bob_init_balance = accounts[1].balance()

    # Creating channel
    chan_address = alice.establish_channel(
        bob.get_eth_address(), bob.get_ip_address(), 10 * ONE_ETH)

    # Alice sends money thrice
    alice.send(chan_address, 1 * ONE_ETH)
    old_state = alice.get_current_channel_state(chan_address)
    alice.send(chan_address, 1 * ONE_ETH)
    alice.send(chan_address, 1 * ONE_ETH)

    # ALICE TRIES TO CHEAT
    alice.close_channel(chan_address, old_state)

    # Waiting one block
    chain.mine(1)

    # Bob checks if he needs to appeal, and appeals if he does
    bob.appeal_closed_chan(chan_address)

    # waiting
    chain.mine(APPEAL_PERIOD)

    # Bob Withdraws
    bob.withdraw_funds(chan_address)

    # Alice Withdraws
    alice.withdraw_funds(chan_address)

    assert alice_init_balance == accounts[0].balance() + 3*ONE_ETH
    assert bob_init_balance == accounts[1].balance() - 3*ONE_ETH


# a sample communication test:
def test_node_rejects_receive_message_of_unknown_channel(alice: LightningNode, bob: LightningNode, charlie: LightningNode,
                                                         chan_addr: EthereumAddress) -> None:
    hist = len(history)
    msg = ChannelStateMessage(chan_addr, 5*ONE_ETH, 5*ONE_ETH, 10)
    signed_msg = sign(msg, alice.get_eth_address())
    charlie.receive_funds(signed_msg)  # the message here should be ignored

    assert charlie.get_list_of_channels() == []
    with pytest.raises(Exception):
        charlie.get_current_channel_state(chan_addr)
    assert hist == len(history)


# when we do something wrong, like close the contract twice
# we should be stopped both by the node and by the contract. Here we are stopped by the contract:
def test_close_by_alice_twice(alice: LightningNode, chan: Channel) -> None:
    alice.send(chan.address, ONE_ETH)
    msg = alice.get_current_channel_state(chan.address)
    alice.close_channel(chan.address)

    with pytest.raises(Exception):
        alice.close_channel(chan.address)

    v, r, s = msg.sig

    with pytest.raises(VirtualMachineError):
        # Here we try to send the transaction to close manually, and it should revert!
        tx = chan.one_sided_close(msg.balance1, msg.balance2, msg.serial_number, v, r, s, {
            "from": alice.get_eth_address()})


# Here the node refuses to close the closed channel once again (no transaction should be sent!)
def test_cant_close_channel_twice(alice: LightningNode, bob: LightningNode, chan_addr: EthereumAddress) -> None:
    alice.send(chan_addr, 1*ONE_ETH)
    alice.close_channel(chan_addr)
    hist = len(history)
    with pytest.raises(Exception):
        alice.close_channel(chan_addr)
    with pytest.raises(Exception):
        bob.close_channel(chan_addr)
    assert len(history) == hist
