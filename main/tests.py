import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.utils import timezone
from django.db.utils import IntegrityError
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser, CustomUserManager
from .forms import CustomUserCreationForm, CustomUserChangeForm
from . import views # Import views for URL resolution

# Import dependent models for profile view testing (using try-except as in views)
try:
    from club_directories.models import League, Club, LeaguePick as FavoriteClub # Use LeaguePick as FavoriteClub based on previous context
except ImportError:
    League, Club, FavoriteClub = None, None, None

try:
    from forum.models import Post
except ImportError:
    Post = None

try:
    # Assuming matchpredictions has Match and Vote models
    from matchpredictions.models import Match, Vote
except ImportError:
    Match, Vote = None, None

# Helper function from previous tests
def create_user(username, password='password123', is_staff=False, email_suffix='@example.com', full_name_prefix='Test ', role='user'):
    is_staff_flag = is_staff or (role == 'admin')

    if role == 'admin':
        return CustomUser.objects.create_superuser(
            username=username,
            password=password,
            email=f'{username}{email_suffix}',
            full_name=f'{full_name_prefix}{username.capitalize()}'
        )
    else:
        return CustomUser.objects.create_user(
            username=username,
            password=password,
            email=f'{username}{email_suffix}',
            full_name=f'{full_name_prefix}{username.capitalize()}',
            role=role,
            is_staff=is_staff_flag
        )

class MainAppTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.user = create_user('main_user', role='user')
        cls.admin_user = create_user('main_admin', role='admin')

        if League and Club and FavoriteClub:
            cls.league = League.objects.create(name="Profile League", region="Profile Region")
            cls.club = Club.objects.create(league=cls.league, name="Profile Club")
            cls.fav_club = FavoriteClub.objects.create(user=cls.user, league=cls.league, club=cls.club)
        else:
            cls.fav_club = None

        if Post:
            cls.post = Post.objects.create(author=cls.user, title="Profile Post", content="Test")
        else:
            cls.post = None

        if Match and Vote:
            home_team, _ = Club.objects.get_or_create(name="Home Team", defaults={'league': cls.league})
            away_team, _ = Club.objects.get_or_create(name="Away Team", defaults={'league': cls.league})
            cls.match = Match.objects.create(
                home_team=home_team, away_team=away_team,
                match_date=timezone.now(), league=cls.league
            )
            cls.vote = Vote.objects.create(user=cls.user, match=cls.match, prediction='home_win')
        else:
             cls.vote = None

    def setUp(self):
        """Set up client for each test."""
        self.client = Client()

    def test_create_user_success(self):
        user = create_user('test_create', full_name_prefix='Create ')
        self.assertEqual(user.username, 'test_create')
        self.assertEqual(user.email, 'test_create@example.com')
        self.assertEqual(user.full_name, 'Create Test_create')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.role, 'user')
        self.assertFalse(user.is_staff)

    def test_create_user_missing_fields(self):
        with self.assertRaisesRegex(ValueError, 'The Username must be set'):
            CustomUser.objects.create_user(username='', email='t@e.com', full_name='FN')
        with self.assertRaisesRegex(ValueError, 'The Email must be set'):
            CustomUser.objects.create_user(username='u', email='', full_name='FN')
        with self.assertRaisesRegex(ValueError, 'The Full Name must be set'):
            CustomUser.objects.create_user(username='u', email='t@e.com', full_name='')

    def test_create_superuser_success(self):
        admin = self.admin_user
        self.assertEqual(admin.username, 'main_admin')
        self.assertTrue(admin.check_password('password123'))
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_staff)

    def test_create_superuser_invalid_role(self):
        with self.assertRaisesRegex(ValueError, 'Superuser must have role of admin.'):
            CustomUser.objects.create_superuser(
                username='badadmin', email='b@a.com', full_name='BA', role='user'
            )

    def test_create_superuser_is_staff_false(self):
         with self.assertRaisesRegex(ValueError, 'Superuser must have is_staff=True.'):
             CustomUser.objects.create_superuser(
                 username='badadmin2', email='b2@a.com', full_name='BA2', is_staff=False
             )

    def test_custom_user_str(self):
        self.assertEqual(str(self.user), 'main_user')

    def test_custom_user_permissions(self):
        self.assertTrue(self.admin_user.has_perm('any_perm'))
        self.assertTrue(self.admin_user.has_module_perms('any_app'))
        self.assertFalse(self.user.has_perm('any_perm'))
        self.assertFalse(self.user.has_module_perms('any_app'))

    def test_custom_user_creation_form_valid(self):
        form_data = {
            'username': 'newuser',
            'email': 'new@e.com',
            'full_name': 'New User FN',
            'password1': 'ComplexPas$word123',
            'password2': 'ComplexPas$word123'
        }
        form = CustomUserCreationForm(data=form_data)
        if not form.is_valid(): print("Form errors (valid):", form.errors.as_json())
        self.assertTrue(form.is_valid())

    def test_custom_user_creation_form_invalid(self):
        form_data = {'username': 'newuser'}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('full_name', form.errors)
        self.assertIn('password2', form.errors)

    def test_custom_user_creation_form_duplicate_username(self):
        form_data = {
            'username': 'main_user',
            'email': 'new_dup@e.com',
            'full_name': 'New User FN',
            'password1': 'ComplexPas$word123',
            'password2': 'ComplexPas$word123'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_custom_user_creation_form_cleaning(self):
        form_data = {
            'username': '<script>alert("xss")</script>user',
            'email': 'new_clean@e.com',
            'full_name': '<h1>FN Clean</h1>',
            'password1': 'ComplexPas$word123',
            'password2': 'ComplexPas$word123'
        }
        form = CustomUserCreationForm(data=form_data)
        if not form.is_valid(): print("Form errors (cleaning):", form.errors.as_json())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'alert("xss")user')
        self.assertEqual(form.cleaned_data['full_name'], 'FN Clean')

    def test_custom_user_change_form_valid(self):
        form_data = {'full_name': 'Updated Name', 'email': 'updated@e.com', 'profpict': 'http://new.pic'}
        form = CustomUserChangeForm(data=form_data, instance=self.user)
        if not form.is_valid(): print(form.errors.as_json())
        self.assertTrue(form.is_valid())

    def test_custom_user_change_form_invalid_email(self):
        form_data = {'full_name': 'Updated Name', 'email': 'invalid-email'}
        form = CustomUserChangeForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_custom_user_change_form_username_disabled(self):
        form = CustomUserChangeForm(instance=self.user)
        self.assertTrue(form.fields['username'].disabled)
        self.assertEqual(form.fields['username'].initial, self.user.username)

    def test_custom_user_change_form_cleaning(self):
        form_data = {'full_name': '<b>Updated Name</b>', 'email': 'updated_clean@e.com'}
        form = CustomUserChangeForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['full_name'], 'Updated Name')

    def test_register_user_get(self):
        response = self.client.get(reverse('main:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)

    def test_register_user_post_success(self):
        user_count = CustomUser.objects.count()
        form_data = {
            'username': 'register_test', 'email': 'reg@e.com', 'full_name': 'Reg FN',
            'password1': 'ComplexPas$word123',
            'password2': 'ComplexPas$word123'
        }
        response = self.client.post(reverse('main:register'), form_data)
        if response.status_code != 201: print("Register errors:", response.content.decode())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(CustomUser.objects.count(), user_count + 1)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['redirect_url'], reverse('main:login'))

    def test_register_user_post_invalid(self):
        user_count = CustomUser.objects.count()
        form_data = {'username': 'reg_invalid'}
        response = self.client.post(reverse('main:register'), form_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CustomUser.objects.count(), user_count)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.assertIn('full_name', data['errors'])

    def test_login_user_get(self):
        response = self.client.get(reverse('main:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_login_user_post_success(self):
        login_data = {'username': 'main_user', 'password': 'password123'}
        response = self.client.post(reverse('main:login'), login_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['user']['username'], 'main_user')
        self.assertEqual(data['redirect_url'], reverse('main:show_main'))
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.pk)
        self.assertIn('last_login', response.cookies)

    def test_login_user_post_invalid(self):
        login_data = {'username': 'main_user', 'password': 'wrongpassword'}
        response = self.client.post(reverse('main:login'), login_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)
        self.assertIn('__all__', data['errors'])
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertNotIn('last_login', response.cookies)

    def test_logout_user_post(self):
        self.client.login(username='main_user', password='password123')
        self.client.cookies.load({'last_login': 'dummy_time'})
        self.assertIn('_auth_user_id', self.client.session)
        self.assertIn('last_login', self.client.cookies)

        response = self.client.post(reverse('main:logout'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['redirect_url'], reverse('main:login'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertIn('last_login', response.cookies)
        self.assertEqual(response.cookies['last_login']['max-age'], 0)

    def test_logout_user_get_not_allowed(self):
        self.client.login(username='main_user', password='password123')
        response = self.client.get(reverse('main:logout'))
        self.assertEqual(response.status_code, 405)

    def test_show_main_authenticated(self):
        self.client.login(username='main_user', password='password123')
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('statisticsrafi:home'))

    def test_show_main_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('main:show_main'))
        self.assertEqual(response.status_code, 302)
        login_url = reverse('main:login')
        self.assertRedirects(response, reverse('statisticsrafi:home'))

    def test_profile_view_get_authenticated(self):
        self.client.login(username='main_user', password='password123')
        response = self.client.get(reverse('main:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertIsInstance(response.context['edit_form'], CustomUserChangeForm)
        self.assertIn('favorite_clubs', response.context)
        self.assertIn('user_posts', response.context)
        self.assertIn('user_predictions', response.context)
        if FavoriteClub and self.fav_club:
            self.assertEqual(len(response.context['favorite_clubs']), 1)
        if Post and self.post:
            self.assertEqual(len(response.context['user_posts']), 1)
        if Vote and self.vote:
             self.assertEqual(len(response.context['user_predictions']), 1)

    def test_profile_view_get_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('main:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('main:login'), response.url)

    def test_profile_edit_post_success(self):
        self.client.login(username='main_user', password='password123')
        original_full_name = self.user.full_name
        form_data = {'full_name': 'Updated Profile Name', 'email': 'new_profile@e.com', 'profpict': ''}
        response = self.client.post(reverse('main:profile_edit'), form_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, 'Updated Profile Name')
        self.assertEqual(self.user.email, 'new_profile@e.com')
        self.assertEqual(data['user']['full_name'], 'Updated Profile Name')

    def test_profile_edit_post_invalid(self):
        self.client.login(username='main_user', password='password123')
        original_email = self.user.email
        form_data = {'full_name': 'Updated Name', 'email': 'invalid-email'}
        response = self.client.post(reverse('main:profile_edit'), form_data)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)
        self.assertIn('email', data['errors'])
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email)

    def test_profile_edit_get_not_allowed(self):
        self.client.login(username='main_user', password='password123')
        response = self.client.get(reverse('main:profile_edit'))
        self.assertEqual(response.status_code, 405)

    def test_profile_edit_unauthenticated(self):
        self.client.logout()
        response = self.client.post(reverse('main:profile_edit'), {})
        self.assertEqual(response.status_code, 302)