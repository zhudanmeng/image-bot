from fbchat import log, Client
from fbchat.models import *
import os, random

lst = ["Hit me up good bot", "hit me up good bot", "give me another one", "Give me another one"]
folder=r"C:\Users\Peter Zhu\Desktop\SHADBot\lib\pics"


class SHADBot(Client):
    def onMessage(self, message_object, author_id, thread_id, thread_type, ts, metadata, msg, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)


        # Do something with message_object here
        msgObj = str(message_object)
        print(type(msgObj))
        print(msgObj)
        if any(s in msgObj for s in lst):
            client.sendLocalImage("C:/Users/Peter Zhu/Desktop/SHADBot/lib/pics/" +
                                  random.choice(os.listdir(folder)),
                                  thread_id=thread_id,
                                  thread_type=thread_type)
            pass


client = SHADBot('email', 'password')
client.listen()