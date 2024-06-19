import pandas as pd 
import sqlalchemy
import os

from dotenv import load_dotenv
load_dotenv()

# Create DB conneciton
uri = f'postgresql://{os.environ["DB_USERNAME"]}:{os.environ["DB_PASSWORD"]}@{os.environ["DB_HOST"]}:{os.environ["DB_PORT"]}/{os.environ["DB_NAME"]}'
DB_ENGINE = sqlalchemy.create_engine(uri)

# Save bundlers & paymasters
for sheet_name in ["Bundlers", "Paymasters"]:
    df = pd.read_excel("ERC4337 Operator Registry.xlsx", sheet_name=sheet_name)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={
        "Entity Name": "entity_name",
        "Address": "address"
    })
    df = df[["address", "entity_name"]]
    df = df.dropna(subset=["address"])
    df["address"] = df["address"].str.lower()

    df.to_sql(
        sheet_name.lower(), 
        DB_ENGINE, 
        index=False, 
        if_exists="replace"
    )