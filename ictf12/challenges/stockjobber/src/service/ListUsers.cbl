       IDENTIFICATION DIVISION.
       PROGRAM-ID. ListUsers.


       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT UsersFile ASSIGN TO
                   "/home/stockjobber/service/USERS.DAT"
                   ORGANIZATION IS LINE SEQUENTIAL.


       DATA DIVISION.
       FILE SECTION.
       FD UsersFile.
       01 STORED_CREDENTIALS.
           02 STORED_BANKNAME PIC A(20).
           02 STORED_USERNAME PIC A(10).
           02 STORED_PASSWORD PIC 9(10).
           02 STORED_AUTHLEVEL PIC 9(2).

       LINKAGE SECTION.
       01 BANKNAME PIC A(20).

       PROCEDURE DIVISION USING BANKNAME.
       10Start.
           OPEN INPUT UsersFile.
           READ UsersFile
                   AT END NEXT SENTENCE
           END-READ

           PERFORM UNTIL 1 = 2
                   IF STORED_BANKNAME = BANKNAME
                           DISPLAY "User " STORED_USERNAME "(with
      - "encrypted PIN " STORED_PASSWORD ")
      - "has access " STORED_AUTHLEVEL
                   END-IF
                   READ UsersFile
                           AT END NEXT SENTENCE
                   END-READ
           END-PERFORM.
           CLOSE UsersFile.
