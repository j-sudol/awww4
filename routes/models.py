from django.db import models
from rest_framework import serializers
from rest_framework import viewsets
# Create your models here.

from backgrounds.models import Background

class Route(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    background = models.ForeignKey(Background, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.user.username}"

class RoutePoint(models.Model):
    id = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='points')
    x = models.FloatField()
    y = models.FloatField()
    order = models.IntegerField()

    def save(self, *args, **kwargs):
        if not self.order:  # If order is not set
            last_point = RoutePoint.objects.filter(route=self.route).order_by('-order').first()
            self.order = last_point.order + 1 if last_point else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Point {self.order} of {self.route.name}"

