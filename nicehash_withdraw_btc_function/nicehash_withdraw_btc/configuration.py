import os

class Configuration:

    def __init__(self):
        self.nicehash = NiceHash()

class NiceHashWithdrawals:

    def __init__(self):
        self.address_code = os.environ.get('NICE_HASH_WITHDRAWALS_ADDR_CODE')
        self.address = os.environ.get('NICE_HASH_WITHDRAWALS_ADDR')
        # If this is specified, address_code and address are both ignored 
        # as they are used to find this value dynamically
        self.address_id = os.environ.get('NICE_HASH_WITHDRAWALS_ADDR_ID')
        self.minimum_balance = float(os.environ.get('NICE_HASH_WITHDRAWALS_MIN_BAL'))
        self.standard_transfer_amount = float(os.environ.get('NICE_HASH_WITHDRAWALS_STD_TRANSFER_AMT'))

class NiceHash:

    def __init__(self):
        self.organization_id = os.environ.get('NICE_HASH_ORG_ID')
        self.wallet_api_key = os.environ.get('NICE_HASH_WALLET_API_KEY')
        self.wallet_api_secret = os.environ.get('NICE_HASH_WALLET_API_SECRET')
        self.api_url = os.environ.get('NICE_HASH_API_URL')
        self.cryptocurrency = os.environ.get('NICE_HASH_CRYPTOCURRENCY')
        self.withdrawals = NiceHashWithdrawals()
