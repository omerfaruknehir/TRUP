import smtplib, ssl
import smtpd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading
import time


class MailManager:
    def __init__(self, mail, mail_pass):
        self.mail = mail
        self.mail_pass = mail_pass
        self.queue = []
        self.wait_time = 0.5
        self.running = False
        self._thread = threading.Thread(target=self._mail_thread, daemon=True)

    def start(self):
        self.running = True
        self._thread.start()

    def stop(self):
        self.running = False

    def add_queue(self, receiver, subject, body):
        self.queue.append({"receiver": receiver, "subject": subject, "body": body})

    def _send_mail(self, mail_data):
        # mail_data: {'receiver': receiver, 'subject': subject, 'body': body}

        message = MIMEMultipart("alternative")
        message["Subject"] = mail_data["subject"]
        message["From"] = self.mail
        message["To"] = mail_data["receiver"]

        part2 = MIMEText(mail_data["body"], "html")
        
        message.attach(part2)

        with open("mails.txt", "a", encoding="utf-8") as logfile:
            logfile.write(f"""



# MAIL
    FROM: {self.mail}
      TO: {mail_data["receiver"]}
 SUBJECT: {mail_data["subject"]}
    BODY: 
{mail_data["body"]}""")

        #self.server.sendmail(self.mail, mail_data["receiver"], message.as_string())

    def _mail_thread(self):
        #context = ssl.create_default_context()
        #with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:      
        #    #server.connect("smtp.gmail.com", 587)
        #    server.ehlo()
        #    #server.starttls(context=context)
        #    server.login(self.mail, self.mail_pass)
        #    self.server = server
        while self.running:
            while not self.queue:
                time.sleep(1)
            self._send_mail(self.queue[0])
            self.queue.pop(0)
            time.sleep(self.wait_time)
        #self.server.quit()
        #self.server = None
