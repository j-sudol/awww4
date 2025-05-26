from django.contrib import admin
from django import forms
from .models import Board, Game

# Custom admin class for the Board model
class BoardAdmin(admin.ModelAdmin):
    list_display = ('board_name', 'user', 'rows', 'columns')  # Fields to display in the list view
    search_fields = ('board_name', 'user__username')  # Enable search by board name and username
    list_filter = ('user',)  # Add filters for the user field
    ordering = ('board_name',)  # Default ordering by board name

class GameAdmin(admin.ModelAdmin):
    list_display = ('user', 'board', 'dots')  # Fields to display in the list view
    search_fields = ('user__username', 'board__board_name')  # Enable search by username and board name
    list_filter = ('user', 'board')  # Add filters for user and board fields
    ordering = ('user',)  # Default ordering by user

admin.site.register(Board, BoardAdmin)
admin.site.register(Game, GameAdmin)  # Register the Game model with the custom admin class
