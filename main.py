import requests
import time
import json
from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants from environment variables
ZX_API_KEY = os.getenv("ZX_API_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ETH_ADDRESS = os.getenv("ETH_ADDRESS")
NETWORK = os.getenv("NETWORK")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
CMC_PRO_API_KEY = os.getenv("CMC_PRO_API_KEY")

# Network configurations
network_settings = {
    # Base network configuration
    "base": {
        "ZEROX_PRICE_ENDPOINT": "https://base.api.0x.org/swap/v1/price",
        "ZEROX_QUOTE_ENDPOINT": "https://base.api.0x.org/swap/v1/quote",
        "ETH_TOKEN_ADDRESS": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
        "AMKT_TOKEN_ADDRESS": "0x13F4196cC779275888440b3000AE533BbBbC3166",
        "HTTP_PROVIDER_URL": "https://mainnet.base.org",
    },
    # Additional networks can be added here
}

# Select the current network configuration
current_network_settings = network_settings.get(NETWORK)
if not current_network_settings:
    raise ValueError(f"Unsupported network: {NETWORK}")

# Update constants with network-specific values
ZEROX_PRICE_ENDPOINT = current_network_settings["ZEROX_PRICE_ENDPOINT"]
ZEROX_QUOTE_ENDPOINT = current_network_settings["ZEROX_QUOTE_ENDPOINT"]
ETH_TOKEN_ADDRESS = current_network_settings["ETH_TOKEN_ADDRESS"]
AMKT_TOKEN_ADDRESS = current_network_settings["AMKT_TOKEN_ADDRESS"]
w3 = Web3(Web3.HTTPProvider(current_network_settings["HTTP_PROVIDER_URL"]))
mainnet_w3 = Web3(Web3.HTTPProvider("https://rpc.ankr.com/eth"))

# Other constants
AMKT_NAV_ENDPOINT = "https://amkt.batterylabs.io/api/data/getAmktSummary"
COINGECKO_ETH_PRICE_ENDPOINT = (
    "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
)
CHECK_INTERVAL = 120  # Interval for checking arbitrage opportunities in seconds
AMKT_AMOUNT = 1  # Amount of AMKT to trade
SLIPPAGE_PERCENTAGE = "0.003"  # Slippage percentage for 0x trades

ADDRESSES = {
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "WSTETH": "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
    "MATIC": "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
    "SHIB": "0x95aD61b0a150d79219dCF64E1E6Cc01f0B64C4cE",
    "LINK": "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "LDO": "0x5A98FcBEA516Cf06857215779Fd812CA3beF1B32",
    "MNT": "0x3c3a81e81dc49A522A592e7622A7E711c06bf354",
    "CRO": "0xA0b73E1Ff0B80914AB6fe0444E65848C4C34450b",
    "QNT": "0x4a220E6096B25EADb88358cb44068A3248254675",
    "ARB": "0xB50721BCf8d664c30412Cfbc6cf7a15145234ad1",
    "MKR": "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
    "AAVE": "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "GRT": "0xc944E90C64B2c07662A292be6244BDf05Cda44a7",
    "WORMHOLE_BNB": "0x418D75f65a02b3D53B2418FB8E1fe493759c7605",
    "WORMHOLE_SOL": "0xD31a59c85aE9D8edEFeC411D448f90841571b89c",
    "WORMHOLE_AVAX": "0x85f138bfEE4ef8e540890CFb48F620571d67Eda3",
    "21CO_BNB": "0x1bE9d03BfC211D83CFf3ABDb94A75F9Db46e1334",
    "21CO_SOL": "0xb80a1d87654BEf7aD8eB6BBDa3d2309E31D4e598",
    "21CO_AVAX": "0x399508A43d7E2b4451cd344633108b4d84b33B03",
    "ASTETH": "0x27C2B9fd547EAd2c05C305BeE2399A55811257c2",
    "21CO_XRP": "0x0d3bd40758dF4F79aaD316707FcB809CD4815Ffe",
    "21CO_ADA": "0x9c05d54645306d4C4EAd6f75846000E1554c0360",
    "21CO_DOGE": "0xD2aEE1CE2b4459dE326971DE036E82f1318270AF",
    "21CO_DOT": "0xF4ACCD20bFED4dFFe06d4C85A7f9924b1d5dA819",
    "21CO_LTC": "0x9F2825333aa7bC2C98c061924871B6C016e385F3",
    "21CO_BCH": "0xFf4927e04c6a01868284F5C3fB9cba7F7ca4aeC0",
    "STETH": "0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
}

DECIMALS = {
    "WBTC": 8,
    "WSTETH": 18,
    "MATIC": 18,
    "SHIB": 18,
    "LINK": 18,
    "UNI": 18,
    "LDO": 18,
    "MNT": 18,
    "CRO": 18,
    "QNT": 18,
    "ARB": 18,
    "MKR": 18,
    "AAVE": 18,
    "GRT": 18,
    "WORMHOLE_BNB": 18,
    "WORMHOLE_SOL": 9,
    "WORMHOLE_AVAX": 18,
    "21CO_BNB": 8,
    "21CO_SOL": 9,
    "21CO_AVAX": 18,
    "ASTETH": 18,
    "21CO_XRP": 6,
    "21CO_ADA": 6,
    "21CO_DOGE": 8,
    "21CO_DOT": 10,
    "21CO_LTC": 8,
    "21CO_BCH": 8,
    "STETH": 18,
}


# Helper functions
def convert_units_to_numbers(units):
    return {asset: units[asset] / (10 ** DECIMALS[asset]) for asset in units}


def convert_address_to_symbol(val):
    for key, value in ADDRESSES.items():
        if val == value:
            return key


def get_amkt_nav():
    current_units = get_current_units()
    current_units_numbers = convert_units_to_numbers(current_units)
    market_data = get_market_data()
    nav = sum(
        calculate_implementation_value(asset, current_units_numbers[asset], market_data)
        for asset in current_units_numbers
    )
    return nav


def get_eth_usd_price():
    response = requests.get(COINGECKO_ETH_PRICE_ENDPOINT)
    data = response.json()
    print("Fetched ETH USD Price: ${}".format(data['ethereum']['usd']))
    return data['ethereum']['usd']


def get_current_units():
    result = get_virtual_units()

    units = {convert_address_to_symbol(item[0]): item[1] for item in result}
    return units


def get_virtual_units():
    vault_address = "0xf3bCeDaB2998933c6AAD1cB31430D8bAb329dD8C"
    vault_abi = '[{"inputs":[{"internalType":"contract IIndexToken","name":"_indexToken","type":"address"},{"internalType":"address","name":"_owner","type":"address"},{"internalType":"address","name":"_feeRecipient","type":"address"},{"internalType":"address","name":"_emergencyResponder","type":"address"},{"internalType":"uint256","name":"_inflationRate","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"AMKTVaultEmergency","type":"error"},{"inputs":[],"name":"AMKTVaultFeeTooEarly","type":"error"},{"inputs":[],"name":"AMKTVaultFeeTooSmall","type":"error"},{"inputs":[],"name":"AMKTVaultInflationRateTooLarge","type":"error"},{"inputs":[{"internalType":"address","name":"who","type":"address"}],"name":"AMKTVaultOnly","type":"error"},{"inputs":[],"name":"AMKTVaultOnlyInvokers","type":"error"},{"inputs":[],"name":"VaultInvariant","type":"error"},{"inputs":[],"name":"VaultZeroCheck","type":"error"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferStarted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"emergencyResponder","type":"address"}],"name":"VaultEmergencyResponderSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"bool","name":"emergency","type":"bool"}],"name":"VaultEmergencySet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"VaultFeeMinted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"feeRecipient","type":"address"}],"name":"VaultFeeRecipientSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"inflationRate","type":"uint256"}],"name":"VaultInflationRateSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"issuance","type":"address"}],"name":"VaultIssuanceSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"rebalancer","type":"address"}],"name":"VaultRebalancerSet","type":"event"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"emergency","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"emergencyResponder","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"feeRecipient","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"indexToken","outputs":[{"internalType":"contract IIndexToken","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"inflationRate","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"invariantCheck","outputs":[],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"invokeBurn","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct IVault.InvokeERC20Args[]","name":"args","type":"tuple[]"}],"name":"invokeERC20s","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"invokeMint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"virtualUnits","type":"uint256"}],"internalType":"struct IVault.SetNominalArgs[]","name":"args","type":"tuple[]"}],"name":"invokeSetNominals","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_token","type":"address"}],"name":"isUnderlying","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"issuance","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"lastKnownTimestamp","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"rebalancer","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bool","name":"_emergency","type":"bool"}],"name":"setEmergency","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_emergencyResponder","type":"address"}],"name":"setEmergencyResponder","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_feeRecipient","type":"address"}],"name":"setFeeRecipient","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_inflationRate","type":"uint256"}],"name":"setInflationRate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_issuance","type":"address"}],"name":"setIssuance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_rebalancer","type":"address"}],"name":"setRebalancer","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"tryInflation","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"underlying","outputs":[{"internalType":"address[]","name":"","type":"address[]"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"underlyingLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"}],"name":"virtualUnits","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"virtualUnits","outputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"units","type":"uint256"}],"internalType":"struct TokenInfo[]","name":"","type":"tuple[]"}],"stateMutability":"view","type":"function"}]'
    vault = mainnet_w3.eth.contract(address=vault_address, abi=vault_abi)
    return vault.functions.virtualUnits().call()


def get_steth_by_wsteth(_wstETH):
    wstETH_address = "0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0"
    wstETH_abi = '[{"inputs":[{"internalType":"contract IStETH","name":"_stETH","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"DOMAIN_SEPARATOR","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_wstETHAmount","type":"uint256"}],"name":"getStETHByWstETH","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_stETHAmount","type":"uint256"}],"name":"getWstETHByStETH","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"nonces","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"value","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint8","name":"v","type":"uint8"},{"internalType":"bytes32","name":"r","type":"bytes32"},{"internalType":"bytes32","name":"s","type":"bytes32"}],"name":"permit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"stETH","outputs":[{"internalType":"contract IStETH","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"stEthPerToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"tokensPerStEth","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_wstETHAmount","type":"uint256"}],"name":"unwrap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_stETHAmount","type":"uint256"}],"name":"wrap","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"nonpayable","type":"function"},{"stateMutability":"payable","type":"receive"}]'
    wstETH = mainnet_w3.eth.contract(address=wstETH_address, abi=wstETH_abi)
    return wstETH.functions.getStETHByWstETH(_wstETH).call()


def get_cmc_data(symbols):
    headers = {"X-CMC_PRO_API_KEY": CMC_PRO_API_KEY}
    params = {
        "symbol": ",".join(symbols),
    }
    response = requests.get(
        "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
        headers=headers,
        params=params,
    )
    return response.json()


def get_market_data():
    # Combine old and new assets and remove duplicates
    unique_assets = list(
        set(
            asset
            for asset in [
                "BTC",
                "ETH",
                "BNB",
                "XRP",
                "SOL",
                "ADA",
                "DOGE",
                "LINK",
                "AVAX",
                "MATIC",
                "DOT",
                "LTC",
                "SHIB",
                "BCH",
                "UNI",
            ]
        )
    )
    # Fetch price and circulating supply for each asset
    data = get_cmc_data(unique_assets)

    market_data = {}
    for asset in data["data"].values():
        price = asset["quote"]["USD"]["price"]
        circulating_supply = asset["circulating_supply"]
        market_cap = price * circulating_supply
        market_data[asset["symbol"]] = {
            "price": price,
            "market_cap": market_cap,
        }
    return market_data


def get_0x_price(sell_token, buy_token, sell_amount):
    params = {
        "sellToken": sell_token,
        "buyToken": buy_token,
        "sellAmount": sell_amount,
        "takerAddress": ETH_ADDRESS,
    }
    headers = {"0x-api-key": ZX_API_KEY}
    response = requests.get(ZEROX_PRICE_ENDPOINT, params=params, headers=headers)
    data = response.json()
    estimated_gas = data.get("estimatedGas", 0)
    print(
        "Fetched 0x price for {} AMKT with estimated gas: {}".format(
            AMKT_AMOUNT, estimated_gas
        )
    )
    print(data)
    return data


def calculate_implementation_value(implementation, numbers, market_data):
    reference_data = {}
    if implementation == "WSTETH":
        reference_data = market_data["ETH"]
        return (
            numbers * reference_data["price"] * get_steth_by_wsteth(10**18) / (10**18)
        )
    if implementation == "WBTC":
        reference_data = market_data["BTC"]
    elif implementation == "ASTETH":
        reference_data = market_data["ETH"]
    elif implementation == "WORMHOLE_BNB":
        reference_data = market_data["BNB"]
    elif implementation == "WORMHOLE_SOL":
        reference_data = market_data["SOL"]
    elif implementation == "WORMHOLE_AVAX":
        reference_data = market_data["AVAX"]
    elif implementation == "21CO_XRP":
        reference_data = market_data["XRP"]
    elif implementation == "21CO_SOL":
        reference_data = market_data["SOL"]
    elif implementation == "21CO_ADA":
        reference_data = market_data["ADA"]
    elif implementation == "21CO_DOGE":
        reference_data = market_data["DOGE"]
    elif implementation == "21CO_DOT":
        reference_data = market_data["DOT"]
    elif implementation == "21CO_LTC":
        reference_data = market_data["LTC"]
    elif implementation == "21CO_BCH":
        reference_data = market_data["BCH"]
    elif implementation == "21CO_BNB":
        reference_data = market_data["BNB"]
    elif implementation == "21CO_SOL":
        reference_data = market_data["21CO_SOL"]
    elif implementation == "21CO_AVAX":
        reference_data = market_data["AVAX"]
    else:
        reference_data = market_data[implementation]

    return numbers * reference_data["price"]


def validate_inventory(nav, eth_price, premium_or_discount):
    print("Checking inventory...")
    eth_balance_wei = w3.eth.get_balance(ETH_ADDRESS)
    eth_balance = w3.from_wei(eth_balance_wei, "ether")
    eth_balance_usd = float(eth_balance) * eth_price
    print(f"ETH Balance USD: {eth_balance_usd} USD")

    amkt_contract = w3.eth.contract(
        address=AMKT_TOKEN_ADDRESS,
        abi=[
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function",
            }
        ],
    )
    amkt_balance_wei = amkt_contract.functions.balanceOf(ETH_ADDRESS).call()
    amkt_balance = amkt_balance_wei / 10**18
    amkt_balance_usd = float(amkt_balance) * nav
    print(f"AMKT Balance: {amkt_balance_usd} USD")

    print("eth_balance: ", eth_balance)
    print("amkt_balance: ", amkt_balance)
    print("eth amount: ", AMKT_AMOUNT * nav / eth_price)
    if premium_or_discount > 0:
        # make sure there is enough AMKT balance to sell
        if amkt_balance < AMKT_AMOUNT:
            print("Not enough AMKT balance to sell. Skipping trade...")
            return False
        else:
            print("Enough AMKT balance to sell. Proceeding with trade...")
    else:
        # make sure there is enough ETH balance to buy AMKT
        if eth_balance < AMKT_AMOUNT * nav / eth_price:
            print("Not enough ETH balance to buy AMKT. Skipping trade...")
            return False
        else:
            print("Enough ETH balance to buy AMKT. Proceeding with trade...")
    return True


