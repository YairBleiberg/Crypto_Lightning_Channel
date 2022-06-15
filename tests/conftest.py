from typing import Any, Callable
import pytest
from scripts.node import LightningNode
from scripts.network import Network
from scripts.utils import EthereumAddress, IPAddress
from brownie import accounts, Channel  # type: ignore

ONE_ETH = 10**18


@pytest.fixture(autouse=True)
def shared_setup(fn_isolation: Any) -> None:
    pass


@pytest.fixture
def network() -> Network:
    return Network()


@pytest.fixture
def alice(network: Network) -> LightningNode:
    print("Creating node Alice")

    ip = IPAddress("52.174.73.44")
    node = LightningNode(accounts[0], network, ip)
    network.set_ip_address_of_node(node, ip)
    return node


@pytest.fixture
def bob(network: Network) -> LightningNode:
    print("Creating node Bob")

    ip = IPAddress("122.7.13.182")
    node = LightningNode(accounts[1], network, ip)
    network.set_ip_address_of_node(node, ip)
    return node


@pytest.fixture
def charlie(network: Network) -> LightningNode:
    print("Creating node Charlie")

    ip = IPAddress("117.23.0.1")
    node = LightningNode(accounts[2], network, ip)
    network.set_ip_address_of_node(node, ip)
    return node


@pytest.fixture
def chan_addr(alice: LightningNode, bob: LightningNode) -> EthereumAddress:
    chan_address = alice.establish_channel(
        bob.get_eth_address(), bob.get_ip_address(), 10 * ONE_ETH)
    return chan_address


@pytest.fixture
def chan(chan_addr: EthereumAddress) -> Channel:
    return Channel.at(chan_addr)
