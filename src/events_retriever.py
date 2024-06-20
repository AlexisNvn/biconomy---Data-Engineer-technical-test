from datetime import datetime
import pandas as pd
import sqlalchemy
import json 
import os

from web3.middleware import ExtraDataToPOAMiddleware
from web3 import Web3

# Load ENV variables
from dotenv import load_dotenv
load_dotenv()

from tqdm import tqdm

from retry import retry


TABLE_NAME = "user_operation_events"

# Used to ignore duplicates on insert
def postgres_insert_ignore_duplicate(table, conn, keys, data_iter):
    from sqlalchemy.dialects.postgresql import insert

    data = [dict(zip(keys, row)) for row in data_iter]

    insert_statement = insert(table.table).values(data).on_conflict_do_nothing(
        constraint=f"{table.table.name}_pkey",
    )
    conn.execute(insert_statement)

# Postgres connection 
uri = f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}'
DB_ENGINE = sqlalchemy.create_engine(uri)

# Polygon Web3 connector
rpc_url = 'wss://polygon.drpc.org' # Random polygon RPC websocket support eth_newFilter
web3_connector = Web3(Web3.LegacyWebSocketProvider(rpc_url))

# POA middleware
web3_connector.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Contract details
ENTRY_POINT_ADDRESS = '0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789'
ENTRY_POINT_ADDRESS = web3_connector.to_checksum_address(ENTRY_POINT_ADDRESS.lower())
with open("entry_point_abi.json", "r") as f:
    ENTRY_POINT_ABI = json.load(f)

# Create contracts
contract = web3_connector.eth.contract(address=ENTRY_POINT_ADDRESS, abi=ENTRY_POINT_ABI)

# Function to retrieve events and store them into postgres
@retry(tries=10, delay=10, backoff=2)
def fetch_and_store_events(start_block, end_block):
    # Create event filter
    event_filter = contract.events.UserOperationEvent.create_filter(from_block=Web3.to_hex(start_block), to_block=Web3.to_hex(end_block)) # incluside = left

    # Retrieve events 
    events = event_filter.get_all_entries()

    if not len(events):
        return

    # Format events
    def format_event(event):
        return {
            'hash': event.transactionHash.to_0x_hex(),
            'block_number': event.blockNumber,
            'block_timestamp': datetime.fromtimestamp(web3_connector.eth.get_block(event.blockNumber).timestamp),
            'from_address': web3_connector.eth.get_transaction_receipt(event.transactionHash)['from'].lower(),
            'log_index': event.logIndex,
            'transaction_index': event.transactionIndex,
            'user_op_hash': Web3.to_hex(event.args.userOpHash),
            'sender': event.args.sender,
            'paymaster': event.args.paymaster,
            'nonce': event.args.nonce,
            'success': event.args.success,
            'actual_gas_cost': event.args.actualGasCost,
            'actual_gas_used': event.args.actualGasUsed
        }
    formatted_events = [format_event(event) for event in tqdm(events)]

    # Send to postgres
    df = pd.DataFrame(formatted_events)
    print(df["block_timestamp"].min(), df["block_timestamp"].max())

    df.to_sql(
        TABLE_NAME, 
        DB_ENGINE, 
        index=False, 
        if_exists="append",
        method=postgres_insert_ignore_duplicate
    )

# Iterate over batch of blocks, not to overload RPC
START_BLOCK = 58250000
END_BLOCK = int(DB_ENGINE.execute(f"SELECT min(block_number) FROM {TABLE_NAME}").scalar())
BATCH_SIZE = 100

for n_batch in range((END_BLOCK - START_BLOCK) // BATCH_SIZE +1):
    start_block = END_BLOCK - BATCH_SIZE * (n_batch +1)
    end_block = END_BLOCK - BATCH_SIZE * n_batch
    print(f"Fetching events for blocks : {start_block} - {end_block}")

    fetch_and_store_events(start_block, end_block)
    