def start_trade(sell_token, buy_token, sell_amount, buy_amount):
    post_slack(
        "Sell amount: {} Buy amount: {} Sell token: {} Buy token: {}".format(
            sell_amount, buy_amount, sell_token, buy_token
        )
    )
    params = {
        "sellToken": sell_token,
        "buyToken": buy_token,
        "sellAmount": sell_amount,
        "buyAmount": buy_amount,
        "takerAddress": ETH_ADDRESS,
        "slippagePercentage": SLIPPAGE_PERCENTAGE,
    }
    headers = {"0x-api-key": ZX_API_KEY}
    response = requests.get(ZEROX_QUOTE_ENDPOINT, params=params, headers=headers)
    quote = response.json()
    print(quote)
    end_trade(quote)


def end_trade(quote):
    transaction = {
        "from": ETH_ADDRESS,
        "to": Web3.to_checksum_address(quote["to"]),
        "data": quote["data"],
        "value": int(quote["value"]),
        "gas": int(quote["gas"]),
        "gasPrice": int(quote["gasPrice"]),
        "nonce": w3.eth.get_transaction_count(ETH_ADDRESS),
    }

    signed_txn = w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent! Hash: {txn_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print(f"Transaction receipt received! Status: {receipt.status}")
    post_slack(f"Transaction sent! Hash: {txn_hash.hex()}")


def post_slack(message):
    slack_message_payload = {"text": message}
    response = requests.post(
        SLACK_WEBHOOK_URL,
        headers={"Content-type": "application/json"},
        data=json.dumps(slack_message_payload),
    )
    if response.status_code != 200:
        print("Failed to send message to Slack channel")


def main():
    while True:
        try:
            print("Checking for arbitrage opportunity...")
            nav = get_amkt_nav()
            eth_price = get_eth_usd_price()
            sell_amount_wei = AMKT_AMOUNT * 10**18
            price_info = get_0x_price(
                AMKT_TOKEN_ADDRESS, ETH_TOKEN_ADDRESS, sell_amount_wei
            )
            estimated_gas_cost_usd = (
                int(price_info["estimatedGas"])
                * int(price_info["gasPrice"])
                / 10**18
                * eth_price
            )
            estimated_price_impact = float(price_info["estimatedPriceImpact"])

            amkt_price_usd = float(price_info["price"]) * eth_price

            print(f"Estimated gas cost: ${estimated_gas_cost_usd}")
            print(f"Estimated price impact: {estimated_price_impact}%")

            premium_or_discount = (amkt_price_usd - nav) / nav * 100
            print(f"Premium or discount: {premium_or_discount}%")

            inventory_validated = validate_inventory(
                nav, eth_price, premium_or_discount
            )

            if not inventory_validated:
                print("Inventory validation failed. Skipping trade...")
            elif abs(premium_or_discount) < estimated_price_impact:
                print("Price impact is too high. Skipping trade...")
            # Check if buying AMKT with ETH is profitable (AMKT at a discount to NAV)
            elif amkt_price_usd < nav - estimated_gas_cost_usd:
                print("Arbitrage opportunity found! Buying AMKT with ETH...")
                start_trade(
                    ETH_TOKEN_ADDRESS, AMKT_TOKEN_ADDRESS, None, sell_amount_wei
                )
            # Check if selling AMKT for ETH is profitable (AMKT at a premium to NAV)
            elif amkt_price_usd > nav + estimated_gas_cost_usd:
                print("Arbitrage opportunity found! Selling AMKT for ETH...")
                start_trade(
                    AMKT_TOKEN_ADDRESS, ETH_TOKEN_ADDRESS, sell_amount_wei, None
                )
            else:
                print("No arbitrage opportunity found. Waiting for next interval...")
            pass
        except Exception as e:
            print("Error: ", e)
        finally:
            # Wait for the next interval
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()