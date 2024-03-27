import requests
import time
import json
from web3 import Web3
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants from environment variables
YOUR_0X_API_KEY = os.getenv("ZX_API_KEY")
YOUR_PRIVATE_KEY = os.getenv("PRIVATE_KEY")
YOUR_ETH_ADDRESS = os.getenv("ETH_ADDRESS")
NETWORK = os.getenv("NETWORK")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

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

# Other constants
AMKT_NAV_ENDPOINT = "https://amkt.batterylabs.io/api/data/getAmktSummary"
COINGECKO_ETH_PRICE_ENDPOINT = (
    "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
)
CHECK_INTERVAL = 120  # Interval for checking arbitrage opportunities in seconds
AMKT_AMOUNT = 5  # Amount of AMKT to trade

# Helper functions
def get_amkt_nav():
    response = requests.get(AMKT_NAV_ENDPOINT)
    data = response.json()
    nav = data["value_required_to_back_1_amkt"]
    print(f"Fetched AMKT NAV: ${nav}")
    return nav


def get_eth_usd_price():
    response = requests.get(COINGECKO_ETH_PRICE_ENDPOINT)
    data = response.json()
    print("Fetched ETH USD Price: ${}".format(data['ethereum']['usd']))
    return data['ethereum']['usd']

def get_0x_price(sell_token, buy_token, sell_amount):
    params = {
        'sellToken': sell_token,
        'buyToken': buy_token,
        'sellAmount': sell_amount,
        'takerAddress': YOUR_ETH_ADDRESS,
    }
    headers = {'0x-api-key': YOUR_0X_API_KEY}
    response = requests.get(ZEROX_PRICE_ENDPOINT, params=params, headers=headers)
    data = response.json()
    estimated_gas = data.get('estimatedGas', 0)
    print("Fetched 0x price for {} AMKT with estimated gas: {}".format(AMKT_AMOUNT, estimated_gas))
    print(data)
    return data

def post_slack(message):
    slack_message_payload = {
        "text": message
    }
    response = requests.post(
        SLACK_WEBHOOK_URL,
        headers={"Content-type": "application/json"},
        data=json.dumps(slack_message_payload),
    )
    if response.status_code != 200:
        print("Failed to send message to Slack channel")
    
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
        "takerAddress": YOUR_ETH_ADDRESS,
        "slippagePercentage": "0.003",
    }
    headers = {'0x-api-key': YOUR_0X_API_KEY}
    response = requests.get(ZEROX_QUOTE_ENDPOINT, params=params, headers=headers)
    quote = response.json()
    print(quote)
    end_trade(quote)


def end_trade(quote):
    transaction = {
        "from": YOUR_ETH_ADDRESS,
        "to": Web3.to_checksum_address(quote["to"]),
        "data": quote["data"],
        "value": int(quote["value"]),
        "gas": int(quote["gas"]),
        "gasPrice": int(quote["gasPrice"]),
        "nonce": w3.eth.get_transaction_count(YOUR_ETH_ADDRESS),
    }

    signed_txn = w3.eth.account.sign_transaction(transaction, YOUR_PRIVATE_KEY)

    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent! Hash: {txn_hash.hex()}")

    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print(f"Transaction receipt received! Status: {receipt.status}")
    post_slack(f"Transaction sent! Hash: {txn_hash.hex()}")

def validate_inventory(nav, eth_price, premium_or_discount):
    print("Checking inventory...")
    eth_balance_wei = w3.eth.get_balance(YOUR_ETH_ADDRESS)
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
    amkt_balance_wei = amkt_contract.functions.balanceOf(YOUR_ETH_ADDRESS).call()
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