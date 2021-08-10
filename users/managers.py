from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """

        proposal_text = extra_fields.pop("proposal_text", None)
        is_fundraiser = extra_fields.get("role") == "FUNDRAISER"

        if is_fundraiser and proposal_text is None:
            raise ValueError("proposal_text is required for role FUNDRAISER.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.full_clean()
        user.save()

        if is_fundraiser:
            from .models import FundraiserProposal
            FundraiserProposal.objects.create(
                fundraiser=user, text=proposal_text)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True

        return self.create_user(email, password, **extra_fields)
