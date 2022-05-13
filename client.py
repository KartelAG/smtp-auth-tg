#!/usr/bin/env python

from email import encoders
from email.mime.base import MIMEBase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from time import sleep

smtp_server = 'localhost'
smtp_port = 2525
attach_pdf = 'attach/rfc5321.pdf'
attach_html = 'attach/rfc5321.html'
attach_jpg = 'attach/cat.jpg'

sender_email = "my@email.com"
receiver_email = ["your@email.com", "MailBot@cbr.ru"]
password = '123'

message = MIMEMultipart()
#message = MIMEMultipart("alternative")
message["Subject"] = "multipart test"
message["From"] = sender_email
message["To"] = ", ".join(receiver_email)

# Create the plain-text and HTML version of your message
body_text = """\
Hi,
How are you?
Real Python has many great tutorials:
www.realpython.com"""
body_html = """\
<html>
  <body>
    <p>Hi,<br>
       How are you?<br>
       <a href="http://www.realpython.com">Real Python</a> 
       has many great tutorials.
    </p>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(body_text, "plain")
part2 = MIMEText(body_html, "html")

# Open PDF file in binary mode
with open(attach_pdf, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part3 = MIMEBase("application", "octet-stream")
    part3.set_payload(attachment.read())

# Encode file in ASCII characters to send by email    
encoders.encode_base64(part3)

# Add header as key/value pair to attachment part
part3.add_header(
    "Content-Disposition",
    f"attachment; filename= {attach_pdf.split('/')[1]}",
)

with open(attach_jpg, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part4 = MIMEBase("image", "jpeg")
    part4.set_payload(attachment.read())

# Encode file in ASCII characters to send by email    
encoders.encode_base64(part4)

# Add header as key/value pair to attachment part
part4.add_header(
    "Content-Disposition",
    f"attachment; filename= {attach_jpg.split('/')[1]}",
)


# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)
message.attach(part3)
message.attach(part4)

# Send text, html and pdf as an attachment
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.sendmail(sender_email, receiver_email, message.as_string())

# sleep(3)
# # Send text, html and pdf as an attachment with an AUTH
# with smtplib.SMTP(smtp_server, smtp_port) as server:
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, message.as_string())

plain_message = """\
Subject: Hi there

This message is sent from Python."""

# Send email here
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.sendmail(sender_email, receiver_email, plain_message)