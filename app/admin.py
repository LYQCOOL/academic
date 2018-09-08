from django.contrib import admin
from app import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.Wlibrary)
admin.site.register(models.Relation)
admin.site.register(models.Nexus)
