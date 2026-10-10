

from urllib.parse import urljoin
from requests import Session

import requests
import secrets
import string


import csv
from rich import print 

# I got this from an example in the CTFd documentation
# https://github.com/CTFd/ctfcli/blob/46f1e222332decff95798ba564c3f40dfbceab1c/ctfcli/utils/api.py
# see also: https://docs.ctfd.io/tutorials/api/using-ctfd-api/#:~:text=Keep%20your%20developer%20tools%20open,%2Fapi%2Fv1%2Fusers%20.
class APISession(Session):
    def __init__(self, prefix_url=None, *args, **kwargs):
        super(APISession, self).__init__(*args, **kwargs)
        # Strip out ending slashes and append a singular one so we generate
        # clean base URLs for both main deployments and subdir deployments
        self.prefix_url = prefix_url.rstrip("/") + "/"

    def request(self, method, url, *args, **kwargs):
        # Strip out the preceding / so that urljoin creates the right url
        # considering the appended / on the prefix_url
        url = urljoin(self.prefix_url, url.lstrip("/"))
        return super(APISession, self).request(method, url, *args, **kwargs)

def generate_password(length=20):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


def register_team(teams):
    url = "https://ictf24-testing.ctfd.io"
    # This token is taken from the high-challenges/.ctf/config file
    token = "d3ac8852adc89335e129bd12d3b7003336e8d1321e99333559c1e98002176a4b"

    # Create API Session
    url = url.strip("/")
    s = APISession(prefix_url=url)
    s.headers.update({"Authorization": f"Token {token}"})

    # See users.csv example template at https://docs.ctfd.io/docs/imports/csv#users

    for team in teams:
        print(f' - Registering {team.team_name}...')
        # Note that the notify parameter is being passed here so CTFd will send the 
        # user an email with their credentials after the account is created
        team_data=team.to_ctfd_dict()
        r = s.post(
            f"{url}/api/v1/users",
            json=team_data,
            headers={"Content-Type": "application/json"}
        )
        if r.status_code != 200:
            print(f'    ❌ API Response: {r.status_code}')
        else:
            print(f'    ✅')
        assert(r.status_code == 200)


class Team:
    def __init__(self, team_name, organization, team_supervisor, team_supervisor_email, team_captain_name, team_captain_email):
        self.team_name = team_name
        self.organization = organization
        self.team_supervisor = team_supervisor
        self.team_supervisor_email = team_supervisor_email
        self.team_captain_name = team_captain_name
        self.team_captain_email = team_captain_email
    
    def __str__(self):
        return f"Team Name: {self.team_name}\nOrganization: {self.organization}\nTeam Supervisor: {self.team_supervisor}\nTeam Supervisor Email: {self.team_supervisor_email}\nTeam Captain Name: {self.team_captain_name}\nTeam Captain Email: {self.team_captain_email}"


    def to_ctfd_dict(self):
        return {
            "team_name": self.team_name,
            "email": self.team_captain_email,
            "password": generate_password(),
            "affiliation": self.organization,
            "type": "user",
            "verified": True,
            "hidden": False,
            "banned": False,
            "fields": []
        }

high_schools = []
undergrads = []

# Function to read and parse the CSV file
def parse_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        data = csvfile.read().splitlines()
    for line in data:
        line = line.split('	')
        
        assert(len(line) == 101)

        level = line[10]

        team = Team(
            team_name=line[1],
            organization=line[3],
            team_supervisor = line[5],
            team_supervisor_email = line[6],
            team_captain_name=line[8],
            team_captain_email = line[9],
        )

        if 'High School' in level:
            high_schools.append(team)
        elif 'Undergraduate' in level:
            undergrads.append(team)

# Path to your CSV file
file_path = './ictf2024_registration.csv'

print(f'Parsing CSV file: {file_path}...')
# Parse the CSV file and display the output
teams = parse_csv(file_path)

#for team in high_schools:
#    print(team)
#    print("\n")

# numbers as reported by Giovanni's registration form
assert(len(high_schools) == 20)

print(f'Registering {len(high_schools)} high school teams...')
register_team(high_schools)

#print(f"\nUndergraduate Teams ({len(undergrads)}):")
#for team in undergrads:
#    print(team)
#    print("\n")

# numbers as reported by Giovanni's registration form
assert(len(undergrads) == 27)

print(f'Registering {len(high_schools)} undergrad teams...')

register_team(undergrads)
