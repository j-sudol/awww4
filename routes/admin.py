from django.contrib import admin

# Register your models here.

from routes.models import Route
from routes.models import RoutePoint

class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'background')

admin.site.register(Route, RouteAdmin)
admin.site.register(RoutePoint)