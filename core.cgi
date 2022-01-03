#!/usr/bin/perl

$version = "version11";

##################################################################
#   
#  (C) Emogic core.cgi Reader by The ScriptMan at http://www.somewhereincanada.com
#  This software is NOT FREEWARE!
#  To register it visit : http://www.emogic.com/scriptman/
#  You may not redistribute this script.
#
#######################################################################
#
# Form supplied VARIABLES

# vars
# email
# databasepath
# templatepath
# records (1,2,4)
# custom1..50

#troubleshooting try without -w

########################################################################

#get arguments from the calling form
%in = &parse_form;

eval {
        use CGI qw/:standard/;
        use CGI::Cookie;

        #load up common variables and routines. //houses &cgierr
        require $in{vars};

        };
warn $@ if $@;

if ($@) {
    print "Content-type: text/plain\n\n";
    print "Error including libraries: $@\n";
    print "Make sure they exist, permissions are set properly, and paths are set correctly.";
    exit;
}

eval { &main; };                            # Trap any fatal errors so the program hopefully
if ($@) { &cgierr("fatal error: $@"); }     # never produces that nasty 500 server error page.
exit;   # There are only two exit calls in the script, here and in in &cgierr.

sub main
{
#called from valid site?
$temp = 0; #fail
foreach $item (@HTTP_REFERER)
          {
          if ($ENV{'HTTP_REFERER'} =~ /^http:\/\/$item/) {$temp = 1}
          }
if ((@HTTP_REFERER != ()) and ($temp == 0))
     {
     print "Content-type: text/html\n\n";
     print "Bad HTTP_REFERER : $ENV{'HTTP_REFERER'}";
     print '\n\n';
     exit;
     }

#GET our tarot deck
open (DATABASE, "$in{databasepath}") || die("no database file at $in{databasepath}");
@db= <DATABASE>;
close DATABASE;

#build a hash %db_def of the field names and positions eg: #field_name => ['position']
@field_names_array  = split(/\|/,$db[0]); #this is a list of all database field names from first line of database
shift @db; #remove fields name from deck database
$field_count = @field_names_array;
foreach $field (0..($field_count - 1)) #create field hash %db_def of the field names eg: #field_name => ['position']
         {
         $fn = $field_names_array[$field];
         $fn =~ s/\n//;
         $fn =~ s/\r//;
         $db_def{$fn} = $field;
         }

@db = grep(/\w/, @db); #remove blank lines in db!!!

#load page template
open (PAGETEMPLATESOURCE, "$in{templatepath}") || die("no template file at $in{templatepath}");
$pagetemplate = join("" , <PAGETEMPLATESOURCE>);
close PAGETEMPLATESOURCE;

if ($email_delayed)
   {
   #load page template
   open (PAGETEMPLATESOURCE, "$email_delay_template") || die("no template file at $in{templatepath}");
   $delay_email_template = join("" , <PAGETEMPLATESOURCE>);
   close PAGETEMPLATESOURCE;
   }

@records = split(',' , $in{records});

# number of records in deck
$recordcount = @db;

# create a list of all available token types
#<%object1%><%fieldname%> will be replaced in template
# the $token list will then be card1 to card20 as there should be no need to have more than 20 cards layed out
@alltokentypes = ();
foreach $num (1..50)
        {
        push @alltokentypes , "<\%object$num\%>";
        }

# create a list of all possible custom token types
#used to allow users to create their own spreads
#NOTE: these are not from the db, but from $in{$customtype} so forms can feed changes to the template
#for example, passing on a user name to the template, etc....
# the $token list will then be custom1 to custom20 as there should be no need to have more than 20 custom tokens layed out
@allcustomtypes = ();
foreach $num (1..50)
        {
        push @allcustomtypes , "custom$num";
        }

#replace database tokens
$count = 0;
foreach $temp (@records) #note that each $tmpcard from the cookie is really a record number in our deck.cgi database
                {
                #we have to generate the <%object1%> tokens, etc
                $token = $alltokentypes[$count];
                $count = $count + 1;
                &replacetokens($temp , $token , $pagetemplate); #replace all occurances of the $token in the $pagetemplate
                }

#replace global variables in $pagetemplate
$pagetemplate =~ s/\<\%site_url\%\>/$site_url/g; #replace all <%site_url%> tokens
$pagetemplate =~ s/\<\%databasepath\%\>/$in{databasepath}/g; #replace all <%databasepath%> tokens
$pagetemplate =~ s/\<\%templatepath\%\>/$in{templatepath}/g; #replace all <%templatepath%> tokens

#records can be placed in the template under
$recordsjoined = join(',' , @records);
$pagetemplate =~ s/\<\%records\%\>/$recordsjoined/g; #replace all <%records%> tokens

#replace all custom types on page
foreach $customtype ( @allcustomtypes )
        {
        $pagetemplate =~ s/\<\%$customtype\%\>/$in{$customtype}/g; #replace all <%customXX%> tokens
        }

if ( &valid_address($in{'email'}) && ($email_enabled) ) #see if the forms email variable exist
        {
        $message = $pagetemplate;

        $time = time();
        $filename = "$time.txt";

        $email_package = "$in{'email'}\n$from\n$subject\n\n$message\n.\n";

        if ($email_delayed)
                {
                open (emailDelay, ">$path_to_delay_email/$filename");
                print emailDelay $email_package;
                close emailDelay;
               #later run delay_email.cgi using a cron job
                }
        else
                {
                if (($SEND_MAIL ne "") || ($SMTP_SERVER ne ""))
                       {
                       $mailresult=&sendmail($from , $from , $in{'email'}, $SMTP_SERVER, "$subject", $message);
                       if ($mailresult ne "1") {
                             print "Content-type: text/html\n\n";
                             print "MAIL NOT SENT. SMTP ERROR: $mailcodes{'$mailresult'}<br>Sendmail: $SEND_MAIL or SMTP Server: $SMTP_SERVER @mailloc\n<br><$sendmail>";
                             exit;
                             }
                       open (emailArchive, ">$path_to_email_archive/$filename");
                       print emailArchive $email_package;
                       close emailArchive;
                     }
                }
      }

#choose what to print to screen.
if ($email_delayed) {$pagetemplate = $delay_email_template};
&print_screen($pagetemplate);

#open file to archive questions
$filename = "$path_to_input_archive/input_archive.txt";
open (QARCHIVE, ">>$filename") or die ("Can't open $filename");
foreach $item (keys %in) #build up all input keys
         {
         $build = "$build , ( $item=$in{$item} )";
         }
print QARCHIVE "$build\n";

close QARCHIVE;
};

