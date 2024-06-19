# biconomy---Data-Engineer-technical-test

# EXPLANATORY LOOM :
[![Watch the video](https://img.youtube.com/vi/T-D1KVIuvjA/maxresdefault.jpg)](https://youtu.be/T-D1KVIuvjA)

# Task description : 
https://biconomy.notion.site/Senior-Data-Engineer-Take-Home-Assignment-32678961244b400d96b237e090367d5c

# Details
Contract address : 
https://polygonscan.com/address/0x5ff137d4b0fdcd49dca30c7cf57e578a026d2789#code

Event : 
UserOperationEvent

# Setup 
- Local postgres (localhost:5432)
- Local grafana (localhost:3000)
- python3.11 
- Dependencies : see requirements.txt

# What I did:

- web3py code to retrieve historical UserOperationEvents from given contract. Contract ABI : src/entry_point_abi.json
- code uses random public RPC websocket
- retrieve block_timestamp and from_address for each event using RPC calls 
- format event data and save into local postgres - See src/create_tables.sql
- download bundler excel and store bundler addresses into postgres - See src/import_bundlers_and_paymasters.py
- create grafana visualization - See src/grafana_queries.slq for sample queries

# Improvements
 - Speed could be improved with better RPC or own hosted node. 
 - Get more events data 
 - Use threading/multiprocessing to speed things up
 - Use indexers or subgraph to retrieve data faster (didn't really look into it)




