import json
import graphene
from graphene.types.generic import GenericScalar
from graphene.types.json import JSONString
from bigchaindb_driver import BigchainDB


class TransactionType(graphene.ObjectType):
    name = 'Transaction'
    description = '...'

    id = graphene.String()
    operation = graphene.String()
    version = graphene.String()
    asset = GenericScalar()
    metadata = GenericScalar()
    inputs = GenericScalar()
    outputs = GenericScalar()


class QueryType(graphene.ObjectType):
    name = 'Query'
    description = '...'

    transaction = graphene.Field(
        TransactionType,
        id=graphene.String()
    )

    def resolve_transaction(self, args, context, info):
        bdb = BigchainDB()
        txid = args.get('id')
        retrieved_tx = bdb.transactions.retrieve(txid)
        return TransactionType(**retrieved_tx)


schema = graphene.Schema(
    query = QueryType
)
