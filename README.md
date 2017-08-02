# GraphQL for BigchainDB

This is an example GraphQL api running on top of the BigchainDB python driver.

The code does not talk to the backend database directly. It just retrieves
whatever data it needs using the python driver and constructs the GraphQL
objects from the returned json.

It also provides a Flask app that provides an in browser IDE from exploring
GraphQL.

### Note

The BigchainDB driver tries to connect to BigchainDB server running on
`localhost:9984`. It you want to change this you need to edit `prepopulate.py`
and `schema.py` and pass the correct parameters to the initialization of the
BigchainDB python driver.

### Setup

1. Install the requirements:
```bash
$ pip install -r requirements.txt
```

2. Start the Flask app:
```bash
$ python app.py
```

3. Open the GraphQL in your browser by going to
   [http://localhost:5000/graphql](http://localhost:5000/graphql)

4. Make sure BigchainDB server is running

5. (Optional) Prepopulate BigchainDB with the example transactions:
```bash
$ python prepopulate.py
```

This are the transactions used in the next examples.


## Examples

After prepopulating BigchainDB with the transactions provided you can copy past
these queries into the GraphQL IDE.

- Query a transaction:
```graphql
query {
    transaction(id:"3b3fd7128580280052595b9bcda98895a851793cba77402ca4de0963be958c9e") {
        id
        operation
        asset
        # we don't care about the inputs
        # inputs

        # from the outputs we don't care about the condition so we only want
        # the amount and public keys
        outputs {
            amount
            publicKeys
        }

        # we don't care about the metadata
        # metadata
    }
}
```

- Query multiple transactions by asset id:
```graphql
query {
    transactions(assetId:"3b3fd7128580280052595b9bcda98895a851793cba77402ca4de0963be958c9e") {
        # For each transaction returned I only want the id, operation and
        # public keys in the outputs
        id
        operation
        outputs {
            publicKeys
        }
    }
}
```

- Query only transfer transactions with asset id:
```graphql
query {
    transactions(assetId:"3b3fd7128580280052595b9bcda98895a851793cba77402ca4de0963be958c9e", operation:"TRANSFER") {
        # I only want the public keys and amounts of all the outputs that this
        # transfer transaction fulfills
        inputs {
            fulfills {
                outputIndex
                # the `transaction_id` inside fulfills is resolved to the
                # actual transaction so we can query fields on the transaction
                # pointed to in this inputs
                transaction {
                    outputs {
                        amount
                        publicKeys
                    }
                }
            }
        }
    }
}
```

- Query the outputs endpoint by public key
```graphql
query {
    outputs(publicKey:"FxEfUt9ArymGeCB99dZtfCUcsKwC29c8AHZ9EPnVWcyL") {
        outputIndex
        # once again the transaction_id is resolved to the actual transaction
        transaction {
           id
           operation
           asset
        }
    }
}
```

- Query without the flask backend:

We don't actually need a flask backend to perform the graphql queries. We can
just execute the queries directly from python code
```python
from schema import schema

result = schema.execute('''
{
    outputs(publicKey:"FxEfUt9ArymGeCB99dZtfCUcsKwC29c8AHZ9EPnVWcyL") {
        outputIndex
        # once again the transaction_id is resolved to the actual transaction
        transaction {
           id
           operation
           asset
        }
    }
}
''')
result.data
```

This means that we can implement this directly on top of the javascript driver
and run entirely in the browser.
