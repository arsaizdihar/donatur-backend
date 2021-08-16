from django.contrib import admin

from .models import FundraiserProposal, User

admin.site.register((User, FundraiserProposal))
