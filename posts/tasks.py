from celery import shared_task
import telegram
from django.conf import settings
from .models import Post


@shared_task
def adding_task(x, y):
    return x + y


@shared_task
def send_post(post_pk):

    post = Post.objects.get(pk=post_pk)
    if not post.tg_post:
        return
    attachments = post.attachments.all()
    chat_id = post.author.tg_info.chat_id
    text = post.text

    media = []

    if len(attachments) == 1:
        image = open(settings.BASE_DIR + attachments[0].image.url, "rb")
        media.append(image)
    else:
        for a in attachments:
            image = open(settings.BASE_DIR + a.image.url, "rb")
            media.append(telegram.InputMediaPhoto(media=image))

    bot = telegram.Bot(settings.TG_BOT_TOKEN)

    if media:
        media[0].caption = text

    result = None

    if len(media) == 1:
        result = bot.send_photo(chat_id=chat_id, photo=media[0], caption=text)
    elif len(media):
        result = bot.send_media_group(media=media, chat_id=chat_id)
    else:
        result = bot.send_message(text=text, chat_id=chat_id)

    if hasattr(result, "message_id"):
        post.tg_message_id = result["message_id"]
        post.tg_message_chat_id = result["chat"]["id"]
        post.save()


@shared_task
def delete_post(chat_id, message_id):
    bot = telegram.Bot(settings.TG_BOT_TOKEN)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass


@shared_task
def edit_post(chat_id, message_id, new_text):
    bot = telegram.Bot(settings.TG_BOT_TOKEN)
    try:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=new_text)
    except:
        pass
