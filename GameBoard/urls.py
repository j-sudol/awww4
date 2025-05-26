from . import views
from django.urls import path

urlpatterns = [
    path('edit/', views.create_or_edit_board, name='edit_board'),
    path('edit/<int:board_id>/', views.create_or_edit_board, name='edit_board'),
    path('', views.home, name='home'),
    path('delete_board/<int:board_id>', views.delete_board, name='delete_board'),
    path('solve/<int:board_id>', views.solve_board, name='solve_board'),
    path('save/', views.save_game, name='save_game'),
]