#end of main routine
#end of main routine
#end of main routine
#end of main routine
#end of main routine
#end of main routine
#end of main routine
#end of main routine
#end of main routine

sub replacetokens{
# arguments: card database record number , first half of token to replace in pagetemplate , pagetemplate passed by reference
#take the given record number, exctract all record data
#replace all possible tokens in pagetemplate
#return by reference only
my ($selected , $pick);

#get argument value (card number picked) (1 to @deck(number of deck.txt records))

$pick = $_[0];
$token = $_[1]; #use the token fed from the functions second argument
# $_[2] will be the selected $pagetemplate and modified by reference

#this is the random record chosen
$selected = $db[$pick];

#get all picked card record data out of $selected
@record  = split(/\|/,$selected);

#replace all tokens based on columns #'s named in %db_def
# %db_def is PosnName => Column #
foreach $key ( keys %db_def ) {
        $replaceme = $record[$db_def{$key}];
        $_[2] =~ s/$token\<\%$key\%\>/$replaceme/g;
        };
};

sub thereisatokeninpagetemplate
{
#take the $tokentype argument given
#see if token exists on pagetemplate.html
#if so return 1, if not return 0

my ($token);

$token = $_[0];
return ($_[1] =~ m/$token/) or 0;
};

sub print_screen
{
print "Content-type:text/html\n\n";

#print @alltokentypes;
#print @records;
print $_[0];
print "\n\n";

#scent our script
print qq|
<!--Script by the Scriptman http://www.emogic.com/scriptman/-->
|;

print "\n\n";
print "\n\n";
};

sub cgierr {
# --------------------------------------------------------
# Displays any errors and prints out FORM and ENVIRONMENT
# information. Useful for debugging.
#
    if (!$html_headers_printed) {
        print "Content-type: text/html\n\n";
        $html_headers_printed = 1;
    }
    print "<PRE>\n\nCGI ERROR\n==========================================\n";
    $_[0]      and print "Error Message       : $_[0]\n";
    $0         and print "Script Location     : $0\n";
    $]         and print "Perl Version        : $]\n";

    print "\nForm Variables\n-------------------------------------------\n";
    foreach $key (sort keys %in) {
        my $space = " " x (20 - length($key));
        print "$key$space: $in{$key}\n";
    }
=pod
    print "\nEnvironment Variables\n-------------------------------------------\n";
    foreach $env (sort keys %ENV) {
        my $space = " " x (20 - length($env));
        print "$env$space: $ENV{$env}\n";
    }
=cut
    print "\n</PRE>";
    exit -1;
}

sub parse_form {
# --------------------------------------------------------
# Parses the form input and returns a hash with all the name
# value pairs. Removes SSI and any field with "---" as a value
# (as this denotes an empty SELECT field.

        my (@pairs, %in);
        my ($buffer, $pair, $name, $value);

        if ($ENV{'REQUEST_METHOD'} eq 'GET') {
                @pairs = split(/&/, $ENV{'QUERY_STRING'});
        }
        elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
                read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
                 @pairs = split(/&/, $buffer);
        }
        else {
                &cgierr ("This script must be called from the Web\nusing either GET or POST requests\n\n");
        }
        PAIR: foreach $pair (@pairs) {
                ($name, $value) = split(/=/, $pair);

                $name =~ tr/+/ /;
                $name =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ tr/+/ /;
                $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

                $value =~ s/<!--(.|\n)*-->//g;                          # Remove SSI.
                if ($value eq "---") { next PAIR; }                  # This is used as a default choice for select lists and is ignored.
                (exists $in{$name}) ?
                        ($in{$name} .= "~~$value") :              # If we have multiple select, then we tack on
                        ($in{$name}  = $value);                                  # using the ~~ as a seperator.
        }
        return %in;
}

