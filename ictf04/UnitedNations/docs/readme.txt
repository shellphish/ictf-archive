VOTER REGISTRATION

Description: 

Users can register for voting through a web form. The information is stored in
a MySQL database. Users provide last, first, World-Wide ID, email address, and
password.  Users can review and modify their personal info by providing WW-ID
and Password. 

Flags:

The flag is stored as the ID of a new registered user. To set a flag, create a
new user. To get a flag request the info for that user using the flag value.

Exploit:

Using MySQL injection it is possible to access the users' info. From the
source of the form it is possible to access the encrypted ID. By analyzing the
code of the CGI script it is possible to break the encryption.

CAST-A-VOTE

Description:

C program that allows one to cast a vote. The vote is sent encrypted by
XOR-ing it with a wired-in encryption key (a la Diebold). Only the binary is
provided.  The votes are stored in a file, encrypted. The server adds the vote
to the file and if a previous matching vote is found the previous vote is
returned to the user.

Flags:

Casting a vote sets the flag. Re-casting the vote is used to retrieve the
flag.

Exploit: 

There is a buffer overflow and a hidden debug feature that allows one to query
the database for specific matches on the first name or the last name. Using a
query of "*,*" it is possible to get all votes. Editing the binary allows one
to set the limit for the incoming buffer and to disable the debug feature.

CANDIDATES FEEDBACK

Description:

A web page allows to review the candidates' programs. It is possible to
provide feedback. A new user is created if no user with the provided name
exists. Otherwise, the comments are added to the file of the existent user.
Every time a comment is inserted the whole history of comments is returned.

Flags:

Providing a comment for a user sets the flag. Submitting a new comment reveals
the previously set flag.

Exploit:

No checks are made on usernames. Any file in the system can be read. A hidden
admin field allows one to see all candidates names.

TALK OF THE UNITED NATIONS

Description:

This service is a bulleting board system that allows voting organizers to
discuss the issues regarding voting. Users can create discussion groups and
add or remove messages (using a password).

Flags:

The flag is set by using a private message. To get the flag one has to login
with the right parameters.

Exploit:

Buffer overflows, and system/popen vulnerabilities. Possibly a brainwashing
attack (e.g., filename overflow).

PASSWORD VERIFICATION SYSTEM

Description:

Application that allows a user to check for the strength of a password.  The
user can store and review words in a personalized dictionary.  The password is
then grep-ed against the host's dict file and the personalized file.

Flags:

The flag is set adding a word to a user's dict. The flag is retrieved by
reviewing the dictionary.

Exploit:

Buffer overflows, format string vulnerabilities, add a line to any file,
system()-based vulns.

DIE-BALD ADMINISTRATION FORM

Description:

CGI program written in C. Allows one to create a new Die-Bald administrator,
to assign tasks to the administrator and to review the current list of tasks.

Flags:

Flags are set by creating a user and assigning a task. Flags are retrieved by
reviewing a user's tasks.

Exploit:

Buffer overflow, format string vulnerabilities, add a line to any file.
Also the diebald account associated with this has a password of "pianoforte".

DISCUSS IT

Description:

A program that allows a user to chat about the elections. It's a socket that
connects to an Eliza-like program. The program remembers the last topic for a
certain user.

Flags:

The flag are set by starting a conversation that has a topic the flag. The
flag is retrieved by opening a new conversation.

Exploits:

The chat application has (natively) a bunch of buffer overflows. No checks on
the username are made as well.


TO POLL OR NOT TO POLL

Description:

Form allows to submit polls to personalized by username. Also, it is possible
to compute polls by user or globally.

Flags:

A flag is set by using a specific poll id. The flag is checked by requesting the poll with that id.

Exploit:

By sending a username that matches the name of the perl file and a poll id of
pl it is possible to overwrite a file that has the poll-computing functions. By
requesting the file it is possible to execute the code.

CONTRIBUTION SERVER

Description:

Service that allow a user to make contributions to the Candidates.

Flags:

The flag is set by making a contribution. Each time a contribution is made the
whole history of contributions is shown, revealing the flag.

Exploit:

By including PHP code in the contribution it is possible to get it executed.


ELECTION SERVER BACKDOOR

Description:

Malicious users can gain direct access to the voting database through a
SSL-protected service on port 8008.  Through a simple protocol, users
can view, add, and change votes stored in the election database.

Flags:

The flag is stored as the vote of an election participant.  To set a
flag, a new vote is created.  To retrieve a flag, the vote caster is
retrieved along with the vote.

Exploit:

By sending a long flag string, a local variable is overflowed which sets
a debug variable that triggers a dump of the entire vote database, thus
revealing all flags to any client.

