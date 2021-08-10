from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User

from campaign.models import Campaign


class CampaignFundraiserViewTests(APITestCase):
    BASE_URL = "http://127.0.0.1:8000/api/fundraiser/campaigns"
    AUTH_URL = "http://127.0.0.1:8000/api"

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            email="user@user.com", password="user1234", role="FUNDRAISER", proposal_text="CAMPAIGN")

    @property
    def bearer_token(self):
        """Returns Authorization headers, which can be passed to APIClient instance."""
        refresh = RefreshToken.for_user(self.user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def fundraiser_create_campaign(self):
        campaign = Campaign.objects.create(
            title="Title",
            description="Description",
            target_amount=2000000,
            created_at=timezone.now(),
            status="FUNDRAISER",
            fundraiser=self.user,
            image_url=""
        )
        return campaign

    def test_str_method(self):
        campaign = self.fundraiser_create_campaign
        self.assertEqual(
            str(campaign), f"{campaign.title}, {campaign.created_at}")

    def test_wrong_method(self):
        """Test CampaignList with not allowed methods"""
        url = f"{self.BASE_URL}/"
        response = self.client.delete(url, **self.bearer_token)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(url, **self.bearer_token)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, **self.bearer_token)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_fundraiser_get_all_campaigns(self):
        url = f"{self.BASE_URL}/"
        response = self.client.get(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fundraiser_create_campaign(self):
        url = f"{self.BASE_URL}/"
        data = {
            "title": "Title",
            "description": "Description",
            "target_amount": 2000000,
            "image_url": ""
        }
        response = self.client.post(url, data, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_fundraiser_detailed_campaign(self):
        campaign = self.fundraiser_create_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        response = self.client.get(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_fundraiser_invalid_id(self):
        url = f"{self.BASE_URL}/99/"
        response = self.client.get(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_fundraiser_campaign(self):
        campaign = self.fundraiser_create_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        response = self.client.delete(url, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_fundraiser_invalid_id(self):
        url = f"{self.BASE_URL}/99/"
        response = self.client.delete(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
