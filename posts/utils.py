from .social_networks_apis import tg


def send_tg(post, user):
    '''
    Tries to send post to telegram channel
    '''
    has_tg = hasattr(user, "tg_info")
    chat_id = 0
    if has_tg:
        chat_id = user.tg_info.chat_id
    else:
        raise Exception("No Telegram info provided")

    tg.send_post(post, chat_id)


def send_post(post, user):
    if post.tg_post:
        send_tg(post, user)
