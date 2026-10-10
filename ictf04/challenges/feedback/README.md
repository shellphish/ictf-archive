# Feedback Service (iCTF 2004)

Part of the **UN Voting System** theme of iCTF 2004.

## Description

A PHP/CGI web application at `/~feedback/cgi-bin/candidates.php` that accepts
public feedback about election candidates. The scorebot stores flags as the
`comment` field in feedback submissions.

## Endpoints

- `POST /~feedback/cgi-bin/candidates.php` — submit feedback with fields:
  `candidate`, `name`, `comment` (flag stored here)

## Protocol

HTTP. The scorebot uses a browser simulation to submit forms and later retrieve
stored flags by candidate name.

## Source

Original service extracted from the iCTF 2004 competition. See `writeup/FeedbackServiceScript.py`
for the scorebot checker that shows the exact API used.
