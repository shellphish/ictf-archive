       IDENTIFICATION DIVISION.
       PROGRAM-ID. AuthenticateUsers.


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

       WORKING-STORAGE SECTION.
       01 CUR_BANKNAME PIC A(20).
       01 CUR_USERNAME PIC A(10).
       01 CUR_PASSWORD PIC 9(10).
       01 CUR_AUTHLEVEL PIC 9(2) VALUE 42.
       01 TMP_AUTHLEVEL PIC 9(2) VALUE 99.
       01 TMP_PASSWORD PIC 9(10).
       01 ENC_PASSWORD PIC 9(10).

       LINKAGE SECTION.
       01 BANKNAME PIC A(20).
       01 USERNAME PIC A(10).
       01 PASSWORD PIC 9(10).
       01 AUTHLEVEL PIC 9(2).

       PROCEDURE DIVISION USING BANKNAME, USERNAME, PASSWORD, AUTHLEVEL.
       10Start.
           MOVE "BLANK" TO CUR_USERNAME
           MOVE 0012759299 TO CUR_PASSWORD
           MOVE 42 TO CUR_AUTHLEVEL
           PERFORM VerifyCredentials.
       GOBACK.

       CopyValues.
           MOVE STORED_BANKNAME TO CUR_BANKNAME.
           MOVE STORED_USERNAME TO CUR_USERNAME.
           MOVE STORED_PASSWORD TO CUR_PASSWORD.
           MOVE STORED_AUTHLEVEL TO CUR_AUTHLEVEL.

       VerifyCredentials.
           OPEN INPUT UsersFile.
           MOVE FUNCTION MOD(PASSWORD,100) TO TMP_PASSWORD
           CALL "RSA" USING 0016847419 0000000005 TMP_PASSWORD
           ENC_PASSWORD

           PERFORM UNTIL 1 = 2
                   IF USERNAME = CUR_USERNAME AND ENC_PASSWORD =
                           CUR_PASSWORD
                           ADD 0 CUR_AUTHLEVEL GIVING TMP_AUTHLEVEL
                           MOVE CUR_BANKNAME TO BANKNAME
                   END-IF
                   READ UsersFile
                           AT END NEXT SENTENCE
                           NOT AT END PERFORM CopyValues
                   END-READ
           END-PERFORM.
           CLOSE UsersFile.

           IF TMP_AUTHLEVEL = 99
                   DISPLAY "No valid, verified user matched."
           ELSE
                   MOVE TMP_AUTHLEVEL TO AUTHLEVEL
           END-IF.
