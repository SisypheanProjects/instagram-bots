from abc import ABC

from Models.Bots.IBot import IBot


class IImgurBot(IBot, ABC):
    pass

from imgurpython import ImgurClient

client_id = 'YOUR CLIENT ID'
client_secret = 'YOUR CLIENT SECRET'

client = ImgurClient(client_id, client_secret)

# Example request
items = client.gallery()
for item in items:
    print(item.link)
