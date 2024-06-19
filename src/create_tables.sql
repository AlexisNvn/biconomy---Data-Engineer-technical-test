CREATE TABLE user_operation_events (
    hash TEXT,
    block_number NUMERIC,
    block_timestamp TIMESTAMP,
    from_address TEXT,
    user_op_hash TEXT,
    sender TEXT,
    paymaster TEXT,
    nonce NUMERIC,
    log_index INT,
    transaction_index INT,
    success BOOL,
    actual_gas_cost NUMERIC,
    actual_gas_used NUMERIC,
    PRIMARY KEY (hash, log_index)
);

CREATE TABLE bundlers (
    address TEXT PRIMARY KEY,
    entity_name TEXT
);

CREATE TABLE paymasters (
    address TEXT PRIMARY KEY,
    entity_name TEXT
);