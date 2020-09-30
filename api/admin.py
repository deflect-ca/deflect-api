from django.contrib import admin
from .models import Website, WebsiteOption, Record, Certificate, YamlDiff

# Register your models here.
admin.site.register(Website)
admin.site.register(WebsiteOption)
admin.site.register(Record)
admin.site.register(Certificate)
admin.site.register(YamlDiff)
