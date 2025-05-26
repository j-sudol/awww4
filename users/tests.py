from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm
# Create your tests here.


class UserTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
        )
        self.user.save()
    
    def test_user_creation(self):
        # Check if the user was created successfully
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('testpassword'))
        self.assertFalse(self.user.check_password('wrongpassword'))
        self.assertTrue(self.user.is_active)

    

    def test_user_deletion(self):
        # Delete the user
        self.user.delete()
        
        # Check if the user was deleted successfully
        self.assertEqual(User.objects.count(), 0)
        self.assertRaises(User.DoesNotExist, User.objects.get, username='testuser')

    

    def test_registration_form(self):
        # Test the registration form
        form_data = {
            'username': 'newuser',
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Create the user
        form.save()
        
        # Check if the user was created successfully
        self.assertEqual(User.objects.count(), 2)

    def test_registration_form_invalid(self):
        # Test the registration form with invalid data
        form_data = {
            'username': 'newuser',
            'password': 'newpassword',
            'password_confirm': 'differentpassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match', form.errors['password_confirm'])

    def test_registration_form_empty(self):
        # Test the registration form with empty data
        form_data = {
            'username': '',
            'password': '',
            'password_confirm': ''
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('This field is required.', form.errors['username'])
        self.assertIn('This field is required.', form.errors['password'])
        self.assertIn('This field is required.', form.errors['password_confirm'])

    def test_registration_form_username_exists(self):
        # Test the registration form with an existing username
        form_data = {
            'username': 'testuser',
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('A user with that username already exists.', form.errors['username'])

    def test_registration_form_with_too_long_username(self):
        # Test the registration form with a too long username
        form_data = {
            'username': 'a' * 151,  # Exceeding the max length of 150 characters
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Ensure this value has at most 150 characters (it has 151).', form.errors['username'])

class AuthenticationTestCase(TestCase):
    
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
        )
        self.user.save()
        self.client = Client()
        self.protected_url = reverse('home')
        self.login_url = reverse('login')

    def test_user_login(self):
        # Test user login
        login = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login)
        
        # Test user logout
        logout = self.client.logout()
        self.assertFalse(logout)
        # Check if the user is still active
        self.assertTrue(self.user.is_active)
    
    def test_user_update(self):
        # Update the user's username
        self.user.username = 'updateduser'
        self.user.save()
        
        # Check if the username was updated successfully
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'updateduser')

        login = self.client.login(username='updateduser', password='testpassword')
        self.assertTrue(login)
        
        # Test user logout
        logout = self.client.logout()
        self.assertFalse(logout)
    
    def test_login_view(self):
        # Test the login view
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.protected_url[0])
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'testuser')

    def test_login_view_invalid(self):
        # Test the login view with invalid credentials
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_and_logout(self):
        login = self.client.login(username='testuser', password='testpassword')
        self.assertTrue(login)

        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 200)

        self.client.logout()
        response = self.client.get(self.protected_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

        self.assertRedirects(response, self.login_url + '?next=' + self.protected_url[0])


