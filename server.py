#!/usr/bin/env python

import asyncore
import asyncio
import os
from datetime import datetime

from pkg_resources import safe_extra
from smtp_server import SMTPServer
import email
from email.message import Message
from aiogram import Bot, types


class MySMTPServer(SMTPServer):
    
    def __init__(self, localaddr, remoteaddr, cert_file=None, key_file=None, bot_token=None, chat_id=None, relayserver=None, proxyserver=None):
        if bot_token == None or chat_id == None or chat_id == '' or bot_token == '': 
            print('[Error] Telegram bot token or chat id are empty, exiting')
            exit()            
        super().__init__(localaddr, remoteaddr, cert_file, key_file)
        self.bot = Bot(token=bot_token, proxy=proxyserver)
        self.chat_id = chat_id
        self.relayserver = relayserver
        

    async def send_text(self, some_text):
        await self.bot.send_message(chat_id=self.chat_id, text=some_text)

    async def send_group(self, some_message):
        await self.bot.send_media_group(chat_id=self.chat_id, media = some_message)

    def save_temp_file(self, attach: Message, ext: str) -> str:
        temp_filename = '_'.join((datetime.now().strftime('%Y%d%m_%H%M%S'), ext))
        temp_filepath = os.path.join('saved',temp_filename)
        open(temp_filepath, 'wb').write(attach.get_payload(decode=True))
        return temp_filepath

    def send_to_relay(self, mailfrom, rcpttos, data):
            if self.relayserver == None:
                print('no relay specified')
                exit
            import smtplib
            refused = {}
            try:
                s = smtplib.SMTP()
                s.connect(self.relayserver[0], self.relayserver[1])
                try:
                    refused = s.sendmail(mailfrom, rcpttos, data)
                finally:
                    s.quit()
                    if refused:
                        print(f'some mails were refused: {refused}')
            except:
                print('error sending to relay')

    def send_to_bot(self, msg, text = '') -> None:
        parsed_from_bytes = email.message_from_bytes(msg)
        filename_list = []
        media_group = types.MediaGroup()
        if parsed_from_bytes.is_multipart():
            for att in parsed_from_bytes.get_payload():
                ctype = att.get_content_maintype()
                cfulltype = att.get_content_type()
                if cfulltype in ('text/plain'):
                    text += att.get_payload(decode=True).decode('utf-8')
                elif cfulltype in ('text/html'):
                    filepath = self.save_temp_file(att, '.html')
                    media_group.attach_document(types.InputFile(filepath))
                    filename_list.append(filepath)
                elif ctype in ('application') or ctype in ('image'):
                    filepath = self.save_temp_file(att, att.get_filename())
                    media_group.attach_document(types.InputFile(filepath))
                    filename_list.append(filepath)
            #self.bot.send_message(chat_id=self.chat_id, text=message_text, allow_sending_without_reply=True)
            if len(media_group.media) > 0:
                media_group.media[0].caption = text
                asyncio.get_event_loop().run_until_complete(self.send_group(media_group))
            else:    
                asyncio.get_event_loop().run_until_complete(self.send_text(text))
            for filename in filename_list:
                if os.path.exists(filename):
                    os.remove(filename)
        else:
            asyncio.get_event_loop().run_until_complete(self.send_text(parsed_from_bytes.get_payload()))

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        message_text = f'From: {mailfrom}\nTo: {rcpttos}\n'
        print(rcpttos)
        other_rcpts = [i for i in rcpttos if i.lower() != 'mailbot@cbr.ru']
        if rcpttos != other_rcpts:
            self.send_to_bot(data, text=message_text)
        self.send_to_relay(mailfrom, rcpttos, data)
       

if __name__ == '__main__':
    # example
    # RELAY_SERVER = ('1.2.3.4', 25)
    RELAY_SERVER = None
    # example
    # PROXY_SERVER = 'http://5.6.7.8:3128'
    PROXY_SERVER = None
    try:
        with open('bot-token', 'r') as f:
            token = f.readline()
        with open('chat-id', 'r') as f:
            chat = f.readline()
    except:
        print('no bot token or chat id provided! exiting')
        exit()    
    MySMTPServer(
        ('0.0.0.0', 2525),
        None, 
        bot_token=token, 
        chat_id=chat,
        relayserver=RELAY_SERVER,
        proxyserver=PROXY_SERVER
    )
    asyncore.loop()