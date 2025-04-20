import mysql.connector
import random
import string
import os
from dotenv import load_dotenv, set_key

# Load the environment variables from the .env file if it exists
load_dotenv()


# Function to generate a random string (used for client_id, client_secret, and secret_key)
def generate_random_string(length=32):
    characters = string.ascii_letters + string.digits
    return "".join(random.choice(characters) for i in range(length))


# Function to create a database if it doesn't exist
def create_database():
    db_user = os.getenv("DATABASE_USER")
    db_password = os.getenv("DATABASE_PASSWORD")
    db_host = os.getenv("DATABASE_HOST")
    db_port = os.getenv("DATABASE_PORT")

    # Connect to MySQL server
    connection = mysql.connector.connect(
        host=db_host, user=db_user, password=db_password, port=db_port
    )

    cursor = connection.cursor()

    # Create the database if it doesn't exist
    database_name = os.getenv("DATABASE_NAME")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
    print(f"Database `{database_name}` is ready.")

    cursor.close()
    connection.close()


# Function to generate client_id, client_secret, and secret_key
def generate_keys():
    client_id = generate_random_string(32)
    client_secret = generate_random_string(64)
    secret_key = generate_random_string(64)

    print(f"Generated client_id: {client_id}")
    print(f"Generated client_secret: {client_secret}")
    print(f"Generated secret_key: {secret_key}")

    return client_id, client_secret, secret_key


# Function to update the .env file with new values
def update_env(client_id, client_secret, secret_key):
    env_file = ".env"

    if not os.path.exists(env_file):
        print(f"{env_file} file does not exist. Creating a new one.")
        # Create an empty .env file if it doesn't exist
        open(env_file, "w").close()

    # Update the .env file
    set_key(env_file, "CLIENT_ID", client_id)
    set_key(env_file, "CLIENT_SECRET", client_secret)
    set_key(env_file, "SECRET_KEY", secret_key)

    print(".env file updated with the new keys.")


def main():
    print("Starting setup...")

    # Step 1: Create the database if it doesn't exist
    create_database()

    # Step 2: Generate keys (client_id, client_secret, secret_key)
    client_id, client_secret, secret_key = generate_keys()

    # Step 3: Update the .env file with the generated keys
    update_env(client_id, client_secret, secret_key)

    print("Setup completed successfully.")


if __name__ == "__main__":
    main()
