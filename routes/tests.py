import json
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from backgrounds.models import Background
from .models import Route, RoutePoint
from .views import deleteRoute
from django.test import Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token


# Create your tests here.

class RoutesTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.background = Background.objects.create(name='Test Background', image='test_image.jpg')
        self.route = Route.objects.create(user=self.user, name='Test Route', background=self.background)
        self.route2 = Route.objects.create(user=self.user2, name='Test Route 2', background=self.background)

        self.assertEqual(Route.objects.count(), 2)

    def test_route_creation(self):
        # Create a new route
        new_route = Route.objects.create(user=self.user, name='New Route', background=self.background)
        
        # Check if the route was created successfully
        self.assertEqual(Route.objects.count(), 3)
        self.assertEqual(new_route.name, 'New Route')
        self.assertEqual(new_route.user.username, 'testuser')
        self.assertEqual(new_route.background.name, 'Test Background')
        self.assertEqual(new_route.background.image, 'test_image.jpg')
        self.assertEqual(new_route.background.id, self.background.id)

    def test_initial_route_count(self):
        self.assertEqual(Route.objects.count(), 2)  # Correct count after setup

    def remove_user(self):
        # Remove the user
        self.user.delete()
        
        # Check if the user was removed successfully
        self.assertEqual(User.objects.count(), 0)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='testuser')

class RoutePointTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.background = Background.objects.create(name='Test Background', image='test_image.jpg', created_at='2023-10-01')
        self.route1 = Route.objects.create(user=self.user, name='Test Route', background=self.background)
        self.route2 = Route.objects.create(user=self.user2, name='Test Route 2', background=self.background)
        
        # Create route points
        self.route_point1 = RoutePoint.objects.create(route=self.route1, x=10.0, y=20.0)
        self.route_point2 = RoutePoint.objects.create(route=self.route1, x=30.0, y=40.0)
        self.route_point3 = RoutePoint.objects.create(route=self.route1, x=50.0, y=60.0)
        self.route_point4 = RoutePoint.objects.create(route=self.route2, x=70.0, y=80.0)
        self.route_point5 = RoutePoint.objects.create(route=self.route2, x=90.0, y=100.0)

    def test_route_with_points(self):
        # Check if the route has points
        self.assertEqual(RoutePoint.objects.count(), 5)  # Correct count
        self.assertEqual(self.route1.points.count(), 3)
        self.assertEqual(self.route2.points.count(), 2)
    
    def test_remove_route_point(self):
        # Remove a route point
        self.route_point1.delete()
        
        # Check if the route point was removed successfully
        self.assertEqual(RoutePoint.objects.count(), 4)
        self.assertRaises(RoutePoint.DoesNotExist, RoutePoint.objects.get, id=self.route_point1.id)
        self.assertEqual(self.route1.points.count(), 2)
        self.assertEqual(self.route2.points.count(), 2)

        # Check the order of the remaining points
        remaining_points = RoutePoint.objects.filter(route=self.route1).order_by('order')
        self.assertEqual(remaining_points[0].order, 2)
        self.assertEqual(remaining_points[1].order, 3)

    def test_remove_route(self):
        # Remove a route
        self.route1.delete()
        
        # Check if the route was removed successfully
        self.assertEqual(Route.objects.count(), 1)
        self.assertRaises(Route.DoesNotExist, Route.objects.get, id=self.route1.id)
        self.assertEqual(RoutePoint.objects.count(), 2)  # Correct count
        self.assertEqual(self.route2.points.count(), 2)

class RouteEditTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user1 = User.objects.create_user(username='testuser1', password='testpassword1')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.background = Background.objects.create(name='Test Background', image='test_image.jpg')
        self.route1 = Route.objects.create(user=self.user1, name='Test Route', background=self.background)
        self.route2 = Route.objects.create(user=self.user2, name='Test Route 2', background=self.background)
        self.client = Client()
        self.client.login(username='testuser1', password='testpassword1')
    def test_route_delete(self):
        self.client.logout()
        response = self.client.post(reverse('delete_route', args=[self.route1.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Route.objects.count(), 2)

        self.client.login(username='testuser1', password='testpassword1')
        response = self.client.post(reverse('delete_route', args=[self.route2.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Route.objects.count(), 2)

        response = self.client.post(reverse('delete_route', args=[self.route1.id]))
        self.assertEqual(Route.objects.count(), 1)
        self.assertRaises(Route.DoesNotExist, Route.objects.get, id=self.route1.id)
    
    def test_point_add(self):
        # Add a new point to the route
        response = self.client.post(reverse('add_route_point'), {'route_id': self.route1.id, 'x': 30.0, 'y': 40.0}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RoutePoint.objects.count(), 1)
        self.assertEqual(self.route1.points.count(), 1)

        response = self.client.post(reverse('add_route_point'), {'route_id': self.route2.id, 'x': 30.0, 'y': 40.0}, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(RoutePoint.objects.count(), 1)
        self.assertEqual(self.route1.points.count(), 1)
        self.assertEqual(self.route2.points.count(), 0)

    def test_route_info(self):
        # Test route info
        response = self.client.get(reverse('route_detail') + f'?id={self.route1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')

        response = self.client.get(reverse('route_detail') + f'?id={self.route2.id}')
        self.assertEqual(response.status_code, 403)

class WebInterfaceTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        self.background = Background.objects.create(name='Test Background', image='test_image.jpg')
        self.route = Route.objects.create(user=self.user, name='Test Route', background=self.background)
        self.route2 = Route.objects.create(user=self.user, name='Test Route 2', background=self.background)
        self.route_point1 = RoutePoint.objects.create(route=self.route, x=10.0, y=20.0)

    def test_home_view(self):
        # Test the home view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        self.assertContains(response, 'Test Route 2')
        self.assertContains(response, 'testuser')

    def test_route_list_view(self):
        # Test the route list view
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        self.assertContains(response, 'Test Route 2')

    def test_route_add(self):
        # Test adding a new route
        self.client.post(reverse('add_route'), {'name': 'New Route', 'background': self.background.id})
        self.assertEqual(Route.objects.count(), 3)
        new_route = Route.objects.get(name='New Route')
        self.assertEqual(new_route.user.username, 'testuser')
        self.assertEqual(new_route.background.name, 'Test Background')
        self.assertEqual(new_route.background.image, 'test_image.jpg')
        self.assertEqual(new_route.points.count(), 0)

    def test_route_point_add(self):
        # Test adding a new point to a route
        response = self.client.post(reverse('add_route_point'), {'route_id': self.route.id, 'x': 10.0, 'y': 20.0}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RoutePoint.objects.count(), 2)
        new_point = RoutePoint.objects.get(id=2)
        self.assertEqual(new_point.x, 10.0)
        self.assertEqual(new_point.y, 20.0)

    def test_route_point_remove(self):
        # Test removing a point from a route
        self.client.post(reverse('delete_route_point', args=[self.route_point1.id]))
        self.assertEqual(RoutePoint.objects.count(), 0)
        self.assertRaises(RoutePoint.DoesNotExist, RoutePoint.objects.get, id=self.route_point1.id)
        self.assertEqual(self.route.points.count(), 0)

class ApiTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)   
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.token2 = Token.objects.create(user=self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)

        self.background = Background.objects.create(name='Test Background', image='test_image.jpg')
        self.route = Route.objects.create(user=self.user, name='Test Route', background=self.background)
        self.route2 = Route.objects.create(user=self.user, name='Test Route 2', background=self.background)
        self.route3 = Route.objects.create(user=self.user2, name='Test Route 3', background=self.background)
        self.route_point1 = RoutePoint.objects.create(route=self.route, x=10.0, y=20.0)

    def test_route_token_authentication(self):
        # Test token authentication
        response = self.client.get('/api/route/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        self.assertContains(response, 'Test Route 2')
        self.assertNotContains(response, 'Test Route 3')
        self.assertNotContains(response, 'testuser2')

    def test_route_details_token_authentication(self):
        # Test route details with token authentication
        response = self.client.get(f'/api/route/{self.route.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        self.assertNotContains(response, 'Test Route 2')

        response = self.client2.get(f'/api/route/{self.route.id}/')
        self.assertEqual(response.status_code, 404)

    def test_route_point_delete_token_authentication(self):
        # Test deleting a route point with token authentication

        response = self.client2.delete(f'/api/route/{self.route.id}/points/{self.route_point1.id}/')
        self.assertEqual(response.status_code, 404)

        response = self.client.delete(f'/api/route/{self.route.id}/points/{self.route_point1.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RoutePoint.objects.count(), 0)
        self.assertRaises(RoutePoint.DoesNotExist, RoutePoint.objects.get, id=self.route_point1.id)
        self.assertEqual(self.route.points.count(), 0)

class RouteEndpointTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.user2 = User.objects.create_user(username='testuser2', password='testpassword2')
        self.token2 = Token.objects.create(user=self.user2)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)

        self.background = Background.objects.create(name='Test Background', image='test_image.jpg')
        self.route = Route.objects.create(user=self.user, name='Test Route', background=self.background)
        self.route2 = Route.objects.create(user=self.user, name='Test Route 2', background=self.background)
        self.route_point1 = RoutePoint.objects.create(route=self.route, x=10.0, y=20.0)

        self.route3 = Route.objects.create(user=self.user2, name='Test Route 3', background=self.background)
        self.route_point2 = RoutePoint.objects.create(route=self.route3, x=30.0, y=40.0)

    def test_add_route(self):
        # Test adding a new route
        response = self.client.post('/api/route/', {'name': 'New Route', 'background': self.background.id})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Route.objects.count(), 4)
        new_route = Route.objects.get(name='New Route')
        self.assertEqual(new_route.user.username, 'testuser')
        self.assertEqual(new_route.background.name, 'Test Background')
        self.assertEqual(new_route.background.image, 'test_image.jpg')
        self.assertEqual(new_route.points.count(), 0)

    def test_route_list(self):
        # Test getting the list of routes
        response = self.client.get('/api/route/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        self.assertContains(response, 'Test Route 2')
        self.assertNotContains(response, 'Test Route 3')
        self.assertJSONEqual(str(response.content, 'utf-8'), json.dumps([{'id': self.route.id, 'user': self.user.id, 
                                                                         'name': 'Test Route', 'background': self.background.id},
                                                                        {'id': self.route2.id, 'user': self.user.id, 
                                                                         'name': 'Test Route 2', 'background': self.background.id}]))
    
    def test_route_details(self):
        # Test getting route details
        response = self.client.get(f'/api/route/{self.route.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Route')
        self.assertNotContains(response, 'Test Route 2')
        self.assertJSONEqual(str(response.content, 'utf-8'), json.dumps({'id': self.route.id, 'user': self.user.id, 
                                                                         'name': 'Test Route', 'background': self.background.id}))

        response = self.client2.get(f'/api/route/{self.route.id}/')
        self.assertEqual(response.status_code, 404)

    def test_route_delete(self):
        # Test deleting a route
        response = self.client.delete(f'/api/route/{self.route.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Route.objects.count(), 2)
        self.assertRaises(Route.DoesNotExist, Route.objects.get, id=self.route.id)
        self.assertEqual(RoutePoint.objects.count(), 1) # Removing the route should remove the points

        response = self.client2.delete(f'/api/route/{self.route.id}/')
        self.assertEqual(response.status_code, 404)

    def test_route_point_add(self):
        # Test adding a new point to a route
        response = self.client.post(f'/api/route/{self.route.id}/points/', {'x': 50.0, 'y': 40.0}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(RoutePoint.objects.count(), 3)
        new_point = RoutePoint.objects.get(x=50.0, y=40.0)
        self.assertEqual(new_point.route.id, self.route.id)
        self.assertEqual(new_point.x, 50.0)
        self.assertEqual(new_point.y, 40.0)

        
    def test_list_of_points(self):
        # Test getting the list of points for a route
        response = self.client.get(f'/api/route/{self.route.id}/points/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '10.0')
        self.assertContains(response, '20.0')
        self.assertNotContains(response, '30.0')
        self.assertNotContains(response, '40.0')
        self.assertJSONEqual(str(response.content, 'utf-8'), json.dumps([{'id': self.route_point1.id, 'route': self.route.id ,'x': 10.0, 'y': 20.0, 'order': 1}]))

        response = self.client2.get(f'/api/route/{self.route.id}/points/')
        self.assertEqual(response.status_code, 404)

    def test_route_point_delete(self):
        # Test deleting a route point
        response = self.client.delete(f'/api/route/{self.route.id}/points/{self.route_point1.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(RoutePoint.objects.count(), 1)
        self.assertRaises(RoutePoint.DoesNotExist, RoutePoint.objects.get, id=self.route_point1.id)
        self.assertEqual(self.route.points.count(), 0)

        response = self.client2.delete(f'/api/route/{self.route.id}/points/{self.route_point1.id}/')
        self.assertEqual(response.status_code, 404)

    def test_create_route_missing_fields(self):
        # Test creating a route with missing fields
        response = self.client.post('/api/route/', {'name': 'New Route'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Route.objects.count(), 3)
        self.assertJSONEqual(str(response.content, 'utf-8'), json.dumps({'background': ['This field is required.']}))

    def test_create_route_invalid_background(self):
        # Test creating a route with an invalid background
        response = self.client.post('/api/route/', {'name': 'New Route', 'background': 999})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Route.objects.count(), 3)
        self.assertJSONEqual(str(response.content, 'utf-8'), json.dumps({'background': ['Invalid pk "999" - object does not exist.']}))

    def test_create_route_point_invalid_route(self):
        # Test creating a route point with an invalid route
        response = self.client.post('/api/route/999/points/', {'x': 50.0, 'y': 40.0}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(RoutePoint.objects.count(), 2)

    def test_get_route_details_missing_route(self):
        # Test getting route details with a missing route
        response = self.client.get('/api/route/999/')
        self.assertEqual(response.status_code, 404)

    

    

        


        
    
