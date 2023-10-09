import requests
from bs4 import BeautifulSoup
import configparser
import re
import os

def create_or_update_config(username, password):
    config = configparser.ConfigParser()
    config['Login'] = {'Username': username, 'Password': password}
    with open('studidb-login.conf', 'w') as configfile:
        config.write(configfile)
    print("Saved successful!")
    read_config()

def read_config():
    config = configparser.ConfigParser()
    config.read('studidb-login.conf')
    if 'Login' in config:
        username = config['Login']['Username']
        password = config['Login']['Password']
        get_and_print_grades(username, password)
    else:
        print("No username or password, please enter:")
        create_or_update_config(input("Username: "), input("Password: "))

def get_and_print_grades(username, password):
    login_url = "https://studidb.informatik.uni-kiel.de:8484/studierende/login"
    s = requests.Session()
    data = {"username": username, "password": password, "login": "Login"}
    r_login = s.post(login_url, data=data)
    session_id = re.search(r'session_id=(.+?)">', r_login.text)
    if not session_id:
        print("Username or password not matching, change and try again!")
        os.remove('studidb-login.conf')
        exit("Restart this script!")
    
    session_id = session_id.group(1)
    grades_url = f"https://studidb.informatik.uni-kiel.de:8484/studierende/leistungen?session_id={session_id}"
    
    soup = BeautifulSoup(s.get(grades_url).content.decode(), 'html.parser')
    leistungen_tabelle = soup.find('table', {'cellpadding': '2'})
    headers = ["Semester", "Modul", "Note", "ECTS", "Dozent"]
    data_rows = []
    
    for row in leistungen_tabelle.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) == 6:
            data = [col.text.strip() for col in cols]
            data_rows.append(data)
    
    column_widths = [max(len(headers[i]), max(len(row[i]) for row in data_rows)) for i in range(len(headers))]
    separator = "-" * (sum(column_widths) + len(column_widths) * 3 + 1)
    
    print(separator)
    print("| " + " | ".join(headers[i].ljust(column_widths[i]) for i in range(len(headers))) + " |")
    print(separator)
    
    for row in data_rows:
        formatted_row = "| " + " | ".join(row[i].ljust(column_widths[i]) for i in range(min(len(row), len(column_widths)))) + " |"
        print(formatted_row)
    
    print(separator)

read_config()

