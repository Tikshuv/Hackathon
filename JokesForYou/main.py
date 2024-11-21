import psycopg2
import os
from dotenv import load_dotenv
from psycopg2 import sql
import requests
import json


class Main:
    load_dotenv(dotenv_path='config.env')
    DB_NAME = 'Entertainment'
    USER = os.getenv('DB_USERNAME')
    PASSWORD = os.getenv('DB_PASSWORD')
    HOST = os.getenv('DB_HOST')
    PORT = os.getenv('DB_PORT')

    def __init__(self):
        self.create_db()  # Create the database when the instance is initialized
        self.create_table_j()  # Create the table for jokes after the DB is created
        self.create_table_uf()  # Create the table for useless facts after DB is created

    @classmethod
    def create_db(cls):
        """Class method to create the database if it doesn't exist."""
        try:
            # Connect to server to create database
            connection = psycopg2.connect(
                user=cls.USER,
                password=cls.PASSWORD,
                host=cls.HOST,
                port=cls.PORT
            )
            connection.autocommit = True  # Allow database creation
            cursor = connection.cursor()

            # Check if the database exists
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{cls.DB_NAME}'")
            exists = cursor.fetchone()

            if not exists:
                create_db_q = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(cls.DB_NAME))
                cursor.execute(create_db_q)
                print(f"Database '{cls.DB_NAME}' created successfully.")
            else:
                print(f"Database '{cls.DB_NAME}' already exists.")
            cursor.close()
            connection.close()
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")

    @classmethod
    def create_table_j(cls):
        """Class method to create the jokes table if it doesn't exist."""
        try:
            # Connect to the database to create the table
            connection = psycopg2.connect(
                user=cls.USER,
                password=cls.PASSWORD,
                host=cls.HOST,
                port=cls.PORT,
                dbname=cls.DB_NAME
            )
            cursor = connection.cursor()

            # Check if the table exists
            cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'jokes';")
            exists = cursor.fetchone()

            if not exists:
                create_table_q = '''
                       CREATE TABLE jokes(
                           j_id SERIAL PRIMARY KEY,
                           joke TEXT NOT NULL,
                           rating SMALLINT NOT NULL DEFAULT 0
                       )
                   '''
                cursor.execute(create_table_q)
                print('Created table for jokes')

                # Now to fill the table with jokes
                jokes = set()
                while len(jokes) < 50:
                    response = requests.get(
                        'https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,'
                        'political,racist,sexist,explicit&type=single&amount=10'
                    )
                    response = response.json().get('jokes')
                    for re in response:
                        jokes.add(re.get('joke'))

                jokes_q = '''
                       INSERT INTO jokes(joke)
                       VALUES(%s)
                   '''
                for joke in jokes:
                    cursor.execute(jokes_q, (joke,))
                connection.commit()
                print("Inserted jokes into the table.")

            cursor.close()
            connection.close()

        except psycopg2.OperationalError as e:
            print(f"Error: {e}")

    @classmethod
    def create_table_uf(cls):
        """Class method to create the jokes table if it doesn't exist."""
        try:
            # Connect to the database to create the table
            connection = psycopg2.connect(
                user=cls.USER,
                password=cls.PASSWORD,
                host=cls.HOST,
                port=cls.PORT,
                dbname=cls.DB_NAME
            )
            cursor = connection.cursor()

            # Check if the table exists
            cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'facts';")
            exists = cursor.fetchone()

            if not exists:
                create_table_q = '''
                       CREATE TABLE facts(
                           f_id SERIAL PRIMARY KEY,
                           fact TEXT NOT NULL,
                           rating SMALLINT NOT NULL DEFAULT 0
                       )
                   '''
                cursor.execute(create_table_q)
                print('Created table for facts')

                # Now to fill the table with jokes
                facts = set()
                while len(facts) < 25:
                    response = requests.get(
                        'https://corporatebs-generator.sameerkumar.website/'
                    )
                    response = response.json()
                    facts.add(response.get('phrase'))

                facts_q = '''
                       INSERT INTO facts(fact)
                       VALUES(%s)
                   '''
                for fact in facts:
                    cursor.execute(facts_q, (fact,))
                connection.commit()
                print("Inserted facts into the table.")

            cursor.close()
            connection.close()

        except psycopg2.OperationalError as e:
            print(f"Error: {e}")



a = Main()
