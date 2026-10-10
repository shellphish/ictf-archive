import secrets
import string

import pandas as pd

file_path = './iCTF 2024 Registration (Responses) - Form Responses 1.csv'
data = pd.read_csv(file_path)


def generate_password(length=20):
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


high_schools = data[data['Category to participate'] == 'High School Level']
undergrads = data[data['Category to participate'] == 'Undergraduate Level']
print(f"High School Teams ({len(high_schools)}):")
print(f'Undergraduate Teams ({len(undergrads)}):')

high_school_teams_for_our_backup = []
high_school_teams_for_our_ctfd_format = []
for index, row in high_schools.iterrows():
    password = generate_password()
    high_school_teams_for_our_backup.append({
        'team_name': row['Team Name'],
        'organization': row['Organization/ School Name'],
        'team_supervisor': row["Teacher/Lecturer/Faculty Supervisor's name"],
        'team_supervisor_email': row["Teacher/Lecturer/Faculty Supervisor's email"],
        'team_captain_name': row[
            "Team Captain's Name ( The contact person to receive registration related information and is responsible to  share with whole team; should be available via email )"],
        'team_captain_email': row["Team Captain's Email Address"],
        'password': password
    })
    high_school_teams_for_our_ctfd_format.append({
        'name': row['Team Name'],
        'email': row["Team Captain's Email Address"],
        'password': password
    })

high_school_teams_for_our_backup = pd.DataFrame(high_school_teams_for_our_backup)
high_school_teams_for_our_ctfd_format = pd.DataFrame(high_school_teams_for_our_ctfd_format)
high_school_teams_for_our_backup.to_csv('high_school_teams_for_our_backup.csv', index=False)
high_school_teams_for_our_ctfd_format.to_csv('high_school_teams_for_our_ctfd_format.csv', index=False)
print(len(high_school_teams_for_our_backup))

undergrad_teams_for_our_backup = []
undergrad_teams_for_our_ctfd_format = []
for index, row in undergrads.iterrows():
    password = generate_password()
    undergrad_teams_for_our_backup.append({
        'team_name': row['Team Name'],
        'organization': row['Organization/ School Name'],
        'team_supervisor': row["Teacher/Lecturer/Faculty Supervisor's name"],
        'team_supervisor_email': row["Teacher/Lecturer/Faculty Supervisor's email"],
        'team_captain_name': row[
            "Team Captain's Name ( The contact person to receive registration related information and is responsible to  share with whole team; should be available via email )"],
        'team_captain_email': row["Team Captain's Email Address"],
        'password': password
    })
    undergrad_teams_for_our_ctfd_format.append({
        'name': row['Team Name'],
        'email': row["Team Captain's Email Address"],
        'password': password
    })

undergrad_teams_for_our_backup = pd.DataFrame(undergrad_teams_for_our_backup)
undergrad_teams_for_our_ctfd_format = pd.DataFrame(undergrad_teams_for_our_ctfd_format)
undergrad_teams_for_our_backup.to_csv('undergrad_teams_for_our_backup.csv', index=False)
undergrad_teams_for_our_ctfd_format.to_csv('undergrad_teams_for_our_ctfd_format.csv', index=False)
print(len(undergrad_teams_for_our_backup))
