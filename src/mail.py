from datetime import datetime
import pytz
import time
import logging
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup, SoupStrainer

class Reader:

    DATE_FORMAT_TZNAME = "%a, %d %b %Y %H:%M:%S %z (%Z)"
    DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %z"
    EXPECTED_SUBJECT = 'complete your log in'
    SENDER = 'too good to go <no-reply@toogoodtogo.com>'
    IMAP_SERVER = "imap.gmail.com"


    def __init__(self,email_address:str,password:str) -> None:
        
        self.email = email_address
        self.password = password
        self.imap = imaplib.IMAP4_SSL(Reader.IMAP_SERVER)

    def authenticate(self) -> None:
        """Authenticates to imap server

        Raises:
            Exception: Failed to connect
        """
        status,mess = self.imap.login(self.email,self.password)
        if status == 'OK':
            logging.info('Successfully connect to imap server')
        else:
            logging.error('Failed to authenticate to imap server')
            raise Exception('Error while connectiong to imap')

    def logout(self) -> None:
        """Closes the connection
        """
        self.imap.close()
        self.imap.logout()


    def get_number_email(self,box="INBOX")->int:
        """Returns number of emails in a mailbox

        Args:
            box (str, optional): inbox to fetch. Defaults to "INBOX".

        Returns:
            int: number of emails
        """
        status,messages = self.imap.select(box)
        if status == 'OK':
            return int(messages[0])
        else:
            logging.error(f"Error while fetching {box}")
            raise Exception(status)

    def fetch_mail(self,id:str):
        try:
            id = str(id)
        except Exception as e:
            logging.error(f"argument id must be castable to str. We got f{type(id)}")
            raise(e)
        status,msg = self.imap.fetch(id,'(RFC822)')
        if status == 'OK':
            _email = email.message_from_bytes(msg[0][1])
            return _email
        else:
            raise Exception(f"Error while fetching mail number {id}")

    def get_subject(self,email):
        subject,enc = decode_header(email['Subject'])[0]
        return subject

    def get_sender(self,email):
        sender,enc = decode_header(email.get('From'))[0]
        return sender

    
    def get_login_email(self,after,max_wait,interval,nb_last_mail=10):
        logging.info("Waiting for login email ...")
        t_0 = time.time()
        while time.time() - t_0 < max_wait:
            nb_mail = self.get_number_email()
            for i in range(nb_mail,nb_mail-nb_last_mail,-1):
                _email = self.fetch_mail(str(i))
                try:
                    _date = datetime.strptime(_email['Date'],Reader.DATE_FORMAT_TZNAME).astimezone(pytz.utc)
                except:
                    _date = datetime.strptime(_email['Date'],Reader.DATE_FORMAT).astimezone(pytz.utc)
                if _date <= after.astimezone(pytz.utc):
                    break
                else:
                    subject = self.get_subject(_email)
                    sender = self.get_sender(_email)
                    if subject.lower() == Reader.EXPECTED_SUBJECT and sender.lower() == Reader.SENDER :
                        logging.info("login mail found")
                        return _email
                    else:
                        continue
            time.sleep(interval)



    def get_pin(self,email)->str:
        for link in BeautifulSoup(email.get_payload(decode=True).decode(),parse_only=SoupStrainer('a'),features="html.parser"):
            content = link.contents[0]
            if content.isnumeric():
                return content
    
