       IDENTIFICATION DIVISION.
       PROGRAM-ID. CheckBank.


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
       01 EXISTS PIC 9(1).

       PROCEDURE DIVISION USING BANKNAME, EXISTS.
       10Start.
           MOVE 0 TO EXISTS.

           OPEN INPUT UsersFile.
           READ UsersFile
                   AT END NEXT SENTENCE
           END-READ

           PERFORM UNTIL 1 = 2
                   IF BANKNAME = STORED_BANKNAME
                           MOVE 1 TO EXISTS
                   END-IF
                   READ UsersFile
                           AT END NEXT SENTENCE
                   END-READ
           END-PERFORM.
           CLOSE UsersFile.
