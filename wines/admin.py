from django.contrib import admin

from wines.models import Wine, WineReview

admin.site.register(Wine)
admin.site.register(WineReview)
