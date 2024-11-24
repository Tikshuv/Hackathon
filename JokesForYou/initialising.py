import psycopg2
import os
from dotenv import load_dotenv
from psycopg2 import sql
import requests
import json


class Initialise:


    def __init__(self):
        self.configs()
        self.db_name = os.getenv("DB_NAME")
        self.uname = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')
        self.create_db()  # Create the database when the instance is initialized
        self.create_table_j()  # Create the table for jokes after the DB is created
        self.create_table_uf()  # Create the table for useless facts after DB is created(probably could refactor jokes
        # func somehow to use also for creating other tables but later, maybe
        self.preferences()

    @classmethod
    def configs(cls):
        conf_env = 'configs.env'
        if not os.path.exists(conf_env):
            host = input("Server's host: ")
            port = input("Port: ")
            s_name = input("Username: ")
            password = input("Password for the server: ")
            name = input("Desired name for database: ")
            values = {
                'DB_HOST': host,
                'DB_USERNAME': f'{s_name}',
                'DB_PASSWORD': f'{password}',
                'DB_PORT': port,
                'DB_NAME': name
            }
            with open(conf_env, 'w') as configs:
                for key, value in values.items():
                    configs.write(f"{key}={value}\n")
            os.sync()
        load_dotenv(dotenv_path='configs.env')

    def create_db(self):
        """Class method to create the database if it doesn't exist."""
        try:
            # Connect to server to create database
            connection = psycopg2.connect(
                user=self.uname,
                password=self.password,
                host=self.host,
                port=self.port
            )
            connection.autocommit = True  # Allow database creation
            cursor = connection.cursor()

            # Check if the database exists
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.db_name}'")
            exists = cursor.fetchone()

            if not exists:
                create_db_q = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.db_name))
                cursor.execute(create_db_q)
                print(f"Database '{self.db_name}' created successfully.")
            else:
                print(f"Database '{self.db_name}' already exists.")
            cursor.close()
            connection.close()
        except psycopg2.OperationalError as e:
            print(f"Error: {e}")

    def create_table_j(self):
        """Class method to create the jokes table if it doesn't exist."""
        try:
            # Connect to the database to create the table
            connection = psycopg2.connect(
                user=self.uname,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.db_name
            )
            cursor = connection.cursor()

            # Check if the table exists
            cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'jokes';")
            exists = cursor.fetchone()

            if not exists:
                create_table_q = '''
                       CREATE TABLE jokes(
                           j_id SERIAL PRIMARY KEY,
                           text TEXT NOT NULL,
                           rating SMALLINT NOT NULL DEFAULT 1
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
                       INSERT INTO jokes(text)
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

    def create_table_uf(self):
        """Class method to create the jokes table if it doesn't exist."""
        try:
            # Connect to the database to create the table
            connection = psycopg2.connect(
                user=self.uname,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.db_name
            )
            cursor = connection.cursor()

            # Check if the table exists
            cursor.execute("SELECT * FROM information_schema.tables WHERE table_name = 'facts';")
            exists = cursor.fetchone()

            if not exists:
                create_table_q = '''
                       CREATE TABLE facts(
                           f_id SERIAL PRIMARY KEY,
                           text TEXT NOT NULL,
                           rating SMALLINT NOT NULL DEFAULT 1
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
                       INSERT INTO facts(text)
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

    @classmethod
    def preferences(cls):
        """Another class method but to create json file with preferences"""
        pref_p = 'preferences.json'
        if not os.path.exists(pref_p):
            choices = {'y': 2, 'n': -2, '': 0}
            while True:
                j_c = input("Do you like jokes?(leave empty if can't decide)\n\t(Y)es\tOR\t(N)o\n\t\t\t")
                if j_c.lower() in choices.keys():
                    break
                print("Please, select only 'Y' or 'N'")
            while True:
                f_c = input("What about random facts, do you like them(leave empty if can't decide?\n\t(Y)es\t("
                            "N)o\n\t\t\t")
                if f_c.lower() in choices.keys():
                    break
                print("Please, select only 'Y' or 'N'")
            preferences = {'jokes': 5+choices[j_c], 'facts': 5+choices[f_c]}
            with open(pref_p, 'w') as pref:
                json.dump(preferences, pref, indent=4)
