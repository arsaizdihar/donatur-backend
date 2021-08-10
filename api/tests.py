from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from users.models import FundraiserProposal, User


class AuthViewsTests(TestCase):
    AUTH_URL = 'http://127.0.0.1:8000/api'

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            first_name="Te",
            last_name="st",
            email="test@gmail.com",
            password="tester41",
        )

    def test_login_token(self):
        url = f"{self.AUTH_URL}/login/"
        data = {
            "first_name": "Te",
            "last_name": "st",
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
            "first_name": "Te",
            "last_name": "st",
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
            "role": "FUNDRAISER",
            "proposal_text": "test proposal text"
        }
        self.client.post(url, data, format="json")
        response = User.objects.filter(role="FUNDRAISER").count()
        self.assertEqual(response, 1)

        new_fundraiser_proposal = FundraiserProposal.objects.get(
            fundraiser__email="tester@gmail.com")
        self.assertEqual(new_fundraiser_proposal.text, "test proposal text")

    def test_register_fundraiser_no_proposal(self):
        url = f"{self.AUTH_URL}/register/"
        data = {
            "first_name": "Te",
            "last_name": "st",
            "email": "tester@gmail.com",
            "password": "tester41",
            "role": "FUNDRAISER",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
            "first_name": "Te",
            "last_name": "st",
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

    def test_me_view(self):
        url = f"{self.AUTH_URL}/me/"
        self.client.login(email="test@gmail.com", password="tester41")
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("email"), "test@gmail.com")

    def test_me_without_credentials(self):
        url = f"{self.AUTH_URL}/me/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class VerifyFundraiserViewsTests(TestCase):
    URL = 'http://127.0.0.1:8000/api/admin/fundraiser-requests/'

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_superuser(
            first_name="Te",
            last_name="st",
            email="admin@admin.com", password="admin1234")

    def test_new_fundraiser_and_verify(self):
        self.client.login(email="admin@admin.com", password="admin1234")

        new_fundraiser = User.objects.create_user(
            first_name="F", last_name="Test", email="ftest@gmail.com", password="12345678", role="FUNDRAISER", proposal_text="test fundraiser proposal")
        fundraiser_list_response = self.client.get(self.URL)
        self.assertEqual(fundraiser_list_response.status_code,
                         status.HTTP_200_OK)

        data = fundraiser_list_response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get("id"), new_fundraiser.id)
        self.assertEqual(data[0].get("proposal_text"),
                         "test fundraiser proposal")

        fundraiser_verify_response = self.client.put(
            self.URL, {"id": new_fundraiser.id})

        self.assertEqual(
            fundraiser_verify_response.status_code, status.HTTP_200_OK)

        fundraiser_verified = User.objects.get(id=new_fundraiser.id)
        self.assertEqual(fundraiser_verified.verified, True)
