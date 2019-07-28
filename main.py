from fbchat import log, Client
from fbchat.models import *

email = input("Enter Facebook account email:")
password = input("Enter Password for that account:")
word = input("What is the trigger word?")
txtMsg = input("What do you want the bot to reply?")



class PetersonBot(Client):
    def onMessage(self, message_object, author_id, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        # Do something with message_object here
        msgObj = str(message_object)
        print(type(msgObj))
        print(msgObj)
        if word in msgObj:
            print('1')
            client.send(Message(text = txtMsg), thread_id=thread_id, thread_type=thread_type)
            pass


client = PetersonBot(email , password)
client.listen()