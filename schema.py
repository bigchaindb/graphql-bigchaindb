import json
import graphene
from graphene.types.generic import GenericScalar
from bigchaindb_driver import BigchainDB
from bigchaindb_driver.exceptions import NotFoundError


class OutputType(graphene.ObjectType):
    name = 'Output'
    description ='...'

    condition = GenericScalar()
    public_keys = graphene.List(graphene.String)
    amount = graphene.String()

    @classmethod
    def from_json(cls, output):
        return cls(**output)


class InputType(graphene.ObjectType):
    name = 'Input'
    description = '...'

    owners_before = graphene.List(graphene.String)
    fulfillment = graphene.String()
    fulfills = graphene.Field(lambda: FulfillsType)

    @classmethod
    def from_json(cls, input_):
        fulfills = FulfillsType.from_json(input_['fulfills'])
        return cls(
            owners_before=input_['owners_before'],
            fulfillment=input_['fulfillment'],
            fulfills=fulfills
        )


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
    def from_json(cls, retrieved_tx):
        outputs = [
            OutputType.from_json(output) for output in retrieved_tx['outputs']
        ]
        inputs = [
            InputType.from_json(input_) for input_ in retrieved_tx['inputs']
        ]

        return cls(
            id=retrieved_tx['id'],
            version=retrieved_tx['version'],
            inputs=inputs,
            outputs=outputs,
            operation=retrieved_tx['operation'],
            asset=retrieved_tx['asset'],
            metadata=retrieved_tx['metadata'],
        )


class FulfillsType(graphene.ObjectType):
    name = 'Fulfills'
    description = '...'

    output_index = graphene.Int()
    transaction = graphene.Field(TransactionType)

    @classmethod
    def from_json(cls, fulfills):
        bdb = BigchainDB()
        try:
            retrieved_tx = bdb.transactions.retrieve(fulfills['transaction_id'])
            return cls(
                output_index=fulfills['output_index'],
                transaction=TransactionType.from_json(retrieved_tx)
            )
        except (KeyError, TypeError, NotFoundError):
            return cls(
                output_index=None,
                transaction=None
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
        asset_id=graphene.String(),
        operation=graphene.String()
    )

    outputs = graphene.Field(
        graphene.List(FulfillsType),
        public_key=graphene.String()
    )

    def resolve_transaction(self, args, context, info):
        bdb = BigchainDB()
        txid = args.get('id')
        retrieved_tx = bdb.transactions.retrieve(txid)
        return TransactionType.from_json(retrieved_tx)

    def resolve_transactions(self, args, context, info):
        bdb = BigchainDB()
        asset_id = args.get('asset_id')
        operation = args.get('operation', None)
        retrieved_txs = bdb.transactions.get(asset_id=asset_id,
                                             operation=operation)
        return [TransactionType.from_json(tx) for tx in retrieved_txs]

    def resolve_outputs(self, args, context, info):
        bdb = BigchainDB()
        public_key = args.get('public_key')
        outputs = bdb.outputs.get(public_key)

        return [FulfillsType.from_json(output) for output in outputs]


schema = graphene.Schema(
    query = QueryType
)
