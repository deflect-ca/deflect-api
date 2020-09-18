from django.contrib import admin
from .models import Website, WebsiteOption

# Register your models here.
admin.site.register(Website)
admin.site.register(WebsiteOption)
