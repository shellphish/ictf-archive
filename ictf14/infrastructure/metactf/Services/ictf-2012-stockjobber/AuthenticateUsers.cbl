       IDENTIFICATION DIVISION.
       PROGRAM-ID. AuthenticateUsers.


       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT UsersFile ASSIGN TO
                   "./data/USERS.DAT"
                   ORGANIZATION IS LINE SEQUENTIAL.


       DATA DIVISION.
       FILE SECTION.
       FD UsersFile.
       01 STORED_CREDENTIALS.
           02 STORED_BANKNAME PIC A(20).
           02 STORED_USERNAME PIC A(10).
           02 STORED_PASSWORD PIC 9(10).
           02 STORED_AUTHLEVEL PIC S9(2).

       WORKING-STORAGE SECTION.
       01 CUR_BANKNAME PIC A(20).
       01 CUR_USERNAME PIC A(10) VALUE "X".
       01 CUR_PASSWORD PIC 9(10) VALUE 0.
       01 CUR_AUTHLEVEL PIC 9(2) VALUE 11.
       01 TMP_AUTHLEVEL PIC 9(2) VALUE 99.
       01 ENC_PASSWORD PIC 9(10).

       LINKAGE SECTION.
       01 BANKNAME PIC A(20).
       01 USERNAME PIC A(10).
       01 PASSWORD PIC 9(10).
       01 AUTHLEVEL PIC S9(2).

       PROCEDURE DIVISION USING BANKNAME, USERNAME, PASSWORD, AUTHLEVEL.
       10Start.
           PERFORM VerifyCredentials.
       GOBACK.

       CopyValues.
           MOVE STORED_BANKNAME TO CUR_BANKNAME.
           MOVE STORED_USERNAME TO CUR_USERNAME.
           MOVE STORED_PASSWORD TO CUR_PASSWORD.
           MOVE STORED_AUTHLEVEL TO CUR_AUTHLEVEL.

       VerifyCredentials.
           OPEN INPUT UsersFile.
           CALL "RSA" USING PASSWORD ENC_PASSWORD.

           PERFORM UNTIL 1 = 2
      *            DISPLAY " " USERNAME " " CUR_USERNAME
      *            DISPLAY " " ENC_PASSWORD " " CUR_PASSWORD
                   IF USERNAME = CUR_USERNAME AND ENC_PASSWORD =
                           CUR_PASSWORD
                           MOVE CUR_AUTHLEVEL TO TMP_AUTHLEVEL
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
