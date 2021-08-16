from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from wallet.models import DonationHistory, WithdrawRequest

from campaign.models import Campaign


class CampaignFundraiserViewTests(APITestCase):
    BASE_URL = "http://127.0.0.1:8000/api/fundraiser/campaigns"

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            first_name="Te", last_name="st",
            email="user@user.com", password="user1234", role="FUNDRAISER", proposal_text="CAMPAIGN", verified=True)

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
            status="PENDING",
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

    def test_get_all_campaigns(self):
        campaign = self.fundraiser_create_campaign
        campaign2 = self.fundraiser_create_campaign
        campaign2.status = "VERIFIED"
        campaign2.save()

        url = f"http://127.0.0.1:8000/api/campaigns/"
        response = self.client.get(url, format="json")
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 1)
        self.assertEqual(Campaign.objects.all().count(), 2)

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
            "image_url": "",
        }
        response = self.client.post(url, data, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_fundraiser_create_campaign_not_verified(self):
        url = f"{self.BASE_URL}/"
        data = {
            "title": "Title",
            "description": "Description",
            "target_amount": 2000000,
            "image_url": "",
        }
        self.user.verified = False
        self.user.save()
        response = self.client.post(url, data, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_fundraiser_create_campaign_missing_field(self):
        url = f"{self.BASE_URL}/"
        data = {
            "description": "Description",
            "image_url": ""
        }
        response = self.client.post(url, data, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_fundraiser_detailed_campaign(self):
        campaign = self.fundraiser_create_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        response = self.client.get(url, format="json", **self.bearer_token)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("id"), campaign.id)

        keys = ('id', 'title', 'description', 'amount', 'target_amount',
                'status', 'image_url')

        for key in keys:
            self.assertEqual(data.get(key), getattr(campaign, key))

        self.assertEqual(parse_datetime(data.get(
            "created_at")), campaign.created_at)

        self.assertEqual(data.get(
            "fundraiser", {}).get("full_name"), self.user.get_full_name())

        self.assertEqual(data.get(
            "fundraiser", {}).get("email"), self.user.email)

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

    def test_stop_fundraiser_campaign(self):
        campaign = self.fundraiser_create_campaign
        campaign.verify()
        url = f"{self.BASE_URL}/{campaign.id}/"
        response = self.client.patch(url, **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Campaign.objects.get(
            id=campaign.id).status, "STOPPED")


class CampaignVerifyViewTests(APITestCase):
    BASE_URL = "http://127.0.0.1:8000/api/admin/proposals"

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_superuser(
            email="admin@admin.com", password="admin3231", first_name="Te",
            last_name="st")
        cls.user = User.objects.create_user(
            first_name="Te", last_name="st",
            email="user@user.com", password="user1234", role="FUNDRAISER", proposal_text="CAMPAIGN")

    @property
    def make_campaign(self):
        campaign = Campaign.objects.create(
            title="Title",
            description="Description",
            target_amount=2000000,
            created_at=timezone.now(),
            status="PENDING",
            fundraiser=self.user,
            image_url=""
        )
        return campaign

    @property
    def admin_bearer_token(self):
        refresh = RefreshToken.for_user(self.admin)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def user_bearer_token(self):
        refresh = RefreshToken.for_user(self.user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    def test_get_all_pending_campaign(self):
        url = f"{self.BASE_URL}/"
        response = self.client.get(url, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_pending_campaign_not_admin(self):
        url = f"{self.BASE_URL}/"
        response = self.client.get(url, **self.user_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_pending_campaign_by_id(self):
        data = self.make_campaign
        url = f"{self.BASE_URL}/{data.id}/"
        response = self.client.get(url, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_pending_campaign_by_id_not_admin(self):
        data = self.make_campaign
        url = f"{self.BASE_URL}/{data.id}/"
        response = self.client.get(url, **self.user_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_no_data_by_id(self):
        url = f"{self.BASE_URL}/1/"
        response = self.client.get(url, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_pending_campaign_wrong_method(self):
        url = f"{self.BASE_URL}/"
        response = self.client.delete(url, **self.admin_bearer_token)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(url, **self.admin_bearer_token)
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_wrong_url(self):
        url = f"{self.BASE_URL}/xx/"
        response = self.client.get(url, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauth_admin(self):
        url = f"{self.BASE_URL}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_proposal_campaign(self):
        url = f"{self.BASE_URL}/"
        proposal_campaign = self.make_campaign
        verify_proposal_campaign = {
            "id": proposal_campaign.id, "status": "VERIFIED"}

        response = self.client.put(
            url, verify_proposal_campaign, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        proposal_campaign = Campaign.objects.first()
        self.assertEqual(proposal_campaign.status, "VERIFIED")

    def test_reject_proposal_campaign(self):
        url = f"{self.BASE_URL}/"
        proposal_campaign = self.make_campaign
        verify_proposal_campaign = {
            "id": proposal_campaign.id, "status": "REJECTED"}

        response = self.client.put(
            url, verify_proposal_campaign, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        proposal_campaign = Campaign.objects.first()
        self.assertEqual(proposal_campaign.status, "REJECTED")

    def test_verify_campaign_by_id(self):
        data = self.make_campaign
        url = f"{self.BASE_URL}/{data.id}/"
        verify_proposal_campaign = {"id": data.id, "status": "VERIFIED"}

        response = self.client.put(
            url, verify_proposal_campaign, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        proposal_campaign = Campaign.objects.first()
        self.assertEqual(proposal_campaign.status, "VERIFIED")

    def test_reject_campaign_by_id(self):
        data = self.make_campaign
        url = f"{self.BASE_URL}/{data.id}/"
        verify_proposal_campaign = {"id": data.id, "status": "REJECTED"}

        response = self.client.put(
            url, verify_proposal_campaign, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        proposal_campaign = Campaign.objects.first()
        self.assertEqual(proposal_campaign.status, "REJECTED")

    def test_verify_campaign_invalid_id_by_id(self):
        data = self.make_campaign
        url = f"{self.BASE_URL}/2/"
        verify_proposal_campaign = {"id": data.id, "status": "VERIFIED"}

        response = self.client.put(
            url, verify_proposal_campaign, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verify_campaign_invalid_id(self):
        url = f"{self.BASE_URL}/"
        verify_proposal_campaign = {"id": "2", "status": "REJECTED"}

        response = self.client.put(
            url, verify_proposal_campaign, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class DonationViewTests(APITestCase):
    BASE_URL = "http://127.0.0.1:8000/api/donor/campaigns"

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            first_name="Te", last_name="st",
            email="user@user.com", password="user1234", role="DONATUR", wallet_amount=100000)
        cls.user2 = User.objects.create_user(
            first_name="Te", last_name="st",
            email="user2@user2.com", password="user1234", role="DONATUR", wallet_amount=0)

    @property
    def bearer_token(self):
        """Returns Authorization headers, which can be passed to APIClient instance."""
        refresh = RefreshToken.for_user(self.user)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def bearer_token2(self):
        """Returns Authorization headers, which can be passed to APIClient instance."""
        refresh = RefreshToken.for_user(self.user2)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def make_campaign(self):
        campaign = Campaign.objects.create(
            title="Title",
            description="Description",
            target_amount=10000,
            created_at=timezone.now(),
            status="PENDING",
            fundraiser=self.user,
            image_url=""
        )
        return campaign

    def test_retrieve_campaign_by_id(self):
        data = self.make_campaign
        url = f"{self.BASE_URL}/{data.id}/"
        response = self.client.get(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_campaign_invalid_id(self):
        url = f"{self.BASE_URL}/10/"
        response = self.client.get(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_donation(self):
        campaign = self.make_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        request = {
            "amount": 6000,
            "password": "user1234"
        }
        response = self.client.post(
            url, request, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="user@user.com")
        self.assertEqual(user.wallet_amount, 100000 - 6000)

    def test_create_donation_wrong_password(self):
        campaign = self.make_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        request = {
            "amount": 6000,
            "password": "wrong_pw"
        }
        response = self.client.post(
            url, request, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_donation_user_wallet_lt_amount(self):
        campaign = self.make_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        request = {
            "amount": 6000,
            "password": "user1234"
        }
        response = self.client.post(
            url, request, format="json", **self.bearer_token2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donation_view(self):
        campaign = self.make_campaign
        url = f"{self.BASE_URL}/{campaign.id}/"
        url_donate = "http://127.0.0.1:8000/api/donate/"

        request = {
            "amount": 6000,
            "password": "user1234"
        }
        self.client.post(url, request, format="json", **self.bearer_token)

        response = self.client.get(url, format="json", **self.bearer_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(DonationHistory.objects.filter(
            user=self.user).count(), 1)
        self.assertEqual(DonationHistory.objects.filter(
            user=self.user2).count(), 0)


class WithdrawVerifyViewTests(APITestCase):
    WITHDRAW_URL = "http://127.0.0.1:8000/api/fundraiser/campaigns"
    WITHDRAW_LIST_URL = "http://127.0.0.1:8000/api/withdraw/"
    VERIF_URL = "http://127.0.0.1:8000/api/withdraw/requests"
    DONATE_URL = "http://127.0.0.1:8000/api/donor/campaigns"
    CAMPAIGN_URL = "http://127.0.0.1:8000/api/admin/proposals"

    def setUp(self) -> None:
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls) -> None:
        cls.admin = User.objects.create_superuser(
            email="admin@gmail.com", password="admin3231", first_name="I'm",
            last_name="Admin")
        cls.fundraiser = User.objects.create_user(
            first_name="I'm", last_name="Fundraiser",
            email="fundraiser@gmail.com", password="user1234", role="FUNDRAISER", proposal_text="CAMPAIGN", verified=True)
        cls.donatur = User.objects.create_user(
            first_name="I'm", last_name="Donatur",
            email="donatur@gmail.com", password="user1234", role="DONATUR", wallet_amount=1000000)

    @property
    def admin_bearer_token(self):
        refresh = RefreshToken.for_user(self.admin)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def fundraiser_bearer_token(self):
        refresh = RefreshToken.for_user(self.fundraiser)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def donatur_bearer_token(self):
        refresh = RefreshToken.for_user(self.donatur)
        return {"HTTP_AUTHORIZATION": f'Bearer {refresh.access_token}'}

    @property
    def make_campaign(self):
        campaign = Campaign.objects.create(
            title="Title",
            description="Description",
            amount=0,
            target_amount=2000000,
            created_at=timezone.now(),
            status="PENDING",
            fundraiser=self.fundraiser,
            image_url=""
        )
        return campaign

    def test_withdraw_workflow(self):
        campaign = self.make_campaign
        campaign2 = self.make_campaign
        url_verify_withdraw = f"{self.VERIF_URL}/"
        url_verify_campaign = f"{self.CAMPAIGN_URL}/{campaign.id}/"
        url_withdraw = f"{self.WITHDRAW_URL}/{campaign.id}/"
        url_donate = f"{self.DONATE_URL}/{campaign.id}/"

        """  Verify proposal campaign from campaign"""
        verify_proposal_campaign = {
            "id": campaign.id, "status": "VERIFIED"}
        response = self.client.put(
            url_verify_campaign, verify_proposal_campaign, format="json",
            **self.admin_bearer_token
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        proposal_campaign = Campaign.objects.first()
        self.assertEqual(proposal_campaign.status, "VERIFIED")

        """  Donate from Donatur user """
        data_donate = {
            "amount": 500000,
            "password": "user1234"
        }
        response = self.client.post(
            url_donate, data_donate, format="json", **self.donatur_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        donatur = User.objects.get(email="donatur@gmail.com")
        self.assertEqual(donatur.wallet_amount, 500000)

        campaign = Campaign.objects.get(id=campaign.id)
        self.assertEqual(campaign.amount, 500000)

        donation = DonationHistory.objects.first()
        self.assertEqual(donation.amount, 500000)

        """  Fundraiser request for withdraw """
        request_withdraw = {
            "amount": 300000
        }
        response = self.client.post(
            url_withdraw, request_withdraw, format="json", **self.fundraiser_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.fundraiser.wallet_amount, 0)

        response = self.client.get(
            self.WITHDRAW_LIST_URL, format="json", **self.fundraiser_bearer_token)
        self.assertEqual(len(response.json()), 1)

        fundraiser = User.objects.get(email="fundraiser@gmail.com")
        withdraw = WithdrawRequest.objects.filter(user=fundraiser)
        campaign = Campaign.objects.get(
            fundraiser=fundraiser, status="VERIFIED")
        self.assertEqual(withdraw.count(), 1)
        self.assertEqual(campaign.withdraw_amount, 300000)

        """ Test REJECTED Withdraw Request """
        verify_withdraw = {
            "id": campaign.id, "status": "REJECTED"
        }
        response = self.client.put(
            url_verify_withdraw, verify_withdraw, format="json", **self.admin_bearer_token)

        withdraw = WithdrawRequest.objects.get(
            user=fundraiser, campaign=campaign)
        campaign = Campaign.objects.first()

        self.assertEqual(campaign.amount, 500000)
        self.assertEqual(withdraw.status, "REJECTED")
        self.assertEqual(self.fundraiser.wallet_amount, 0)
        self.assertEqual(campaign.withdraw_amount, 300000)

        """ Test withdraw status already VERIFIED """
        withdraw.status = "VERIFIED"
        withdraw.save()
        verify_withdraw = {
            "id": campaign.id, "status": "VERIFIED"}

        response = self.client.put(
            url_verify_withdraw, verify_withdraw, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("code"), "verified")

        """ Test withdraw status already REJECTED """
        withdraw.status = "REJECTED"
        withdraw.save()
        verify_withdraw = {
            "id": campaign.id, "status": "VERIFIED"}

        response = self.client.put(
            url_verify_withdraw, verify_withdraw, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("code"), "rejected")

        """ Test withdraw invalid id """
        verify_withdraw = {
            "id": "abcd", "status": "VERIFIED"}

        response = self.client.put(
            url_verify_withdraw, verify_withdraw, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("code"), "invalid-id")

        """ Test withdraw.status not a REJECTED && VERIFIED """
        verify_withdraw = {
            "id": campaign.id, "status": "TEST_ERROR"
        }

        response = self.client.put(
            url_verify_withdraw, verify_withdraw, **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("status"), ["Invalid status"])

        """ Test VERIFIED Withdraw Request """
        withdraw.status = "PENDING"
        withdraw.save()

        verify_withdraw = {
            "id": campaign.id, "status": "VERIFIED"}

        response = self.client.put(
            url_verify_withdraw, verify_withdraw, **self.admin_bearer_token)

        withdraw = WithdrawRequest.objects.get(
            user=self.fundraiser, campaign=campaign)
        campaign = Campaign.objects.first()
        fundraiser = User.objects.get(email="fundraiser@gmail.com")

        self.assertEqual(campaign.withdraw_amount, 0)
        self.assertEqual(withdraw.status, "VERIFIED")
        self.assertEqual(fundraiser.wallet_amount, 300000)

    def test_fundraiser_not_verified(self):
        fundraiser = User.objects.get(email="fundraiser@gmail.com")
        fundraiser.verified = False
        fundraiser.save()

        campaign = self.make_campaign
        url = f"{self.WITHDRAW_URL}/{campaign.id}/"
        request = {
            "amount": 0
        }
        response = self.client.post(
            url, request, **self.fundraiser_bearer_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("status"),
                         "fundraiser not verified.")

    def test_amount_gt_campaign_amount(self):
        campaign = self.make_campaign
        url = f"{self.WITHDRAW_URL}/{campaign.id}/"
        request = {
            "amount": 50000
        }
        response = self.client.post(
            url, request, **self.fundraiser_bearer_token
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("status"),
                         "You can't do withdraw request.")

    def test_verify_no_withdraw_id(self):
        campaign = self.make_campaign
        url = f"{self.VERIF_URL}/"
        request = {
            "status": "VERIFIED"
        }
        response = self.client.put(
            url, request, format="json", **self.admin_bearer_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("id"), "This field is required.")
