import json
import graphene
from graphene.types.generic import GenericScalar
from graphene.types.json import JSONString
from bigchaindb_driver import BigchainDB


class OutputType(graphene.ObjectType):
    name = 'Output'
    description ='...'

    condition = GenericScalar()
    public_keys = graphene.List(graphene.String)
    amount = graphene.String()


class InputType(graphene.ObjectType):
    name = 'Input'
    description = '...'

    owners_before = graphene.List(graphene.String)
    fulfillment = graphene.String()
    fulfills = GenericScalar()


class TransactionType(graphene.ObjectType):
    name = 'Transaction'
    description = '...'

    id = graphene.String()
    operation = graphene.String()
    version = graphene.String()
    asset = GenericScalar()
    metadata = GenericScalar()
    inputs = graphene.List(InputType)
    outputs = graphene.List(OutputType)

    @classmethod
    def from_retrieved_tx(cls, retrieved_tx):
        outputs = [OutputType(**output) for output in retrieved_tx['outputs']]
        inputs = [InputType(**input) for input in retrieved_tx['inputs']]

        return cls(
            id=retrieved_tx['id'],
            version=retrieved_tx['version'],
            inputs=inputs,
            outputs=outputs,
            asset=retrieved_tx['asset'],
            metadata=retrieved_tx['metadata'],
        )


class QueryType(graphene.ObjectType):
    name = 'Query'
    description = '...'

    transaction = graphene.Field(
        TransactionType,
        id=graphene.String()
    )

    transactions = graphene.Field(
        graphene.List(TransactionType),
        asset_id=graphene.String()
    )

    def resolve_transaction(self, args, context, info):
        bdb = BigchainDB()
        txid = args.get('id')
        retrieved_tx = bdb.transactions.retrieve(txid)
        return TransactionType.from_retrieved_tx(retrieved_tx)

    def resolve_transactions(self, args, context, info):
        bdb = BigchainDB()
        asset_id = args.get('asset_id')
        retrieved_txs = bdb.transactions.get(asset_id=asset_id)
        return [TransactionType.from_retrieved_tx(tx) for tx in retrieved_txs]


schema = graphene.Schema(
    query = QueryType
)
