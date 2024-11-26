import psycopg2
import json

with open('secrets.json') as f:
    db_config = json.load(f)

conn = psycopg2.connect(
    dbname=db_config['dbname'],
    user=db_config['user'],
    password=db_config['password'],
    host=db_config['host'],
    port=db_config['port']
)

cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS Tokens (
        PK SERIAL PRIMARY KEY,
        Name VARCHAR(255) NOT NULL,
        Token_address VARCHAR(255) NOT NULL UNIQUE
    )
''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        PK SERIAL PRIMARY KEY,
        Date_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        From_address VARCHAR(255) NOT NULL,
        To_address VARCHAR(255) NOT NULL,
        Transaction_hash VARCHAR(255) NOT NULL UNIQUE,
        Tokens_amount FLOAT NOT NULL,
        Dollar_price FLOAT NOT NULL
    )
''')

def add_transaction(json_data):
    columns = [
        "Date_time",
        "From_address",
        "To_address",
        "Transaction_hash",
        "Tokens_amount",
        "Dollar_price"
    ]

    values = [
        json_data["Дата время"],
        json_data["Адрес отправителя"],
        json_data["Адрес получателя"],
        json_data["Хэш транзакции"],
        json_data["Количество"],
        json_data["Цена в долларах"]
    ]

    query = f"""
        INSERT INTO Transactions ({", ".join(columns)})
        VALUES ({", ".join(["%s"] * len(columns))})
    """
    cur.execute(query, values)

    conn.commit()



conn.commit()

cur.close()
conn.close()