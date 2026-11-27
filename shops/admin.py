from django.contrib import admin

from .models import Service, Shop

admin.site.register(Shop)
admin.site.register(Service)