#############################################################
# @file     btc_parser.py
# @author   criticalEntropy
# @date     23.12.2022
# Hints:    https://www.blockchain.com/explorer/api/blockchain_api
#############################################################
# Import packages
import requests


class BtcAddressMonitoring:
    # Constructor
    def __init__(self, watch_address):
        self.watch_address = watch_address

        self.transaction_list = []
        self.matrix = []

    # Destructor
    def __del__(self):
        print(f"Deleting BtcAddressMonitoring object with watch_address {self.watch_address}")

    #############################################################
    # @brief    This function monitors a bitcoin address and returns 'True' in
    #           case of an unconfirmed Tx-transaction.
    #           The function returns 'False' if no btc was sent from the address.
    #           An unconfirmed transaction is cached in the memory pool.
    #           This function needs to be run periodically to monitor new unconfirmed transactions.
    #           For example, you could set up a cron job that runs the script every 5 minutes.
    #
    # @para     watch_address - Address to be monitored
    # @return   boolean - BTC sent from monitored address?
    # @author   criticalEntropy
    # @date     23.12.2022
    #############################################################
    def is_tx_transaction_from_btc_address(self):
        # Send an HTTP request to the Blockchain.info API to retrieve the list of unconfirmed transactions
        api_url = 'https://blockchain.info/unconfirmed-transactions?format=json'

        # Make sure that the API call was successful and no HTTP errors occurred
        try:
            response = requests.get(api_url)
            response.raise_for_status()
        except (requests.exceptions.RequestException, ValueError) as err:
            print(f"An error occurred while trying to retrieve the list of unconfirmed transactions: {err}")
            return False

        # Make sure that the response of the API call could be parsed correctly
        try:
            # Parse the response as a JSON dictionary
            unconfirmed_transactions = response.json()
        except ValueError as err:
            print(f"An error occurred while parsing the response as a JSON dictionary: {err}")
            return False

        # Make sure that the API response object has the expected format and that the required keys are present.
        try:
            # Iterate over each unconfirmed transaction
            for transaction in unconfirmed_transactions['txs']:
                # Check if the address to be monitored has sent bitcoin
                if transaction['inputs'][0]['prev_out']['addr'] == self.watch_address:
                    # BTC was sent
                    return True
        except (KeyError, IndexError) as err:
            print("An error occurred while parsing the API response:", err)
            return False

        # Return False if the monitored address has not sent any BTC
        return False

    #############################################################
    # @brief    This function monitors a bitcoin address and returns 'True' in
    #           case of an unconfirmed Rx-transaction.
    #           The function returns 'False' if no btc was received from the address.
    #           An unconfirmed transaction is cached in the memory pool.
    #           This function needs to be run periodically to monitor new unconfirmed transactions.
    #           For example, you could set up a cron job that runs the script every 5 minutes.
    #
    # @para     watch_address - Address to be monitored
    # @return   boolean - BTC received by monitored address?
    # @author   criticalEntropy
    # @date     23.12.2022
    #############################################################
    def is_rx_transaction_to_btc_address(self):
        # Send an HTTP request to the Blockchain.info API to retrieve the list of unconfirmed transactions
        api_url = 'https://blockchain.info/unconfirmed-transactions?format=json'

        # Make sure that the API call was successful and no HTTP errors occurred
        try:
            response = requests.get(api_url)
            response.raise_for_status()
        except (requests.exceptions.RequestException, ValueError) as err:
            print(f"An error occurred while trying to retrieve the list of unconfirmed transactions: {err}")
            return False

        # Make sure that the response of the API call could be parsed correctly.
        try:
            # Parse the response as a JSON dictionary
            unconfirmed_transactions = response.json()
        except ValueError as err:
            print(f"An error occurred while parsing the response as a JSON dictionary: {err}")
            return False

        # Make sure that the response of the API call could be parsed correctly
        try:
            # Iterate over each unconfirmed transaction
            for transaction in unconfirmed_transactions['txs']:
                for output in transaction['out']:
                    # Check if the address to be monitored has received bitcoin
                    if 'addr' in output and output['addr'] == self.watch_address:
                        # BTC received
                        return True
        except (KeyError, IndexError) as err:
            print("An error occurred while parsing the API response:", err)
            return False

        # Return False if the monitored address has not received any BTC
        return False

    #############################################################
    # @brief    This function requests the outgoing transaction of a Bitcoin address
    #           from the Blockchain.info API and stores them in a list.
    #
    # @para     watch_address - Address to be monitored
    # @return   list - A list containing the transaction information of a Bitcoin address
    #                   -> transmitter address
    #                   -> receiver address
    #                   -> transaction amount in *10^-8 btc
    # @author   criticalEntropy
    # @date     29.12.2022
    #############################################################

    def get_transactions_from_btc_address(self):
        # Set the number of data packets to 500 per page - A large number was chosen so that Api requests can be reduced
        tx_page = 500

        # Add the page parameter to the API URL
        api_url = f"https://blockchain.info/rawaddr/{self.watch_address}?limit={tx_page}"

        # Make an API request to get the transaction data for the specified address
        response = requests.get(api_url)

        # Check if the API request was successful
        if response.ok:
            # Get the transaction data from the API response
            data = response.json()

            # Check if the API response contains transaction data
            if "txs" in data:
                # Iterate over the transactions in the API response
                for tx in data["txs"]:
                    # Check if the transaction has inputs and outputs
                    if "inputs" in tx and "out" in tx:
                        # Get the address of the sender and the recipient, and the amount of the transaction
                        from_address = tx["inputs"][0]["prev_out"]["addr"] if tx["inputs"] else None
                        to_address = tx["out"][0]["addr"] if tx["out"] else None
                        amount = tx["out"][0]["value"] if tx["out"] and "value" in tx["out"][0] else None

                        # Check if all required data is present
                        if from_address and to_address and amount:
                            # Add the transaction data to the list
                            self.transaction_list.append((from_address, to_address, amount))
        else:
            # Handle the error here
            self.transaction_list = []
            pass

        # Return the list of transactions
        return self.transaction_list


