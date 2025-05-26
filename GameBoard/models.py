from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
# Create your models here.

def validate_dots(value):
    if not isinstance(value, list):
        raise ValidationError("Wartość musi być listą.")
    for dot in value:
        if not all(k in dot for k in ("row", "col", "color")):
            raise ValidationError("Każda kropka musi mieć 'row', 'col' i 'color'.")
        if not isinstance(dot["row"], int) or not isinstance(dot["col"], int):
            raise ValidationError("row i col muszą być liczbami.")
        if not isinstance(dot["color"], str):
            raise ValidationError("color musi być tekstem (hex-kolor).")

class Board(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board_name = models.CharField(max_length=100)
    rows = models.IntegerField(default=0)
    columns = models.IntegerField(default=0)
    dots = models.JSONField(default=list)

class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    dots = models.JSONField(default=list)
