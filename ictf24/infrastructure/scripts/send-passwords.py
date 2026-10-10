#!/usr/bin/env python3
import smtplib

import pandas as pd
import time

### DISCLAIMER: This script was written in a hurry
### and is not intended to be a good example of Python code.
### It is a quick and dirty solution to a specific problem.
### Make changes as needed

# Gmail account information (CHANGE all these values)
GMAIL_USER = 'ictf24@shellphish.net'  # must be the actual netid email
GMAIL_APP_PASS = 'WZv^l4AS'  # The app password you generated for the gmail account


# REPLY_TO = 'ldesilva@ucsb.edu'   # convenient tag for replies of this type


def send_email(team_name, student_email, mentor_email, password, url):
    # This is a very specific function that should be generalized for other uses
    sent_from = GMAIL_USER
    sent_to = [student_email, mentor_email]
    sent_to_string = ', '.join(sent_to)

    sent_subject = "iCTF-24 login information and details"
    sent_body = (f"Hello Team {team_name} \n\n"
                 f"Please login to the CTF website at {url} with \n"
                 f"username:\t{team_name}\n"
                 f"password:\t{password}\n"
                 f"iCTF24 starts on the 16th of November 2024 at 10:00 am PST(UTC-8).\n\n"
                 f"More info\n"
                 "web - https://ictf.cs.ucsb.edu/\n"
                 "discord - https://discord.gg/qNHbUbpr\n"
                 "\n"
                 "Cheers,\n"
                 "~iCTF team\n")
    # Don't indent the email text
    email_text = f"""\
From: {sent_from}
To: {student_email}
CC: {mentor_email}
Subject: {sent_subject}

{sent_body}
"""
    try:
        server = smtplib.SMTP('smtp.ionos.com', 587)
        # server.ehlo()  # send the extended hello to our server
        server.starttls()  # tell server we want to communicate with TLS encryption
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.sendmail(sent_from, sent_to, email_text)
        server.close()

        print(f'Email sent to {student_email}  and {mentor_email} successfully!')
        return True
    except Exception as exception:
        print("Error: %s!\n\n" % exception)
        return False


# with open('students_passwords.csv', mode='r') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         print(row['First Name'], row['Last Name'], row['Hacker Handle'], row['Email Address'], row['pw'])
#         # send email to student
#         student_username = row['Hacker Handle']
#         student_email = row['Email Address']
#         student_password = row['pw']
#         print(f"Sending email to {student_email}")
#         send_email(student_username, student_password, student_email)

data = pd.read_csv("/scripts/undergrad_teams_for_our_backup.csv")
for index, row in data.iterrows():
    time.sleep(5)
    team_name = row['team_name']
    team_supervisor_email = row['team_supervisor_email']
    team_captain_email = row['team_captain_email']
    password = row['password']
    send_email(team_name=team_name,
               student_email=team_captain_email,
               mentor_email=team_supervisor_email,
               password=password,
               url="https://ictf24-under.ctfd.io/")
