# Sender and Recipient Info
$MailFrom = "sender@senderdomain.com"
$MailTo = "recipient@recipientdomain.com"

# Sender Credentials
$Username = "SomeUsername"
$Password = "SomePassword"

# Server Info
$SmtpServer = "localhost"
$SmtpPort = "2525"

# Message stuff
$Encoding = [System.Text.Encoding]::UTF8

$MessageSubject = "Live your best life now" 
$Message = New-Object System.Net.Mail.MailMessage $MailFrom,$MailTo
$Message.Subject = $MessageSubject
$Message.IsBodyHTML = $true
$Message.Body = '<b>this is bold text!</b>'
$Message.BodyEncoding = $Encoding 
$Message.SubjectEncoding = $Encoding

$Attachment = New-Object Net.Mail.Attachment('H:\Fun\Python\smtp-tg-noauth\attach.txt')
$Message.Attachments.Add($Attachment)

# Construct the SMTP client object, credentials, and send
$Smtp = New-Object Net.Mail.SmtpClient($SmtpServer,$SmtpPort)
#$Smtp.EnableSsl = $true
$Smtp.Credentials = New-Object System.Net.NetworkCredential($Username,$Password)
$Smtp.Send($Message)