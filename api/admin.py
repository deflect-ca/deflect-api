from django.contrib import admin
from .models import Website, WebsiteOption, Record, Certificate, YamlDiff

class WebsiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'status', 'ip_address', 'created_at', 'updated_at')

class WebsiteOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data', 'website')

class RecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'hostname', 'value', 'priority', 'weight', 'port', 'ttl', 'website')

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostnames', 'has_private', 'date_created', 'date_expires', 'website')

class YamlDiffAdmin(admin.ModelAdmin):
    list_display = ('id', 'epoch_time', 'prev_epoch_time', 'partition')

# Register your models here.
admin.site.register(Website, WebsiteAdmin)
admin.site.register(WebsiteOption, WebsiteOptionAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(YamlDiff, YamlDiffAdmin)
