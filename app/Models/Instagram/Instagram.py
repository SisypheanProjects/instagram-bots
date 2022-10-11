import email
import imaplib
import re
from pathlib import Path
from typing import Dict, Union

from instagrapi import Client
from instagrapi.mixins.challenge import ChallengeChoice


class InstaGraphAPI:

    __client: Client
    __challenge_email: str
    __challenge_pass: str

    def __init__(self, username: str, password: str, challenge_email: str, challenge_pass: str):
        self.__challenge_email = challenge_email
        self.__challenge_pass = challenge_pass
        self.__client = Client()
        self.__client.challenge_code_handler = self.challenge_code_handler
        self.__client.login(username=username, password=password)

    def photo_upload(self, file_path: str, caption: str, extra_data: Union[Dict, None] = None):
        if extra_data is None:
            extra_data = {}
        self.__client.photo_upload(
            path=Path(file_path),
            caption=caption,
            extra_data=extra_data
        )

    def challenge_code_handler(self, username, choice):
        if choice == ChallengeChoice.EMAIL:
            return self.get_code_from_email(username)
        return False

    def get_code_from_email(self, username):
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(self.__challenge_email, self.__challenge_pass)
        mail.select("inbox")
        result, data = mail.search(None, "(UNSEEN)")
        assert result == "OK", "Error1 during get_code_from_email: %s" % result
        ids = data.pop().split()
        for num in reversed(ids):
            mail.store(num, "+FLAGS", "\\Seen")  # mark as read
            result, data = mail.fetch(num, "(RFC822)")
            assert result == "OK", "Error2 during get_code_from_email: %s" % result
            msg = email.message_from_string(data[0][1].decode())
            payloads = msg.get_payload()
            if not isinstance(payloads, list):
                payloads = [msg]
            code = None
            for payload in payloads:
                body = payload.get_payload(decode=True).decode()
                if "<div" not in body:
                    continue
                match = re.search(">([^>]*?({u})[^<]*?)<".format(u=username), body)
                if not match:
                    continue
                print("Match from email:", match.group(1))
                match = re.search(r">(\d{6})<", body)
                if not match:
                    print('Skip this email, "code" not found')
                    continue
                code = match.group(1)
                if code:
                    return code
        return False
