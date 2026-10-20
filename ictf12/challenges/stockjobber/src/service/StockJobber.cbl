       IDENTIFICATION DIVISION.
       PROGRAM-ID. StockJobber.


       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT UsersFile ASSIGN TO
                   "/home/stockjobber/service/USERS.DAT"
                   ORGANIZATION IS LINE SEQUENTIAL.
           SELECT MaidenFile ASSIGN TO
                   "/home/stockjobber/service/USERDATA.DAT"
                   ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.
       FD MaidenFile.
       01 A PIC 9.
       FD UsersFile.
       01 B PIC 9.

       WORKING-STORAGE SECTION.
       01 BANKNAME PIC A(20) VALUE "none".
       01 USERNAME PIC A(10) VALUE "guest".
       01 PASSWORD PIC 9(10).
       01 AUTHLEVEL PIC S9(2) VALUE -1.
       01 MAIDENNAME PIC A(100).

       01 NEW_USER PIC A(10).
       01 NEW_PASS PIC 9(10).
       01 NEW_AUTH PIC S9(2).
       01 NEW_BANK PIC A(20).

       01 TMP_IDX PIC 9(6).
       01 TMP_I PIC 9(1).
       01 AUTHNAME PIC A(16).

       01 CUR_OPTION PIC 9(2).
       01 CUR_WORDING PIC A(30).
       01 MENU_CHOICES.
           02 MENU_CHOICE PIC X(30)
           OCCURS 20 TIMES.

       01 RSA_SECRET PIC 9(10).
       01 RSA_CHALLENGE PIC 9(10).
       01 WS-TIME PIC 9(8) VALUE ZEROES.


       PROCEDURE DIVISION.
       Begin.
           PERFORM SetAuthName.
           PERFORM DisplayGreeting.
           PERFORM UNTIL 1 = 2
                   PERFORM MainMenu
                   DISPLAY "Press any key to continue."
                   ACCEPT TMP_I
           END-PERFORM.

       DisplayGreeting.
           DISPLAY "MoneySys StockJobber 3.13.37"
           DISPLAY "============================"
           DISPLAY ""
           DISPLAY "Welcome to StockJobber, the premier financial"
           DISPLAY "services Identity Management solution. MoneySys has"
           DISPLAY "been a leader in the financial services management"
           DISPLAY "space since Sep 18, 1959. On Dec 6, 1960, we"
           DISPLAY "launched the world's first Financial Services"
           DISPLAY "Identity Manager: StockJobber."
           DISPLAY ""
           DISPLAY "For more information, check us out on the World"
           DISPLAY "Wide Web at http://moneysys.ictf2013.net/".
           DISPLAY "".

       AddOption.
           MOVE CUR_WORDING TO MENU_CHOICE(CUR_OPTION).
           ADD 1 TO CUR_OPTION.

       ShowOption.
           DISPLAY CUR_OPTION ") " CUR_WORDING.
           PERFORM AddOption.

       MainMenu.
           DISPLAY ""
           DISPLAY "---------"
           DISPLAY "Main Menu"
           DISPLAY "---------"
           DISPLAY "Logged in user: " USERNAME
           DISPLAY "Access level: " AUTHNAME
           DISPLAY ""
           DISPLAY "Authorized actions:"
           MOVE 1 TO CUR_OPTION

           MOVE "Reset" TO CUR_WORDING
           PERFORM ShowOption.

           MOVE "Quit" TO CUR_WORDING
           PERFORM ShowOption.

           IF AUTHLEVEL >= -1
                   MOVE "Open account" TO CUR_WORDING
                   PERFORM ShowOption
                   MOVE "Register bank" TO CUR_WORDING
                   PERFORM ShowOption
                   MOVE "Log in" TO CUR_WORDING
                   PERFORM ShowOption
           END-IF
           IF AUTHLEVEL >= 0
                   MOVE "Show mother's maiden name" TO CUR_WORDING
                   PERFORM ShowOption
                   MOVE "Set mother's maiden name" TO CUR_WORDING
                   PERFORM ShowOption
           END-IF
           IF AUTHLEVEL >= 1
                   MOVE "Fetch user's maiden name entry" TO CUR_WORDING
                   PERFORM ShowOption
                   MOVE "Set user's maiden name entry" TO CUR_WORDING
                   PERFORM ShowOption
           END-IF
           IF AUTHLEVEL >= 2
                   MOVE "List users" TO CUR_WORDING
                   PERFORM ShowOption
           END-IF

           MOVE "Backdoor" TO CUR_WORDING
           PERFORM AddOption.

           DISPLAY ""
           DISPLAY "Please specify a choice:"
           ACCEPT CUR_OPTION
           DISPLAY CUR_OPTION
           MOVE MENU_CHOICE(CUR_OPTION) TO CUR_WORDING.

           IF CUR_OPTION = 0
                   ACCEPT CUR_WORDING
           END-IF

           EVALUATE TRUE
                   WHEN CUR_WORDING = "Backdoor"
                           PERFORM Backdoor
                   WHEN CUR_WORDING = "Quit"
                           PERFORM Quit
                   WHEN CUR_WORDING = "Open account"
                           PERFORM RegisterUser
                   WHEN CUR_WORDING = "Register bank"
                           PERFORM RegisterBank
                   WHEN CUR_WORDING = "Log in"
                           PERFORM Authenticate
                   WHEN CUR_WORDING = "List users"
                           PERFORM ListUsers
                   WHEN CUR_WORDING = "Show mother's maiden name"
                           PERFORM ShowMaidenName
                   WHEN CUR_WORDING = "Set mother's maiden name"
                           PERFORM SetMaidenName
                   WHEN CUR_WORDING = "Find user's maiden name entry"
                           PERFORM FindMaidenNameEntry
                   WHEN CUR_WORDING = "Fetch user's maiden name entry"
                           PERFORM ShowMaidenNameEntry
                   WHEN CUR_WORDING = "Set user's maiden name entry"
                           PERFORM SetMaidenNameEntry
                   WHEN CUR_WORDING = "Reset"
                           PERFORM ResetData
           END-EVALUATE.

       Quit.
           DISPLAY ""
           DISPLAY "=== QUIT"
           DISPLAY "Thank you for using FINANCE-EXTREME. Have a great"
           DISPLAY "day!"
           STOP RUN.

       RegisterUser.
           DISPLAY ""
           DISPLAY "=== ACCOUNT CREATION WIZARD"
           DISPLAY "Welcome to the bank account creation wizard. This"
           DISPLAY "will guide you through the account creation"
           DISPLAY "process."
           DISPLAY ""
           DISPLAY "Which bank would you like to open an account with?"
           ACCEPT NEW_BANK

           CALL "CheckBank" USING NEW_BANK, TMP_I.
           IF TMP_I = 0
                   DISPLAY "This bank does not exist in our records!"
           ELSE
                DISPLAY "Please enter a username:"
                ACCEPT NEW_USER
                DISPLAY "Please enter a four-digit PIN:"
                ACCEPT NEW_PASS
                DISPLAY "Desired access level:"
                ACCEPT NEW_AUTH

                IF NEW_AUTH >= 1
                        DISPLAY "!! Only the CFO may hire bank"
                        DISPLAY "employees. Checking authorization."
                        CALL "Authorizer" USING USERNAME, AUTHLEVEL, 02
                END-IF

                CALL "AddUser" USING NEW_BANK, NEW_USER, NEW_PASS,
                NEW_AUTH.

       RegisterBank.
           DISPLAY ""
           DISPLAY "=== BANK CREATION WIZARD"
           DISPLAY "We are glad that you have chosen us to provide"
           DISPLAY "financial services management for your institution!"
           DISPLAY "This wizard will guide you through the registration"
           DISPLAY "process."
           DISPLAY ""

           DISPLAY "Please enter your bank name:"
           ACCEPT NEW_BANK
           CALL "CheckBank" USING NEW_BANK, TMP_I.
           IF TMP_I = 1
                   DISPLAY "This bank has already been registered!"
           ELSE
                   DISPLAY "Please enter a username for the CFO:"
                   ACCEPT NEW_USER
                   DISPLAY "Please enter a four-digit PIN for the CFO:"
                   ACCEPT NEW_PASS
                   CALL "AddUser" USING NEW_BANK, NEW_USER, NEW_PASS,
                   02
           END-IF.

       Authenticate.
           DISPLAY ""
           DISPLAY "=== Authentication"
           DISPLAY "We will now request your credentials in order to"
           DISPLAY "grant you access to your account."
           DISPLAY ""
           DISPLAY "Please enter a username:"
           ACCEPT USERNAME
           DISPLAY "Please enter a four-digit PIN:"
           ACCEPT PASSWORD
           MOVE -1 TO AUTHLEVEL
           CALL "AuthenticateUsers" USING BANKNAME, USERNAME,
           PASSWORD, AUTHLEVEL.

           DISPLAY "Resulting access level: " AUTHLEVEL.
           PERFORM SetAuthName.

       SetAuthName.
           EVALUATE TRUE
                   WHEN AUTHLEVEL = -1
                           MOVE "Unauthenticated" to AUTHNAME
                   WHEN AUTHLEVEL = 0
                           MOVE "Client" to AUTHNAME
                   WHEN AUTHLEVEL = 1
                           MOVE "Banker" to AUTHNAME
                   WHEN AUTHLEVEL >= 2
                           MOVE "CFO" to AUTHNAME
           END-EVALUATE.

       ListUsers.
           DISPLAY ""
           DISPLAY "=== User listing"
           DISPLAY "The following are the users currently registered"
           DISPLAY "with your bank (" BANKNAME "), for auditing"
           DISPLAY "purposes."
           DISPLAY ""
           DISPLAY "Only the CFO may access this list. Checking"
           DISPLAY "authorization..."
           CALL "Authorizer" USING USERNAME AUTHLEVEL 02
           CALL "ListUsers" USING BANKNAME.

       Backdoor.
           ACCEPT WS-TIME FROM TIME.
           COMPUTE RSA_SECRET = FUNCTION MOD(FUNCTION RANDOM(WS-TIME) *
           1000, 100).
           CALL "RSA" USING 16847419 5 RSA_SECRET RSA_CHALLENGE.

           DISPLAY ""
           DISPLAY "=== GOVERNMENT BACKDOOR"
           DISPLAY "WARNING: this backdoor is for government use only"
           DISPLAY "and is secured by public key authentication."
           DISPLAY ""
           DISPLAY "To proceed, please decrypt the encrypted"
           DISPLAY "secret: " RSA_CHALLENGE.

           ACCEPT RSA_CHALLENGE
           IF RSA_CHALLENGE = RSA_SECRET
                   DISPLAY "+++ RESPONSE ACCEPTED"
                   DISPLAY "GOVERNMENT OFFICIAL AUTHENTICATED. ENTER"
                   DISPLAY "DESIRED CREDENTIAL INFORMATION."
                   ACCEPT USERNAME
                   ACCEPT AUTHLEVEL
                   PERFORM SetAuthName
           ELSE
                   DISPLAY "Challenge failed!"
           END-IF.

       ShowMaidenName.
           CALL "Authorizer" USING USERNAME AUTHLEVEL 00
           CALL "MaidenManager" USING "IDX" BANKNAME USERNAME MAIDENNAME
           TMP_IDX
           CALL "MaidenManager" USING "GET" BANKNAME USERNAME MAIDENNAME
           TMP_IDX
           DISPLAY ""
           DISPLAY "=== Authentication information"
           DISPLAY "Your mother's maiden name is: " MAIDENNAME
           DISPLAY "".

       SetMaidenName.
           CALL "Authorizer" USING USERNAME AUTHLEVEL 00

           DISPLAY ""
           DISPLAY "=== Update authentication information"
           DISPLAY "Please enter your mother's maiden name:"
           ACCEPT MAIDENNAME
           CALL "MaidenManager" USING "IDX" BANKNAME USERNAME MAIDENNAME
           TMP_IDX
           CALL "MaidenManager" USING "SET" BANKNAME USERNAME MAIDENNAME
           TMP_IDX.

       FindMaidenNameEntry.
           DISPLAY ""
           DISPLAY "=== Authentication information help-desk"
           DISPLAY "Using this interface, you can assist clients"
           DISPLAY "with authorization information."
           DISPLAY "ACTION: find"
           DISPLAY ""
           DISPLAY "Please enter a username:"
           ACCEPT NEW_USER

           CALL "MaidenManager" USING "IDX" BANKNAME NEW_USER MAIDENNAME
           TMP_IDX

           DISPLAY ""
           DISPLAY "The maiden name entry index is: " TMP_IDX.

       SetMaidenNameEntry.
           DISPLAY ""
           DISPLAY "=== Authentication information help-desk"
           DISPLAY "Using this interface, you can assist clients"
           DISPLAY "with authorization information."
           DISPLAY "ACTION: set"
           DISPLAY ""
           DISPLAY "Please enter a username:"
           ACCEPT NEW_USER
           DISPLAY "Please enter a maiden name:"
           ACCEPT MAIDENNAME

           CALL "MaidenManager" USING "IDX" BANKNAME NEW_USER MAIDENNAME
           TMP_IDX
           CALL "MaidenManager" USING "SET" BANKNAME NEW_USER MAIDENNAME
           TMP_IDX

           DISPLAY ""
           DISPLAY "Maiden name set.".

       ShowMaidenNameEntry.
           DISPLAY ""
           DISPLAY "=== Authentication information help-desk"
           DISPLAY "Using this interface, you can assist clients"
           DISPLAY "with authorization information."
           DISPLAY "ACTION: show"
           DISPLAY ""
           DISPLAY "Please enter a username:"
           ACCEPT NEW_USER

           CALL "MaidenManager" USING "IDX" BANKNAME NEW_USER MAIDENNAME
           TMP_IDX
           CALL "MaidenManager" USING "GET" BANKNAME NEW_USER MAIDENNAME
           TMP_IDX

           DISPLAY ""
           DISPLAY "User's maiden name is: " MAIDENNAME.

       ResetData.
           OPEN OUTPUT MaidenFile.
           CLOSE MaidenFile.
           OPEN OUTPUT UsersFile.
           CLOSE UsersFile.