class BtcBlockMonitoring:
    # Constructor
    def __init__(self, start_block, end_block):
        self.start_block = start_block
        self.end_block = end_block

        self.matrix = []

    # Destructor
    def __del__(self):
        print(f"Deleting BtcAddressMonitoring object with block {self.end_block}")

    #############################################################
    # @brief    This function checks if a bitcoin address is potentially involved in mixing bitcoin
    #
    # @para     watch_address - Address to be monitored
    # @return   list - A list containing the transaction information of a Bitcoin address
    #                   -> transmitter address
    #                   -> receiver address
    #                   -> transaction amount in *10^-8 btc
    # @author   criticalEntropy
    # @date     29.12.2022
    #############################################################

    def get_mixed_btc_transactions_from_btc_blocks(self):

        # Initialize lists to store the transaction data
        sender_addresses = []
        recipient_addresses = []
        amounts = []

        # Iterate over the block range
        for block_num in range(self.start_block, self.end_block + 1):
            # Make an API request to get the block data
            response = requests.get(f"https://blockchain.info/rawblock/{block_num}")

            # Check if the API request was successful
            if response.ok:
                # Get the block data from the API response
                block_data = response.json()

                # Iterate over the transactions in the block
                for tx in block_data["tx"]:
                    # Check if the transaction is a CoinJoin
                    if len(tx["inputs"]) > 1 and len(tx["out"]) > 1:
                        # Iterate over the inputs in the transaction
                        for input_data in tx["inputs"]:
                            # Get the sender address and amount
                            sender_address = input_data["prev_out"]["addr"]
                            amount = input_data["prev_out"]["value"]

                            # Add the sender address and amount to the lists
                            sender_addresses.append(sender_address)
                            amounts.append(amount)

                        # Iterate over the outputs in the transaction
                        for output_data in tx["out"]:
                            # Get the recipient address and amount
                            recipient_address = output_data["addr"]
                            recipient_addresses.append(recipient_address)
                            amount = output_data["value"]

        # Iterate over the sender addresses
        for i in range(len(sender_addresses)):
            # Create a list for the current transaction
            transaction = [sender_addresses[i], recipient_addresses[i], amounts[i]]

            # Add the transaction to the matrix
            self.matrix.append(transaction)

        # Return the matrix
        return self.matrix
