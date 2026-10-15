#!/usr/bin/python

import cgi
form = cgi.FieldStorage()   # FieldStorage object to
                            # hold the form data

print 'Content-type: text/html\n\n'

print '<html><head>'
print '<title>My Page</title>'
print '</head><body>'

# check whether a field called "username" was used...
# it might be used multiple times (so sep w/ commas)
if form.has_key('username'):
    username = form["username"]
    usernames = ""
    if type(username) is type([]):
        # Multiple username fields specified
        for item in username:
            if usernames:
                # Next item -- insert comma
                usernames = usernames + "," + item.value
            else:
                # First item -- don't insert comma
                usernames = item.value
    else:
        # Single username field specified
        usernames = username.value

# just for the fun of it let's create an HTML list
# of all the fields on the calling form
field_list = '<ul>\n'
for field in form.keys():
    field_list = field_list + '<li>%s</li>\n' % field
field_list = field_list + '</ul>\n'

print "</body>"
print "</html>"

