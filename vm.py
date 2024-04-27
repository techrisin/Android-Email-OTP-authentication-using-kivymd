import smtplib, ssl, random
from email.message import EmailMessage
port = 587
smtp_server = ""
username=""
password = ""
message = "Test email sent successfully."
msg = EmailMessage()
msg['Subject'] = "Test Email"
msg['From'] = ""
msg['To'] = ""
msg.set_content(message)
try:
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(username, password)
            server.send_message(msg)
    elif port == 587:
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
    else:
        print ("use 465 / 587 as port value")
        exit()
    print ("successfully sent")
except Exception as e:
    print (e)

def generateotp(glen = 4):
    gchars = '0123456789'
    gsl = ''.join(random.choice(gchars) for _ in range(glen))
    return gsl