from django.conf import settings
import telegram

def send_post(post, chat_id):
    media = []

    attachments = post.attachments.all()
    if len(attachments) == 1:
        image = open(settings.BASE_DIR + attachments[0].image.url, "rb")
        media.append(image)
    else:
        for a in post.attachments.all():
            image = open(settings.BASE_DIR + a.image.url, "rb")
            media.append(telegram.InputMediaPhoto(media=image))

    bot = telegram.Bot("5468688854:AAFOZlbAjIF-bXxv_PK4qgQDBcjPTA55LcU")
    chat_id = -1001155201526;

    if media:
        media[0].caption = post.text

    if len(media) == 1:
        bot.send_photo(chat_id=chat_id, photo=media[0], caption=post.text)
    elif len(media):
        bot.send_media_group(media=media, chat_id=chat_id)
    else:
        bot.send_message(text=post.text, chat_id=chat_id)


if __name__ == '__main__':
    send_post()
