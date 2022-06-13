from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from .models import (
    Post
)

class AuthenticationBasedApiTestCase(APITestCase):

    def get_credentials(self, id=0):
        return {
            "username": "user" + str(id),
            "password": "passpass" + str(id)
        }

    def authenticate(self, id=0):
        self.client.post(reverse("register"), self.get_credentials(id))

        response = self.client.post(reverse("token_obtain_pair"),
                                    self.get_credentials(id))
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer" + " " + response.data['access'])


class PostApiTestCase(AuthenticationBasedApiTestCase):
    def get_sample_post(self, id=0):
        return {
            "name": "Test name" + str(id),
            "text": "Test text" + str(id),
            "attachments": [],
            "tg_post": False,
            "vk_post": False
        }

    def create_post(self, id=0):
        response = self.client.post(reverse("post_creation"),
                                    self.get_sample_post(id),
                                    format='json')
        return response


class TestPostCreate(PostApiTestCase):

    def test_unauthenticated_post_creating(self):
        response = self.create_post()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_post_creating(self):
        self.authenticate()
        old_count = Post.objects.all().count()

        response = self.create_post()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(old_count + 1, Post.objects.all().count())


class TestPostsList(PostApiTestCase):

    def test_unauthenticated_posts_getting(self):
        response = self.client.get(reverse("my_posts"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_posts_getting(self):
        self.authenticate(1)
        response = self.client.get(reverse("my_posts"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_only_my_posts_getting(self):
        self.authenticate(1)
        self.create_post(1)

        self.authenticate(2)
        self.create_post(2)

        response = self.client.get(reverse("my_posts"))

        current_user_id = response.wsgi_request.user.id
        for post in response.data:
            id = post['id']
            post = Post.objects.get(pk=id)
            post_author_id = post.author.user.id

            self.assertEqual(post_author_id, current_user_id)


class TestPostDetail(PostApiTestCase):

    def test_post_detail(self):
        self.authenticate()
        response = self.create_post(1)

        result = self.client.get(reverse("post_detail",
                                         kwargs={"pk": response.data["id"]}))

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        post = Post.objects.get(pk=response.data["id"])
        self.assertEqual(post.name, result.data["name"])

    def test_post_update(self):
        self.authenticate()
        response = self.create_post(1)

        result = self.client.patch(reverse("post_detail",
                                           kwargs={"pk": response.data["id"]}),
                                   {"name": "edited_name"})
        self.assertEqual(result.status_code, status.HTTP_200_OK)

        updated = Post.objects.get(pk=response.data["id"])
        self.assertEqual(updated.name, "edited_name")

    def test_post_delete(self):
        self.authenticate()
        response = self.create_post(1)

        result = self.client.delete(reverse("post_detail",
                                           kwargs={"pk": response.data["id"]}),)
        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Post.DoesNotExist):
            post = Post.objects.get(pk=response.data["id"])


class TestProfile(AuthenticationBasedApiTestCase):

    def test_user_profile_getting(self):
        self.authenticate()

        response = self.client.get(reverse("profile"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TestVKLinkGetting(AuthenticationBasedApiTestCase):

    def test_get_link(self):
        self.authenticate()
        data = {"group_id": 123456}
        response = self.client.post(reverse("vk_get_link"), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

