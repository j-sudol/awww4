from django.urls import path
from routes import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from drf_yasg import openapi



router = DefaultRouter()
router.register(r'route', views.RouteViewSet, basename='route')

urlpatterns = [
    path('add_route/', views.addRoute, name='add_route'),
    path('route/', views.routeDetail, name='route_detail'),
    path('add_route_point/', views.addRoutePoint, name='add_route_point'),
    path('delete_route_point/<int:point_id>', views.removeRoutePoint, name='delete_route_point'),
    path('delete_route/<int:route_id>', views.deleteRoute, name='delete_route'),
]
