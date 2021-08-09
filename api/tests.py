from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User


class AuthViewsTests(TestCase):
    AUTH_URL = 'http://127.0.0.1:8000/api'

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="test@gmail.com",
            password="tester41",
        )

    @property
    def get_data_registered_user(self):
        url = f"{self.AUTH_URL}/register/"
        data = {
            "first_name": "Te",
            "last_name": "st",
            "email": "tester@gmail.com",
            "password": "tester41",
        }
        data_client = self.client.post(url, data, format="json")
        return data_client

    @property
    def test_register_user(self):
        register_user = self.get_data_registered_user
        self.assertEqual(register_user.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(User.objects.get(email="tester@gmail.com"))

    def test_login_token(self):
        url = f"{self.AUTH_URL}/login/"
        data = {
            "email": "test@gmail.com",
            "password": "tester41"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.json())
        self.assertIn('access', response.json())

    def test_refresh_token(self):
        url = f"{self.AUTH_URL}/login/"
        data = {
            "email": "test@gmail.com",
            "password": "tester41"
        }
        result = self.client.post(url, data).json()
        self.assertEqual(len(result), 2)

        access, refresh = result['access'], result['refresh']

        url_refresh = f"{self.AUTH_URL}/refresh/"
        response = self.client.post(url_refresh, data={
            "refresh": refresh
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn('access', result)
        self.assertNotEqual(access, data['access'])

    def test_register_with_role_donatur(self):
        url = f"{self.AUTH_URL}/register/"
        data = {
            "first_name": "Te",
            "last_name": "st",
            "email": "tester@gmail.com",
            "password": "tester41",
            "role": "DONATUR"
        }
        self.client.post(url, data, format="json")
        response = User.objects.filter(role="DONATUR").count()
        self.assertEqual(response, 1)

    def test_register_with_role_fundraiser(self):
        url = f"{self.AUTH_URL}/register/"
        data = {
            "first_name": "Te",
            "last_name": "st",
            "email": "tester@gmail.com",
            "password": "tester41",
            "role": "FUNDRAISER"
        }
        self.client.post(url, data, format="json")
        response = User.objects.filter(role="FUNDRAISER").count()
        self.assertEqual(response, 1)

    def test_invalid_refresh_token_and_blank_refresh_token(self):
        url = f"{self.AUTH_URL}/refresh/"
        response = self.client.post(url, data={
            "refresh": "invalid_refresh_token"
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(url, data={
            "refresh": ""
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_unregister_user(self):
        url = f"{self.AUTH_URL}/login/"
        data = {
            "email": "unregister@gmail.com",
            "password": "unregister41"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_wrong_method(self):
        url_register = f"{self.AUTH_URL}/register/"
        response = self.client.get(url_register)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        url_login = f"{self.AUTH_URL}/login/"
        response = self.client.get(url_login)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        url_refresh_token = f"{self.AUTH_URL}/refresh/"
        response = self.client.get(url_refresh_token)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)


class VerifyFundraiserViewsTests(TestCase):
    URL = 'http://127.0.0.1:8000/api/admin/fundraiser-requests/'

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_superuser(
            email="admin@admin.com", password="admin1234")

    def test_new_fundraiser_and_verify(self):
        self.client.login(email="admin@admin.com", password="admin1234")

        new_fundraiser = User.objects.create_user(
            first_name="F", last_name="Test", email="ftest@gmail.com", password="12345678", role="FUNDRAISER")
        fundraiser_list_response = self.client.get(self.URL)
        self.assertEqual(fundraiser_list_response.status_code,
                         status.HTTP_200_OK)

        data = fundraiser_list_response.json()
        self.assertLessEqual(1, len(data))

        new_fundraiser_in_data = False
        for user in data:
            if user.get("id") == new_fundraiser.id:
                new_fundraiser_in_data = True
                break

        self.assertEqual(new_fundraiser_in_data, True)

        fundraiser_verify_response = self.client.put(
            self.URL, {"id": new_fundraiser.id})

        self.assertEqual(
            fundraiser_verify_response.status_code, status.HTTP_200_OK)

        fundraiser_verified = User.objects.get(id=new_fundraiser.id)
        self.assertEqual(fundraiser_verified.verified, True)
