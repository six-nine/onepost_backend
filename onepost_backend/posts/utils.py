from django.conf import settings
import requests
from .constants import VK_BASE_API_URL


def vk_get_access_code(auth_code, id):
    if auth_code is None:
        return None

    url = "https://oauth.vk.com/access_token?"

    params = {
        "client_id": settings.VK_APP_ID,
        "client_secret": settings.VK_APP_SECRET,
        "redirect_uri": settings.VK_REDIRECT_URL + "?id=" + str(id),
        "code": auth_code
    }

    for key, value in params.items():
        url += key + "=" + value + "&"

    response = requests.get(url)
    json = response.json()

    if "groups" in json:
        token = json["groups"][0]["access_token"]
        return token
    else:
        return None


def vk_build_url(method, params):
    url = VK_BASE_API_URL + method + "?"

    for param_name, param_value in params.items():
        url += param_name + "=" + param_value + "&"

    url = url[:-1]

    return url

