##################################################
#
#Variables for (core.cgi) functionality
#
# must be runable from:
# require "core.cgi";
#################################################

#only allow calls from these sites
@HTTP_REFERER = ();
#@HTTP_REFERER = ('127.0.0.1','www.emogic.com','www.somewhereincanada.com');

$site_url = "http://www.somewhereincanada.com";
#example $site_url = "http://www.emogic.com";
#required in spreadtemplate_email.html so URL is included in email readings
#Use the <%site_url%> in spreadtemplate_email.html like: <%site_url%><%card2%><%cardimage%>

$path_to_script = "/home/sic/public_html/cgi/chinesefortunesticks";
#example: $path_to_script ="/home/emogic/public_html/cgi/tarot";

$path_to_input_archive = "$path_to_script/data/input_archive";

$path_to_delay_email = "$path_to_script/data/email_delay";

$path_to_email_archive = "$path_to_script/data/email_archive";

$SEND_MAIL= "SENDMAIL_PATH";
#example: $SEND_MAIL="/usr/lib/sendmail -t";

#$SMTP_SERVER="mail.yourdomain.com";
#use SMTP_SERVER if SEND_MAIL is unavailable, BUT NOT BOTH
#example: $SMTP_SERVER="mail.yourdomain.com";

$email_enabled = 0;
#set to 0 if you want to disable email tarot readings

$from = "Tarot Mailer Ver 1.0 <EMAIL_ADDRESS>";
#This will be in all Email from addresses
#example $from = "Tarot Mailer Ver 1.0 <vpelss\@emogic.com>";
#THE SLASH IS MANDITORY!

$subject = "Your Tarot Reading";
#email subject. Note: The script adds the visitors name will show at the end

#set to 1 ONLY if you wish to delay emails sent.
#If set to 0 emails are sent immediately and no cron job is required
#see delay_email_var.cgi settings
#NOTE: delay_email.cgi is to be run by a cron job. Suggested time; once an hour.
# cron job will look similar to:
# perl HTML_ROOT/cgi/tarot/delay_email.cgi >> email_delay.log
$email_delayed = 0;

#template to show when delaying emails. must be full path for script
$email_delay_template = "../../tarot/spreads/emailwillbesent.html";
#example: $email_delay_template = "../../tarot/spreads/emailwillbesent.html"