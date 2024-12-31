import pandas as pd
import mysql.connector
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
user = os.getenv("USER")

# Load the dataset
file_path = f"{user}/cleaned_retail_data.csv"
df = pd.read_csv(file_path)

# Connect to the database using environment variables
connection = mysql.connector.connect(
    host="localhost", user=db_user, password=db_password, database="ecommerce"
)

cursor = connection.cursor()


# Function to insert data into Customers table
def insert_customers(df):
    customer_columns = [
        "customer_id",
        "customer_name",
        "email",
        "phone",
        "address",
        "city",
        "state",
        "zipcode",
        "country",
        "age",
        "gender",
        "income",
        "customer_segment",
    ]
    customers = df[customer_columns].drop_duplicates()

    for _, row in customers.iterrows():
        cursor.execute(
            """
            INSERT INTO customers (customer_id, customer_name, email, phone, address, city, state, zipcode, country, age, gender, income, customer_segment)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            tuple(row),
        )


# Function to insert data into Products table
def insert_products(data):
    product_columns = ["product_category", "product_brand", "product_type", "product"]
    products = data[product_columns].drop_duplicates()
    products["product_id"] = range(1, len(products) + 1)  # Create product IDs

    for _, row in products.iterrows():
        cursor.execute(
            """
            INSERT INTO products (product_category, product_brand, product_type, product)
            VALUES (%s, %s, %s, %s)
        """,
            tuple(row[:-1]),
        )  # Exclude product_id

    return products


# Function to insert data into Transactions table
def insert_transactions(data):
    transaction_columns = [
        "transaction_id",
        "customer_id",
        "transaction_date",
        "transaction_time",
        "purchase_hour",
        "time_of_day",
        "day_of_week",
        "weekend_purchase",
        "month_name",
        "transaction_year",
        "amount",
        "total_amount",
        "payment_method",
        "order_status",
    ]
    transactions = data[transaction_columns].drop_duplicates()

    for _, row in transactions.iterrows():
        cursor.execute(
            """
            INSERT INTO transactions (transaction_id, customer_id, transaction_date, transaction_time, purchase_hour, time_of_day, day_of_week, weekend_purchase, month_name, transaction_year, amount, total_amount, payment_method, order_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            tuple(row),
        )


# Function to insert data into TransactionDetails table
def insert_transaction_details(data, product_mapping):
    transaction_details_columns = [
        "transaction_id",
        "product",
        "ratings",
        "feedback",
        "shipping_method",
    ]
    transaction_details = data[transaction_details_columns]

    # Map product names to product IDs
    transaction_details = transaction_details.merge(
        product_mapping, on="product", how="left"
    )

    for _, row in transaction_details.iterrows():
        cursor.execute(
            """
            INSERT INTO transaction_details (transaction_id, product_id, ratings, feedback, shipping_method)
            VALUES (%s, %s, %s, %s, %s)
        """,
            tuple(
                row[
                    [
                        "transaction_id",
                        "product_id",
                        "ratings",
                        "feedback",
                        "shipping_method",
                    ]
                ]
            ),
        )


# Run the insertion functions
try:
    insert_customers(df)
    product_mapping = insert_products(df)
    insert_transactions(df)
    insert_transaction_details(df, product_mapping)
    connection.commit()  # Commit all changes
    print("Data insertion completed successfully.")
except Exception as e:
    connection.rollback()  # Rollback on failure
    print("Error during insertion:", str(e))
finally:
    cursor.close()
    connection.close()
