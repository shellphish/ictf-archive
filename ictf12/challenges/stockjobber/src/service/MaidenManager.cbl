       IDENTIFICATION DIVISION.
       PROGRAM-ID. MaidenManager.


       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT MaidenFile ASSIGN TO
                   "/home/stockjobber/service/USERDATA.DAT"
                   ORGANIZATION IS LINE SEQUENTIAL.


       DATA DIVISION.
       FILE SECTION.
       FD MaidenFile.
       01 STORED_DATA.
           02 STORED_BANKNAME PIC A(20).
           02 STORED_USERNAME PIC A(10).
           02 STORED_SECRET PIC A(100).
       01 W_DATA.
           02 W_BANKNAME PIC A(20).
           02 W_USERNAME PIC A(10).
           02 W_SECRET PIC A(100).

       WORKING-STORAGE SECTION.
       01 TMP_SECRET PIC A(100).
       01 LOCAL_TBL.
           02 LOCAL_DATA OCCURS 900000 TIMES.
                03 LOCAL_BANKNAME PIC A(20).
                03 LOCAL_USERNAME PIC A(10).
                03 LOCAL_SECRET PIC A(100).
       01 DATA_IDX PIC 9(6).
       01 MAX_IDX PIC 9(6).

       LINKAGE SECTION.
       01 ACTION PIC A(3).
       01 BANKNAME PIC A(20).
       01 USERNAME PIC A(10).
       01 SECRET PIC A(100).
       01 IDX PIC 9(6).

       PROCEDURE DIVISION USING ACTION, BANKNAME, USERNAME, SECRET, IDX.
       10Start.
           PERFORM ReadMaidenNames.

           EVALUATE TRUE
                   WHEN ACTION = "IDX"
                           PERFORM FindMaidenEntry
                           MOVE DATA_IDX TO IDX
                           IF IDX = MAX_IDX
                                   DISPLAY "Entry not found: " USERNAME
                           END-IF
                           DISPLAY "GOT IDX " IDX " FOR " USERNAME
                   WHEN ACTION = "GET"
                           DISPLAY IDX
                           DISPLAY "SHOWING: " LOCAL_SECRET(IDX)
                           MOVE LOCAL_SECRET(IDX) TO SECRET
                   WHEN ACTION = "SET"
                           MOVE IDX TO DATA_IDX
                           PERFORM InsertMaidenEntry
                           PERFORM WriteMaidenNames
           END-EVALUATE.
       GOBACK.

       FindMaidenEntry.
           MOVE ZEROES TO DATA_IDX
           DISPLAY "U " USERNAME
           DISPLAY "B " BANKNAME
           PERFORM UNTIL (USERNAME = LOCAL_USERNAME(DATA_IDX) AND
                   BANKNAME = LOCAL_BANKNAME(DATA_IDX)) OR
                   DATA_IDX = MAX_IDX

                   DISPLAY "DX " DATA_IDX
                   DISPLAY "LU " LOCAL_USERNAME(DATA_IDX)
                   DISPLAY "LB " LOCAL_BANKNAME(DATA_IDX)
                   ADD 1 TO DATA_IDX
           END-PERFORM.

       InsertMaidenEntry.
           MOVE BANKNAME TO LOCAL_BANKNAME(DATA_IDX)
           MOVE USERNAME TO LOCAL_USERNAME(DATA_IDX)
           MOVE SECRET TO LOCAL_SECRET(DATA_IDX)

           IF DATA_IDX = MAX_IDX
                   DISPLAY "Added new maiden name."
                   ADD 1 TO MAX_IDX
           END-IF.

       WriteMaidenNames.
           MOVE 0 TO DATA_IDX
           OPEN OUTPUT MaidenFile.
           PERFORM UNTIL DATA_IDX = MAX_IDX
                   MOVE LOCAL_USERNAME(DATA_IDX) TO W_USERNAME
                   MOVE LOCAL_BANKNAME(DATA_IDX) TO W_BANKNAME
                   MOVE LOCAL_SECRET(DATA_IDX) TO W_SECRET

                   WRITE W_DATA
                   ADD 1 TO DATA_IDX
           END-PERFORM.
           CLOSE MaidenFile.
       GOBACK.

       CopyValues.
           MOVE STORED_BANKNAME TO LOCAL_BANKNAME(DATA_IDX)
           MOVE STORED_USERNAME TO LOCAL_USERNAME(DATA_IDX)
           MOVE STORED_SECRET TO LOCAL_SECRET(DATA_IDX)

           DISPLAY "Loaded maiden name " LOCAL_SECRET(DATA_IDX)
           " for user "
           LOCAL_USERNAME(DATA_IDX)
           ADD 1 TO DATA_IDX.

       ReadMaidenNames.
           MOVE ZEROES TO DATA_IDX.

           OPEN INPUT MaidenFile.
           PERFORM UNTIL 1 = 2
                   READ MaidenFile
                           AT END NEXT SENTENCE
                           NOT AT END PERFORM CopyValues
                   END-READ
           END-PERFORM.
           CLOSE MaidenFile.

           MOVE DATA_IDX TO MAX_IDX.
