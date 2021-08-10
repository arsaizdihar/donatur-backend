from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from wallet.models import TopUpHistory


class TopUpViewTests(APITestCase):
    REQUEST_URL = "http://127.0.0.1:8000/api/topup/"
    VERIFY_URL = "http://127.0.0.1:8000/api/topup/requests/"

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_superuser(
            email="admin@admin.com", password="admin1234")
        cls.user = User.objects.create_user(
            email="user@user.com", password="user1234", role="DONATUR")
        cls.data = {
            "bank_name": "BCA",
            "bank_account": "User",
            "bank_account_number": "012345678",
            "amount": 100000
        }

    @property
    def admin_bearer_token(self):
        refresh = RefreshToken.for_user(self.admin)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def user_bearer_token(self):
        refresh = RefreshToken.for_user(self.user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def top_up_request(self):
        return TopUpHistory.objects.create(user=self.user, **self.data)

    def test_str_method(self):
        top_up = self.top_up_request
        self.assertEqual(str(top_up), f"{top_up.user.id} {top_up.date}")

    def test_request_top_up(self):
        response = self.client.post(
            self.REQUEST_URL, data=self.data, **self.user_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TopUpHistory.objects.filter(user=self.user).exists())

    def test_miss_required_field(self):
        data = self.data.copy()
        data.pop("bank_name")

        response = self.client.post(
            self.REQUEST_URL, data=data, **self.user_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fundraiser_role(self):
        user = self.user
        user.role = "FUNDRAISER"
        user.save()

        response = self.client.post(
            self.REQUEST_URL, data=self.data, **self.user_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_no_auth(self):
        response = self.client.post(
            self.REQUEST_URL, data=self.data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_top_up(self):
        top_up_id = self.top_up_request.id

        response = self.client.patch(
            self.VERIFY_URL, {"id": top_up_id}, **self.admin_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(TopUpHistory.objects.get(id=top_up_id).verified)
        self.assertEqual(User.objects.get(
            id=self.user.id).wallet_amount, 100000)

    def test_verify_missing_id(self):
        response = self.client.patch(
            self.VERIFY_URL, **self.admin_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_id_not_number(self):
        response = self.client.patch(
            self.VERIFY_URL, {"id": "asdasd"}, **self.admin_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_id(self):
        response = self.client.patch(
            self.VERIFY_URL, {"id": "123"}, **self.admin_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_verified_top_up(self):
        top_up = self.top_up_request
        top_up.verify()

        response = self.client.patch(
            self.VERIFY_URL, {"id": top_up.id}, **self.admin_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(response.json().get("code"), "verified")

    def test_top_up_requests_list(self):
        top_up = self.top_up_request
        response = self.client.get(self.VERIFY_URL, **self.admin_bearer_token)

        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0].get("id"), top_up.id)

    def test_verify_top_up_no_admin(self):
        top_up_id = self.top_up_request.id
        response = self.client.patch(
            self.VERIFY_URL, {"id": top_up_id}, **self.user_bearer_token)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
