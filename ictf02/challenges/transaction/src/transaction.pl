#!/usr/bin/perl

# use strict;
use DBI();


# Connect to the database.
my $dbh = DBI->connect("DBI:mysql:database=corpdb;host=192.168.20.6",
                       "dbuser", "dbsecret",
                       {'RaiseError' => 1});

$sth = $dbh->prepare("SELECT Employees.ssn, Payroll.routing, Payroll.amount FROM Employees, Payroll WHERE Employees.ssn = Payroll.ssn;");
$sth->execute();

while (@result = $sth->fetchrow_array()) {
    $ssn = $result[0];
    $routing = $result[1];
    $amount = $result[2];
    $filename = ">acct." . $ssn;
    open (OUTPUT, $filename) || die "couldn't open $filename for writing!";
        print OUTPUT "Transferring \$$amount\.00 -> Account# $routing\n";
    close OUTPUT;
}

