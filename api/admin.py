from django.contrib import admin
from .models import Website, WebsiteOption, Record, Certificate, YamlDiff, Edge, Dnet

class WebsiteAdmin(admin.ModelAdmin):
    list_filter = ['status', 'created_at', 'updated_at']
    list_display = ('id', 'url', 'status', 'ip_address', 'created_at', 'updated_at')

class WebsiteOptionAdmin(admin.ModelAdmin):
    list_filter = ['name', 'website']
    list_display = ('id', 'name', 'data', 'website')

class RecordAdmin(admin.ModelAdmin):
    list_filter = ['type', 'website']
    list_display = ('id', 'type', 'hostname', 'priority', 'weight', 'port', 'ttl', 'website')

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'hostnames', 'has_private', 'date_created', 'date_expires', 'website')

class YamlDiffAdmin(admin.ModelAdmin):
    exclude = ['diff']
    list_display = ('id', 'epoch_time', 'prev_epoch_time', 'partition')

class EdgeAdmin(admin.ModelAdmin):
    list_filter = ['dnet']
    list_display = ('id', 'hostname', 'ip', 'created_at', 'updated_at')

class DnetAdmin(admin.ModelAdmin):
    list_filter = ['name']
    list_display = ('id', 'name', 'created_at', 'updated_at')


# Register your models here.
admin.site.register(Website, WebsiteAdmin)
admin.site.register(WebsiteOption, WebsiteOptionAdmin)
admin.site.register(Record, RecordAdmin)
admin.site.register(Certificate, CertificateAdmin)
admin.site.register(YamlDiff, YamlDiffAdmin)
admin.site.register(Edge, EdgeAdmin)
admin.site.register(Dnet, DnetAdmin)
