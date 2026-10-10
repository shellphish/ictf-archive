#!/usr/bin/perl

use CGI qw(:standard);

print header;
print start_html(
	-title => "Text file viewer",
	-style   => {'src' => '../style.css'}
	);

my $szDirPathLogs="$ENV{'DOCUMENT_ROOT'}/ccn/";

my $file = param(file);
if(length($file) > 0)
{
	if($file !~ m/.*\.tx/)
	{
		print h3("TxtViewer can only open text file (with a .txt extension)");
	}
	elsif($file =~ m/txtviewer\.pl.*\|/)
	{
		print h3("TxtViewer can't launch itself!");
	}
	else
	{
		my $szLogFilePath = $file;
		$szLogFilePath =~ s/\.txt$//;
		print "<h3 align=\"center\">= Content of file \"$szLogFilePath\" =</h3>";
		print "<p class=\"text\" align=\"center\">";
		if(open(FILE, "$szDirPathLogs/$file"))
		{
			my @lines=<FILE>;
			foreach my $line (@lines)
			{
				print "$line<br />";
			}
			close(FILE);
		}
		print "</p>";
	}
}

print "<hr />";
if(opendir LOGSDIR, $szDirPathLogs)
{
	print h3("Select text file to display:");

	print "<ul>\n";

	@filelist = readdir LOGSDIR;
	closedir(LOGSDIR);
	foreach my $szFileName (@filelist)
	{
		if($szFileName =~ m/.*\.txt/)
		{
			my $szLogFilePath = $szFileName;
			$szLogFilePath =~ s/\.txt$//;
			print "<li><a href=\"./txtviewer.pl?file=$szFileName\">$szLogFilePath</a></li>\n";
		}
	}

	print "</ul>\n";
}

print "<hr />\n";
print "Text file viewer by Greg. Holfitt - gholfitt [ at ] gmail.com\n";

print end_html;


