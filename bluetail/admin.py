from django.contrib import admin

from bluetail.models import Flag, OCDSReleaseJSON, FlagAttachment


class FlagAdmin(admin.ModelAdmin):
    fields = ('flag_name', 'flag_field', 'flag_text', 'flag_type')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['flag_name']
        else:
            return []


admin.site.register(Flag, FlagAdmin)
admin.site.register(FlagAttachment)
admin.site.register(OCDSReleaseJSON)
