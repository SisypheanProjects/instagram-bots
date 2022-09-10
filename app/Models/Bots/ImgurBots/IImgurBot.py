from abc import ABC

from imgurpython import ImgurClient

from Models.Bots.IBot import IBot


class IImgurBot(IBot, ABC):
    pass




client_id = 'YOUR CLIENT ID'
client_secret = 'YOUR CLIENT SECRET'

client = ImgurClient(client_id, client_secret)

# Example request
items = client.gallery()
for item in items:
    print(item.link)
