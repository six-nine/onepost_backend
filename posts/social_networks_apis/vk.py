import requests
from django.conf import settings

def get_access_code(auth_code):
    url = "https://oauth.vk.com/access_token?"

    params = {
        "client_id": settings.VK_APP_ID,
        "client_secret": settings.VK_APP_SECRET,
        "redirect_uri": settings.VK_REDIRECT_URL,
        "code": auth_code
    }

    for key, value in params.items():
        url += key + "=" + value + "&"

    url = url[:-1]

    print(url)

    response = requests.get(url)

    print(response.json())
