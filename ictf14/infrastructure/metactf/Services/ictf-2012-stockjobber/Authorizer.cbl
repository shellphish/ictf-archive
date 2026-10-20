       IDENTIFICATION DIVISION.
       PROGRAM-ID. Authorizer.


       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 AUTHED PIC 9(1) VALUE 0.
       01 T PIC S9(1).
       01 L PIC S9(1).

       LINKAGE SECTION.
       01 USERNAME PIC A(10).
       01 A PIC S9(2).
       01 R PIC 9(2).


       PROCEDURE DIVISION USING USERNAME, A, R.
       10Start.
           INSPECT USERNAME TALLYING L FOR CHARACTERS BEFORE INITIAL ' '
           IF L = 0
                   DISPLAY "INVALID USERNAME"
                   GOBACK
           END-IF

           MOVE 0 TO AUTHED.
           MOVE R TO T.

           PERFORM CheckAuth.
           IF AUTHED = 1
                   DISPLAY "Authorization granted."
                   GOBACK
           END-IF.
           PERFORM Fail.

       Fail.
           DISPLAY "UNAUTHORIZED ACTION DETECTED. ABORTING."
           STOP RUN.

       CheckAuth.
           ADD -1 TO T

           DISPLAY "CHECK " A " > " T

           EVALUATE TRUE
                   WHEN L = 7
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 5
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 8
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 2
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 9
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 1
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 6
IF A>T
        MOVE 1 TO AUTHED
END-IF
                   WHEN L = 4
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 10
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
                   WHEN L = 3
                           IF A>T
                                   MOVE 1 TO AUTHED
                           END-IF
           END-EVALUATE.
