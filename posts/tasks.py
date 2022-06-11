from celery import shared_task
import telegram
from django.conf import settings
from .models import Post
import requests
import json
from .constants import VK_BASE_API_URL, VK_COMMON_API_PARAMS


@shared_task
def send_post_tg(post_pk):

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
def delete_post_tg(chat_id, message_id):
    bot = telegram.Bot(settings.TG_BOT_TOKEN)
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass


@shared_task
def edit_post_tg(chat_id, message_id, new_text):
    bot = telegram.Bot(settings.TG_BOT_TOKEN)
    try:
        bot.edit_message_text(chat_id=chat_id,
                              message_id=message_id,
                              text=new_text)
    except:
        pass


def build_url(method):
    return VK_BASE_API_URL + method + "?"


def get_ids(access_token):
    url = build_url("messages.getConversations")

    params = VK_COMMON_API_PARAMS
    params["access_token"] = access_token

    for param_name, param_value in params.items():
        url += param_name + '=' + param_value + '&'

    url = url[:-1]

    response = requests.get(url)
    result = json.loads(response.text)

    ids = []

    if "error" in result:
        return ids

    for obj in result["response"]["items"]:
        ids.append(obj["conversation"]["peer"]["id"])

    return ids


@shared_task
def send_message_vk(post_pk):
    post = Post.objects.get(pk=post_pk)
    if not post.vk_post:
        return

    access_token = post.author.vk_info.access_token
    text = post.text

    ids = get_ids(access_token)
    url = build_url("messages.send")
    params = VK_COMMON_API_PARAMS
    params["message"] = text
    params["random_id"] = '0'
    params["access_token"] = access_token

    peer_ids = ""

    for id in ids:
        peer_ids += str(id) + ","

    peer_ids = peer_ids[:-1]  # erase last ','
    params["peer_ids"] = peer_ids

    for param_name, param_value in params.items():
        url += param_name + "=" + param_value + "&"

    response = requests.post(url)
    print(response.text)

