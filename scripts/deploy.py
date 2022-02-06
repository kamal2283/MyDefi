from importlib.abc import Loader
import json
from sqlite3.dbapi2 import register_adapter
from scripts.helpful_scripts import get_account, get_contract
from brownie import DappToken, TokenFarm, network, config
from web3 import Web3
import yaml
import json
import os
import shutil


KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token(front_end_update=False):
    account = get_account()
    dapp_token = DappToken.deploy(
        {"from": account}
    )  # dapp token is taking paramater account as dictonary
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )  # we also need to add some source bits

    # to verify this token farm contract we need to send some DappTokens to give out those tokens as rewards
    tx = dapp_token.transfer(
        token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE, {"from": account}
    )
    tx.wait(1)
    # dapp_taken, weth_token, Fau_token/dai
    weth_token = get_contract("weth_token")
    fau_token = get_contract(
        "fau_token"
    )  # we want to create here our own fake token to test it locally
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),  # dai
        fau_token: get_contract("dai_usd_price_feed"),  # dai
        weth_token: get_contract("eth_usd_price_feed"),  # eth
    }

    add_allowed_tokens(
        token_farm, dict_of_allowed_tokens, account
    )  # this will  add tokens that we want to allow and add a price feed contract
    if update_front_end:  # this is becasue if we want to update front end
        update_front_end()
    update_front_end()
    return token_farm, dapp_token


def add_allowed_tokens(
    token_farm, dict_of_allowed_tokens, account
):  # dict_of_allowed_ token is dictonary of token address and their associated price feeds
    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(
            token.address, {"from": account}
        )  # loop through tokens called the app allowed tokens
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_tokens[token], {"from": account}
        )
        set_tx.wait(1)
    return token_farm


def update_front_end():
    # Send the build folder
    copy_folders_to_front_end("./build", "./front_end/src/chain-info")

    # Sending the front end our config in JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("./front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
    print("Front end updated!")


def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def main():
    deploy_token_farm_and_dapp_token(front_end_update=True)

    # start at 13:48:02
