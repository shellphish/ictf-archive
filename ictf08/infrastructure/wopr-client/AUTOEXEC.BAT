@echo off 
SET dosdir=C:\FDOS
C:\FDOS\BIN\BANNER2 
C:\FDOS\BIN\BLACKOUT 
set PATH=%dosdir%\bin
set NLSPATH=%dosdir%\NLS 
set HELPPATH=%dosdir%\HELP
set temp=%dosdir%\temp
set tmp=%dosdir%\temp
SET BLASTER=A220 I5 D1 H5 P330
REM ShsuCDhd /QQ /F:C:\FDBOOTCD.ISO
if not "%config%"=="4" REM LH VIAUDIO
if not "%config%"=="4" REM LH VIAFMTSR
if not "%config%"=="4" rem LH FDAPM APMDOS
if "%config%"=="2" LH SHARE
if not "%config%"=="4" rem ShsuCDX /QQ /~ /D:?FDCD0002 /D:?FDCD0003 /D:?CDRCACH0
SET autofile=C:\autoexec.bat 
alias reboot=fdapm warmboot 
alias halt=fdapm poweroff 
SET CFGFILE=C:\fdconfig.sys 
echo type HELP to get support on commands and navigation
echo.
echo Welcome to FreeDOS
echo.
if not "%config%"=="4" mouse 
C:\FDOS\drivers\net\crynwr\pcntpk int=0x60 
SET WATTCP.CFG=%DOSDIR%\BIN
BLACKOUT 
MODE CO80 
c:\fdos\watcom\binw\wopr
@echo off
@reboot
