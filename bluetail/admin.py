from django.contrib import admin

from bluetail.models import Flag, OCDSReleaseJSON, FlagAttachment

admin.site.register(Flag)
admin.site.register(FlagAttachment)
admin.site.register(OCDSReleaseJSON)
