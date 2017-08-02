import json
import time

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.exceptions import NotFoundError


if __name__ == "__main__":
    print('Loading json files...')
    with open('tx_create.json', 'r') as f:
        tx_create = json.load(f)
    with open('tx_transfer.json', 'r') as f:
        tx_transfer = json.load(f)

    print('Submitting create transaction...')
    bdb = BigchainDB()
    bdb.transactions.send(tx_create)

    tries = 0
    while tries < 3:
        try:
            if bdb.transactions.status(tx_create['id']).get('status') == 'valid':
                break
        except NotFoundError:
            tries += 1

    print('Submitting transfer transaction...')
    bdb.transactions.send(tx_transfer)

    tries = 0
    while tries < 3:
        try:
            if bdb.transactions.status(tx_create['id']).get('status') == 'valid':
                break
        except NotFoundError:
            tries += 1

    print('Done!')
