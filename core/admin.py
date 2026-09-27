from django.contrib import admin
from .models import Company, Profile, Shift, ShiftRequest

admin.site.register(Company)
admin.site.register(Profile)
admin.site.register(Shift)
admin.site.register(ShiftRequest)