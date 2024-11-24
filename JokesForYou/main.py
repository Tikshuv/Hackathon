import requests

from initialising import Initialise
import json
import random
import psycopg2


class JokesFY:
    def __init__(self):
        self.jokes = Initialise()

    @staticmethod
    def choice():  # getting user's choice
        choices = ['J', 'F', 'A', 'Q']
        while True:
            choice = input(f'''Choose the kind of entertainment that you want
    \t(J)oke\t(F)act\t(A)ny\t(Q)uit\n\t\tYour choice: ''').strip().upper()
            if choice in choices:
                break

            print('Choose only from the proposed')
        if choice != 'Q':
            while True:
                match choice:
                    case 'J':
                        choice = 'jokes'
                        break
                    case 'F':
                        choice = 'facts'
                        break
                    case 'A':
                        with open('preferences.json', 'r') as prefs:
                            chances = json.load(prefs)
                            choice = random.choices(
                                list(chances.keys()), weights=list(chances.values()), k=1)[0][0].upper()
                            # decisions = []
                            # for key, value in chances.items():
                            #     for step in range(value):
                            #         decisions.append(key)
                            # choice = random.choice(decisions)[0].upper()
        return choice

    def main(self):
        while True:
            choice = self.choice()
            """Sending the response to the slack and getting feedback"""
            if choice != 'Q':
                slack = 'https://hooks.slack.com/services/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'

                connect = psycopg2.connect(dbname=self.jokes.db_name, user=self.jokes.uname, password=self.jokes.password
                                           , host=self.jokes.host, port=self.jokes.port)
                cursor = connect.cursor()
                resp_q = f'SELECT text, rating FROM {choice}'
                cursor.execute(resp_q)
                resp = cursor.fetchall()
                texts = [text[0] for text in resp]
                weights = [text[1] for text in resp]
                resp = random.choices(texts, weights=weights, k=1)[0]
                # print(resp)
                payload = {"text": resp}
                response = requests.post(slack, json=payload)
                if response.status_code == 200:
                    print('Check your slack channel')

                    while True:  # Getting feedback upon successful message and changing rating in table
                        fb = input("Did you like it?\n(Y)es\tIt's (O)k\t(N)o\n\t\tYour choice: ").strip().upper()
                        if fb == 'Y':
                            fb = 1
                            break
                        if fb == 'O':
                            break
                        if fb == 'N':
                            fb = -1
                            break
                        print('Choose only from the suggested options')

                    if fb == 1:
                        fb_q = f'UPDATE {choice} SET rating = rating + %s WHERE text = %s AND rating < 10'
                        cursor.execute(fb_q, (fb, resp))
                    elif fb == -1:
                        fb_q = f'UPDATE {choice} SET rating = rating + %s WHERE text = %s AND rating > 1'
                        cursor.execute(fb_q, (fb, resp))
                    connect.commit()
                    cursor.close()
                    connect.close()
                else:
                    print(f"Failed to send a joke: {response.status_code}, {response.text}")
            else:
                while True:
                    choice = input('Do you wish to change your preferences?\n\t(Y)es\t(N)o\n\t\tYour choice: ')
                    if choice.upper() == 'N':
                        quit()
                    elif choice.upper() == 'Y':
                        with open('preferences.json', 'r') as prefs:
                            e_prefs = json.load(prefs)
                            for key in list(e_prefs.keys()):
                                while True:
                                    choice = input(f"Do you wish to change {key}?\n\t(Y)es\t(N)o")
                                    if choice.upper() == 'Y':
                                        while True:
                                            change = input('Please select a number between 1 and 10: ')
                                            if change.isdigit():
                                                if 1 <= int(change) <= 10:
                                                    e_prefs[key] = int(change)
                                                break
                                            print('Invalid input, try again')
                                        break
                                    if choice == 'N':
                                        break
                                    print('Invalid input, please choose only from offered options')
                        with open('preferences.json', 'w') as prefs:
                            json.dump(e_prefs, prefs, indent=4)
                        print('Preferences were updated, see you next time')
                        quit()
                    print('Choose only from Q or Y')


main = JokesFY()
main.main()