sub valid_address
 {
  $testmail = $_[0];
  if ($testmail =~/ /)
   { return 0; }
  if ($testmail =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ ||
  $testmail !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/)
   { return 0; }
   else { return 1; }
}

sub bad_email
{
print qq|

Content-type: text/html

<FONT SIZE="+1">
<B>
SORRY! Your request could not be processed because of an
improperly formatted e-mail address. Please use your browser's
back button to return to the form entry page.
</B>
</FONT>

|;
}

sub sendmail  {
# error codes below for those who bother to check result codes <gr>
# 1 success
# -1 $smtphost unknown
# -2 socket() failed
# -3 connect() failed
# -4 service not available
# -5 unspecified communication error
# -6 local user $to unknown on host $smtp
# -7 transmission of message failed
# -8 argument $to empty
#
#  Sample call:
#
# &sendmail($from, $reply, $to, $smtp, $subject, $message );
#
#  Note that there are several commands for cleaning up possible bad inputs - if you
#  are hard coding things from a library file, so of those are unnecesssary
#

    my ($fromaddr, $replyaddr, $to, $smtp, $subject, $message) = @_;

    $to =~ s/[ \t]+/, /g; # pack spaces and add comma
    $fromaddr =~ s/.*<([^\s]*?)>/$1/; # get from email address
    $replyaddr =~ s/.*<([^\s]*?)>/$1/; # get reply email address
    $replyaddr =~ s/^([^\s]+).*/$1/; # use first address
    $message =~ s/^\./\.\./gm; # handle . as first character
    $message =~ s/\r\n/\n/g; # handle line ending
    $message =~ s/\n/\r\n/g;
    $smtp =~ s/^\s+//g; # remove spaces around $smtp
    $smtp =~ s/\s+$//g;

    if (!$to)
    {
        return(-8);
    }

 if ($SMTP_SERVER ne "")
  {
    my($proto) = (getprotobyname('tcp'))[2];
    my($port) = (getservbyname('smtp', 'tcp'))[2];

    my($smtpaddr) = ($smtp =~
                     /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/)
        ? pack('C4',$1,$2,$3,$4)
            : (gethostbyname($smtp))[4];

    if (!defined($smtpaddr))
    {
        return(-1);
    }

    if (!socket(MAIL, AF_INET, SOCK_STREAM, $proto))
    {
        return(-2);
    }

    if (!connect(MAIL, pack('Sna4x8', AF_INET, $port, $smtpaddr)))
    {
        return(-3);
    }

    my($oldfh) = select(MAIL);
    $| = 1;
    select($oldfh);

    $_ = <MAIL>;
    if (/^[45]/)
    {
        close(MAIL);
        return(-4);
    }

    print MAIL "helo $SMTP_SERVER\r\n";
    $_ = <MAIL>;
    if (/^[45]/)
    {
        close(MAIL);
        return(-5);
    }

    print MAIL "mail from: <$fromaddr>\r\n";
    $_ = <MAIL>;
    if (/^[45]/)
    {
        close(MAIL);
        return(-5);
    }

    foreach (split(/, /, $to))
    {
        print MAIL "rcpt to: <$_>\r\n";
        $_ = <MAIL>;
        if (/^[45]/)
        {
            close(MAIL);
            return(-6);
        }
    }

    print MAIL "data\r\n";
    $_ = <MAIL>;
    if (/^[45]/)
    {
        close MAIL;
        return(-5);
    }

   }

  if ($SEND_MAIL ne "")
   {
     open (MAIL,"| $SEND_MAIL");
   }

    print MAIL "To: $to\n";
    print MAIL "From: $fromaddr\n";
    #print MAIL "Reply-to: $replyaddr\n" if $replyaddr;
    print MAIL "Subject: $subject\n";
    print MAIL qq|Content-Type: text/html; charset="iso-8859-1"
   Content-Transfer-Encoding: quoted-printable
   |
   ;
    print MAIL "\n\n";
    #print MAIL 'Mime-Version: 1.0'."\n";
    #print MAIL 'content-type:' . "text/HTML\n\n"; # <----------------- put the double \n\n here
    #print MAIL "Content-Transfer-Encoding: quoted-printable\n\n";

    print MAIL "$message";

    print MAIL "\n.\n";

 if ($SMTP_SERVER ne "")
  {
    $_ = <MAIL>;
    if (/^[45]/)
    {
        close(MAIL);
        return(-7);
    }

    print MAIL "quit\r\n";
    $_ = <MAIL>;
  }

    close(MAIL);
    return(1);
}