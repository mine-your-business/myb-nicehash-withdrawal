import json
import os

from .configuration import Configuration
from nicehash import NiceHashPrivateApi

def lambda_handler(event, context):
    """Lambda function reacting to EventBridge events

    Parameters
    ----------
    event: dict, required
        Event Bridge Scheduled Events Format

        Event doc: https://docs.aws.amazon.com/eventbridge/latest/userguide/event-types.html#schedule-event-type

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html

    """

    dry_run = os.environ.get('RUN_MODE') == 'test'
    print(f'Running in {"dry run" if dry_run else "production"} mode')

    config = Configuration()

    private_api = NiceHashPrivateApi(
        config.nicehash.api_url, 
        config.nicehash.organization_id, 
        config.nicehash.wallet_api_key, 
        config.nicehash.wallet_api_secret
    )

    btc_account = private_api.get_accounts_for_currency(config.nicehash.cryptocurrency)
    transfer_amount = 0.0
    if 'available' in btc_account:
        available_bal = float(btc_account['available'])
        if available_bal >= config.nicehash.withdrawals.minimum_balance:
            if os.environ.get('TRANSFER_TYPE') == 'all':
                transfer_amount = available_bal
            else:
                std_transfer = config.nicehash.withdrawals.standard_transfer_amount
                # Transfer the standard amount, unless that's more than we have available, then transfer all
                transfer_amount = std_transfer if std_transfer <= available_bal else available_bal
    else:
        print(f"Something changed in the API contract for {config.nicehash.cryptocurrency} - " + 
            "couldn't find 'available' balance")

    if transfer_amount > 0.0:
        print(f"Transferring {transfer_amount} {config.nicehash.cryptocurrency} to withdrawal address " + 
            f"{config.nicehash.withdrawals.address_code}")
    
    # Address ID may or may not be specified - the Address Code and Address will be used to
    # determine Address ID if not specified
    withdrawal_address_id = config.nicehash.withdrawals.address_id

    if not withdrawal_address_id:
        withdrawal_addresses = private_api.get_withdrawal_addresses(config.nicehash.cryptocurrency, 100, 0)

        if withdrawal_addresses:
            print(f"Found {len(withdrawal_addresses)} withdrawal addresses, looking for " + 
                f"{config.nicehash.withdrawals.address_code} type address for address " + 
                f"{config.nicehash.withdrawals.address}")
            if dry_run:
                print(json.dumps(withdrawal_addresses, indent=2))
            matching_withdrawal_addresses = []
            for address in withdrawal_addresses['list']:
                if (address['type']['code'] == config.nicehash.withdrawals.address_code and 
                        address['address'] == config.nicehash.withdrawals.address and 
                        address['currency'] == config.nicehash.cryptocurrency and 
                        address['status']['code'] == 'ACTIVE'):
                    matching_withdrawal_addresses.append(address['id'])
            if matching_withdrawal_addresses:
                print(f"Found {len(matching_withdrawal_addresses)} {config.nicehash.withdrawals.address_code} " + 
                    f"addresses for withdrawal address {config.nicehash.withdrawals.address} - using the first one")
                # Just use the first one
                withdrawal_address_id = matching_withdrawal_addresses[0]
                print(f"Using withdrawal address id: {withdrawal_address_id}")

    if withdrawal_address_id:
        # For debugging purposes - avoid submitting an actual withdrawal request
        if dry_run:
            withdraw_request_result = {'id': 'fake'}
        else:
            withdraw_request_result = private_api.withdraw_request(
                withdrawal_address_id, 
                transfer_amount, 
                config.nicehash.cryptocurrency
            )
        print(json.dumps(withdraw_request_result, indent=2))

    # We got here successfully!
    return True
