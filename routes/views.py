from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.urls import reverse
from itertools import tee
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

from .forms import addRouteForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Route
from .models import RoutePoint
from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.utils import OpenApiExample
def pairwise(iterable):
    """Helper function to create pairs of consecutive points."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

@login_required
def addRoute(request):
    if request.method == 'POST':
        form = addRouteForm(request.POST)
        if form.is_valid():
            route = form.save(commit=False)
            route.user = request.user
            route.save()

            return redirect(f"{reverse('route_detail')}?id={route.id}")
    else:
        form = addRouteForm()
    return render(request, 'add_route.html', {'add_form': form})

@login_required
def deleteRoute(request, route_id):
    if not route_id:
        return redirect('home')
    try:
        route = Route.objects.get(id=route_id)
    except Route.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Route not found.'}, status=404)
    if route.user != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized.'}, status=403)
    route.delete()

    return redirect('home')

@login_required
def routeDetail(request):
    id = request.GET.get('id')
    if not id:
        return redirect('home')
    try:
        route = Route.objects.get(id=id)
    except Route.DoesNotExist:
        return redirect('home')

    if route.user != request.user:
        return JsonResponse({'success': False, 'error': 'Unauthorized.'}, status=403)
    
    points = RoutePoint.objects.filter(route=route).order_by('order')
    paired_points = list(pairwise(points))  # Create pairs of consecutive points

    return render(request, 'route_detail.html', {'route': route, 'points': points, 'paired_points': paired_points}, status=200)

@csrf_exempt
@login_required
def addRoutePoint(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        x = data.get('x')
        y = data.get('y')
        route_id = data.get('route_id')

        try:
            route = Route.objects.get(id=route_id)
            if route.user != request.user:
                return JsonResponse({'success': False, 'error': 'Unauthorized.'}, status=403)
            RoutePoint.objects.create(route=route, x=x, y=y)
            points = RoutePoint.objects.filter(route=route).order_by('order')
            return render(request, 'route_detail.html', {'route': route, 'points': points})
        except Route.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Route not found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})

@csrf_exempt
@login_required
def removeRoutePoint(request, point_id):
    if request.method == 'POST':
        try:
            point = RoutePoint.objects.get(id=point_id)
            order = point.order
            route = point.route
            if route.user != request.user:
                return JsonResponse({'success': False, 'error': 'Unauthorized.'}, status=403)
            
            # Delete the point and update the order of remaining points
            point.delete()
            for p in RoutePoint.objects.filter(route=route, order__gt=order):
                p.order -= 1
                p.save()

            # Redirect to the route detail page
            return redirect(f"{reverse('route_detail')}?id={route.id}")
        except RoutePoint.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Point not found.'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request.'}, status=400)



class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'user', 'name', 'background']   
        read_only_fields = ['user']
        extra_kwargs = {
            'name': {'help_text': 'Nazwa trasy'},
            'background': {'help_text': 'Tło używane do wizualizacji trasy'},
        }

class RoutePointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutePoint
        fields = ['id', 'route', 'x', 'y', 'order']
        read_only_fields = ['order', 'route']
        extra_kwargs = {
            'x': {'help_text': 'Współrzędna X punktu'},
            'y': {'help_text': 'Współrzędna Y punktu'},
            'route': {'help_text': 'Trasa, do której należy punkt'},
        }


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="Szczegóły trasy",
        description="Pobiera szczegóły wybranej trasy użytkownika.",
        responses={200: RouteSerializer},
        examples=[
            OpenApiExample(
                name="Przykład odpowiedzi",
                value={
                    "id": 1,
                    "name": "Trasa testowa",
                    "background_name": "Tło testowe",
                    "points": [
                        {"id": 1, "route": 1, "x": 50.06143, "y": 19.93658, "order": 1},
                        {"id": 2, "route": 1, "x": 50.06243, "y": 19.93758, "order": 2}
                    ]
                },
                response_only=True
            )
        ]
    )
    @action(detail=True, methods=['get'], url_path='details')
    def details(self, request, pk=None):
        try:
            route = self.get_queryset().get(pk=pk)
        except Route.DoesNotExist:
            return Response({'success': False, 'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

        points = RoutePoint.objects.filter(route=route).order_by('order')
        points_data = RoutePointSerializer(points, many=True).data

        return Response({
            'id': route.id,
            'name': route.name,
            'background_name': route.background.name if route.background else None,
            'points': points_data
        }, status=status.HTTP_200_OK)
    
    @extend_schema(
        methods=['GET'],
        summary="Pobierz punkty trasy",
        description="Pobiera listę punktów należących do wybranej trasy użytkownika.",
        responses={
            200: RoutePointSerializer(many=True),
            404: OpenApiExample(
                name="Trasa nie znaleziona",
                value={"success": False, "error": "Route not found"},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                name="Przykład odpowiedzi",
                value=[
                    {"id": 1, "route": 1, "x": 50.06143, "y": 19.93658, "order": 1},
                    {"id": 2, "route": 1, "x": 50.06243, "y": 19.93758, "order": 2},
                ],
                response_only=True,
            )
        ],
        tags=["Punkty"],
    )
    @extend_schema(
        methods=['POST'],
        summary="Dodaj punkt do trasy",
        description="Dodaje nowy punkt (x, y) do wybranej trasy użytkownika.",
        request=RoutePointSerializer,
        responses={
            201: RoutePointSerializer,
            400: OpenApiExample(
                name="Nieprawidłowe dane",
                value={"x": ["This field is required."], "y": ["This field is required."]},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                name="Przykład żądania",
                value={
                    "x": 50.06143,
                    "y": 19.93658
                },
                request_only=True
            ),
            OpenApiExample(
                name="Przykład odpowiedzi",
                value={
                    "id": 123,
                    "route": 1,
                    "x": 50.06143,
                    "y": 19.93658,
                    "order": 4
                },
                response_only=True
            ),
        ],
        tags=["Punkty"],
    )
    @action(detail=True, methods=['get', 'post'], url_path='points', serializer_class=RoutePointSerializer)
    def points(self, request, pk=None):
        try:
            route = self.get_queryset().get(pk=pk)
        except Route.DoesNotExist:
            return Response({'success': False, 'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            try:
                route = self.get_queryset().get(pk=pk)
            except Route.DoesNotExist:
                return Response({'success': False, 'error': 'Route not found'}, status=status.HTTP_404_NOT_FOUND)

            points = RoutePoint.objects.filter(route=route).order_by('order')
            points_data = RoutePointSerializer(points, many=True).data

            return Response(points_data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            serializer = RoutePointSerializer(data=request.data)
            if serializer.is_valid():
                route = self.get_queryset().get(pk=pk)
                serializer.save(route=route)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @extend_schema(
        summary="Usuń punkt z trasy",
        description="Usuwa punkt z wybranej trasy użytkownika.",
        responses={
            204: None,  # No content for successful deletion
            403: OpenApiExample(
                name="Brak uprawnień",
                value={"success": False, "error": "Unauthorized"},
                response_only=True,
            ),
            404: OpenApiExample(
                name="Nie znaleziono",
                value={"success": False, "error": "Route or point not found"},
                response_only=True,
            ),
        },
        examples=[
            OpenApiExample(
                name="Przykład żądania",
                value={"point_id": 1},
                request_only=True
            )
        ]
    )
    @action(detail=True, methods=['delete'], url_path='points/(?P<point_id>[^/.]+)')
    def delete_point(self, request, pk=None, point_id=None):
        try:
            route = self.get_queryset().get(pk=pk)
            point = RoutePoint.objects.get(pk=point_id, route=route)
        except (Route.DoesNotExist, RoutePoint.DoesNotExist):
            return Response({'success': False, 'error': 'Route or point not found'}, status=status.HTTP_404_NOT_FOUND)

        if route.user != request.user:
            return Response({'success': False, 'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

        point.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Lista tras użytkownika",
        description="Pobiera listę tras należących do zalogowanego użytkownika.",
        responses={200: RouteSerializer(many=True)},
        examples=[
            OpenApiExample(
                name="Przykład odpowiedzi",
                value=[
                    {"id": 1, "user": 1, "name": "Trasa 1", "background": 1},
                    {"id": 2, "user": 1, "name": "Trasa 2", "background": 2}
                ],
                response_only=True
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Dodaj nową trasę",
        description="Tworzy nową trasę dla zalogowanego użytkownika.",
        request=RouteSerializer,
        responses={201: RouteSerializer},
        examples=[
            OpenApiExample(
                name="Przykład żądania",
                value={"name": "Nowa Trasa", "background": 1},
                request_only=True
            ),
            OpenApiExample(
                name="Przykład odpowiedzi",
                value={"id": 1, "user": 1, "name": "Nowa Trasa", "background": 1},
                response_only=True
            )
        ]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Szczegóły trasy",
        description="Pobiera szczegóły wybranej trasy użytkownika.",
        responses={200: RouteSerializer},
        examples=[
            OpenApiExample(
                name="Przykład odpowiedzi",
                value={"id": 1, "user": 1, "name": "Trasa 1", "background": 1},
                response_only=True
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Aktualizuj trasę",
        description="Aktualizuje szczegóły wybranej trasy użytkownika.",
        request=RouteSerializer,
        responses={200: RouteSerializer},
        examples=[
            OpenApiExample(
                name="Przykład żądania",
                value={"name": "Zaktualizowana Trasa", "background": 2},
                request_only=True
            ),
            OpenApiExample(
                name="Przykład odpowiedzi",
                value={"id": 1, "user": 1, "name": "Zaktualizowana Trasa", "background": 2},
                response_only=True
            )
        ]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Częściowa aktualizacja trasy",
        description="Częściowo aktualizuje szczegóły wybranej trasy użytkownika.",
        request=RouteSerializer,
        responses={200: RouteSerializer},
        examples=[
            OpenApiExample(
                name="Przykład żądania",
                value={"name": "Częściowa aktualizacja"},
                request_only=True
            ),
            OpenApiExample(
                name="Przykład odpowiedzi",
                value={"id": 1, "user": 1, "name": "Częściowa aktualizacja", "background": 1},
                response_only=True
            )
        ]
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Usuń trasę",
        description="Usuwa wybraną trasę użytkownika.",
        responses={204: None},
        examples=[
            OpenApiExample(
                name="Przykład żądania",
                value={"id": 1},
                request_only=True
            )
        ]
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)