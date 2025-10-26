import json
import uuid
from datetime import timedelta
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.utils import timezone
from django.db.utils import IntegrityError
from django.core.paginator import Page
from main.models import CustomUser # Direct import
from club_directories.models import Club, League, LeaguePick # Import dependent models
from .models import Post, PostImage, Comment
from .forms import PostForm
from . import views # Import views to test URL resolution

# Helper function to create users easily
def create_user(username, password='password123', is_staff=False, email_suffix='@example.com', full_name_prefix='Test '):
    return CustomUser.objects.create_user(
        username=username, 
        password=password,
        email=f'{username}{email_suffix}',
        full_name=f'{full_name_prefix}{username.capitalize()}',
        is_staff=is_staff
    )

class ForumTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        # Users
        cls.user = create_user('forum_user')
        cls.staff_user = create_user('forum_staff', is_staff=True)
        cls.other_user = create_user('forum_other')

        # Leagues and Clubs
        cls.league1 = League.objects.create(name="Forum League 1", region="Region 1")
        cls.league2 = League.objects.create(name="Forum League 2", region="Region 2")
        cls.club1 = Club.objects.create(league=cls.league1, name="Forum Club 1")
        cls.club2 = Club.objects.create(league=cls.league1, name="Forum Club 2")
        cls.club3 = Club.objects.create(league=cls.league2, name="Forum Club 3")

        # Posts
        now = timezone.now()
        cls.post_discuss1 = Post.objects.create(
            author=cls.user, title="Discussion Post 1", content="Content 1", post_type='discussion', created_at=now - timedelta(days=2)
        )
        cls.post_discuss2 = Post.objects.create(
            author=cls.other_user, title="Discussion Post 2 Searchable", content="More content here", post_type='discussion', created_at=now - timedelta(days=1)
        )
        cls.post_news1 = Post.objects.create(
            author=cls.staff_user, title="News Post 1", content="Official news content", post_type='news', created_at=now
        )
        # Add clubs to posts
        cls.post_discuss1.clubs.add(cls.club1, cls.club2)
        cls.post_news1.clubs.add(cls.club3)

        # Post Images
        cls.image1 = PostImage.objects.create(post=cls.post_news1, image_url="http://example.com/image1.jpg", caption="Caption 1", order=1)
        cls.image2 = PostImage.objects.create(post=cls.post_news1, image_url="http://example.com/image2.jpg", order=0) # Test ordering

        # Comments
        cls.comment1 = Comment.objects.create(post=cls.post_discuss1, author=cls.other_user, content="First comment")
        cls.comment2 = Comment.objects.create(post=cls.post_discuss1, author=cls.user, content="Reply comment", created_at=now - timedelta(hours=1))

    def setUp(self):
        """Set up things that might change between tests (like client)."""
        self.client = Client()
        # Log in the main test user by default
        self.client.login(username='forum_user', password='password123')


    # Model Tests
    def test_post_str(self):
        self.assertEqual(str(self.post_discuss1), "[Discussion] Discussion Post 1")
        self.assertEqual(str(self.post_news1), "[Official News] News Post 1")

    def test_post_ordering(self):
        posts = list(Post.objects.all())
        # News should come first, then discussions ordered by creation date DESC
        self.assertEqual(posts[0], self.post_news1)
        self.assertEqual(posts[1], self.post_discuss2)
        self.assertEqual(posts[2], self.post_discuss1)

    def test_post_get_clubs_list(self):
        self.assertListEqual(self.post_discuss1.get_clubs_list(), [self.club1, self.club2])
        self.assertListEqual(self.post_discuss2.get_clubs_list(), [])

    def test_post_is_official_news(self):
        self.assertTrue(self.post_news1.is_official_news())
        self.assertFalse(self.post_discuss1.is_official_news())

    def test_post_image_str(self):
        self.assertEqual(str(self.image1), f"Image for {self.post_news1.title}")

    def test_post_image_ordering(self):
        images = list(self.post_news1.images.all())
        self.assertEqual(images[0], self.image2) # Order 0 comes first
        self.assertEqual(images[1], self.image1) # Order 1 comes second

    def test_comment_str(self):
        self.assertEqual(str(self.comment1), f'Comment by {self.other_user.username} on {self.post_discuss1.title}')

    def test_comment_ordering(self):
        comments = list(self.post_discuss1.comments.all())
        self.assertEqual(comments[0], self.comment1) # Created later but set earlier time in setUpTestData
        self.assertEqual(comments[1], self.comment2)



    # Form Tests 
    def test_post_form_valid(self):
        form_data = {'title': 'Valid Title', 'post_type': 'discussion', 'content': 'Valid content'}
        form = PostForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_post_form_invalid_missing_fields(self):
        form_data = {'title': 'Valid Title'} # Missing content and post_type
        form = PostForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)
        self.assertIn('post_type', form.errors)
        
    def test_post_form_post_type_choices_regular_user(self):
        form = PostForm(user=self.user)
        # Regular user should only see 'discussion'
        self.assertEqual(len(form.fields['post_type'].choices), 1)
        self.assertEqual(form.fields['post_type'].choices[0], ('discussion', 'Discussion'))

    def test_post_form_post_type_choices_staff_user(self):
        form = PostForm(user=self.staff_user)
        # Staff user should see both options
        self.assertEqual(len(form.fields['post_type'].choices), 2)
        self.assertIn(('news', 'Official News'), form.fields['post_type'].choices)
        self.assertIn(('discussion', 'Discussion'), form.fields['post_type'].choices)


    # URL Tests
    def test_urls_resolve(self):
        self.assertEqual(resolve(reverse('forum:forum_home')).func, views.forum_home)
        self.assertEqual(resolve(reverse('forum:post_detail', args=[self.post_discuss1.pk])).func, views.post_detail)
        # Assuming main.views.login_user is correctly imported
        # self.assertEqual(resolve(reverse('forum:login')).func.__name__, 'login_user') 
        self.assertEqual(resolve(reverse('forum:create_post')).func, views.create_post)
        self.assertEqual(resolve(reverse('forum:get_post_data', args=[self.post_discuss1.pk])).func, views.get_post_data)
        self.assertEqual(resolve(reverse('forum:update_post', args=[self.post_discuss1.pk])).func, views.update_post)
        self.assertEqual(resolve(reverse('forum:delete_post', args=[self.post_discuss1.pk])).func, views.delete_post)
        self.assertEqual(resolve(reverse('forum:create_comment', args=[self.post_discuss1.pk])).func, views.create_comment)
        self.assertEqual(resolve(reverse('forum:update_comment', args=[self.comment1.pk])).func, views.update_comment)
        self.assertEqual(resolve(reverse('forum:delete_comment', args=[self.comment1.pk])).func, views.delete_comment)


    # View Tests - GET Requests
    def test_forum_home_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('forum:forum_home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/home.html')
        self.assertIn('news_posts', response.context)
        self.assertIn('page_obj', response.context)
        self.assertIsInstance(response.context['page_obj'], Page)
        self.assertIn('user_favorite_clubs', response.context)
        self.assertEqual(response.context['user_favorite_clubs'], [])

    def test_forum_home_view_authenticated(self):
        # Logged in via setUp
        LeaguePick.objects.create(user=self.user, league=self.club1.league, club=self.club1) # Add a favorite club
        response = self.client.get(reverse('forum:forum_home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_favorite_clubs', response.context)
        self.assertEqual(len(response.context['user_favorite_clubs']), 1)
        self.assertEqual(response.context['user_favorite_clubs'][0], self.club1)
        self.assertIn('form', response.context) # Post form should be present
        self.assertIsInstance(response.context['form'], PostForm)
        
    def test_forum_home_filtering(self):
        # Filter by club1
        response = self.client.get(reverse('forum:forum_home'), {'clubs': self.club1.id})
        self.assertEqual(response.status_code, 200)
        # News filtered separately
        self.assertEqual(len(response.context['news_posts']), 0) 
        # Discussions filtered in page_obj
        page_obj = response.context['page_obj']
        self.assertEqual(page_obj.paginator.count, 1)
        self.assertEqual(page_obj.object_list[0], self.post_discuss1)
        self.assertEqual(response.context['current_filters']['clubs'], [str(self.club1.id)])

        # Filter by league2
        response = self.client.get(reverse('forum:forum_home'), {'league': self.league2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['news_posts']), 1) # News post is in league 2 via club3
        self.assertEqual(response.context['news_posts'][0], self.post_news1)
        self.assertEqual(response.context['page_obj'].paginator.count, 0) # No discussions in league 2
        self.assertEqual(response.context['current_filters']['league'], str(self.league2.id))

        # Filter by search term
        response = self.client.get(reverse('forum:forum_home'), {'search': 'Searchable'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['news_posts']), 0) 
        self.assertEqual(response.context['page_obj'].paginator.count, 1)
        self.assertEqual(response.context['page_obj'].object_list[0], self.post_discuss2)
        self.assertEqual(response.context['current_filters']['search'], 'Searchable')

    def test_post_detail_view(self):
        response = self.client.get(reverse('forum:post_detail', args=[self.post_discuss1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'forum/post_detail.html')
        self.assertEqual(response.context['post'], self.post_discuss1)
        self.assertListEqual(list(response.context['comments']), [self.comment1, self.comment2]) # Check ordering

    def test_post_detail_404(self):
        response = self.client.get(reverse('forum:post_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_get_post_data_success(self):
        response = self.client.get(reverse('forum:get_post_data', args=[self.post_discuss1.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['post']['id'], self.post_discuss1.pk)
        self.assertEqual(data['post']['title'], self.post_discuss1.title)
        self.assertListEqual(data['post']['club_ids'], [str(self.club1.id), str(self.club2.id)])
        self.assertEqual(len(data['post']['images']), 0)
        
    def test_get_post_data_with_images(self):
        # Log in as staff to fetch news post data
        self.client.login(username='forum_staff', password='password123')
        response = self.client.get(reverse('forum:get_post_data', args=[self.post_news1.pk]))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['post']['images']), 2)
        # Check image order from model meta
        self.assertEqual(data['post']['images'][0]['url'], self.image2.image_url) # order=0
        self.assertEqual(data['post']['images'][1]['url'], self.image1.image_url) # order=1
        
    def test_get_post_data_unauthorized(self):
        # self.user tries to get other_user's post data
        response = self.client.get(reverse('forum:get_post_data', args=[self.post_discuss2.pk]))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Unauthorized')

    def test_get_post_data_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('forum:get_post_data', args=[self.post_discuss1.pk]))
        self.assertEqual(response.status_code, 302) # Redirect to login

    def test_get_post_data_404(self):
        response = self.client.get(reverse('forum:get_post_data', args=[9999]))
        self.assertEqual(response.status_code, 404)


    # View Tests - POST / AJAX Requests
    def test_create_post_success(self):
        post_count = Post.objects.count()
        post_data = {
            'title': 'New Post Title',
            'content': 'New post content.',
            'post_type': 'discussion',
            'clubs': [self.club1.id],
            'image_urls': ['http://example.com/new1.jpg', ''], # Test empty URL
            'image_captions': ['New Caption 1', 'Should be ignored']
        }
        response = self.client.post(reverse('forum:create_post'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(new_post.title, 'New Post Title')
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.clubs.count(), 1)
        self.assertEqual(new_post.images.count(), 1)
        self.assertEqual(new_post.images.first().image_url, 'http://example.com/new1.jpg')
        self.assertEqual(new_post.images.first().caption, 'New Caption 1')

    def test_create_post_news_by_staff(self):
        self.client.login(username='forum_staff', password='password123')
        post_count = Post.objects.count()
        post_data = {'title': 'Staff News', 'content': 'Important', 'post_type': 'news'}
        response = self.client.post(reverse('forum:create_post'), post_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.latest('created_at')
        self.assertEqual(new_post.post_type, 'news')
        self.assertEqual(new_post.author, self.staff_user)

# forum/tests.py
    def test_create_post_news_by_regular_user_forbidden(self):
        # self.user is logged in (non-staff)
        post_count = Post.objects.count()
        post_data = {'title': 'Fake News', 'content': 'Not allowed', 'post_type': 'news'}
        response = self.client.post(reverse('forum:create_post'), post_data)
        self.assertEqual(response.status_code, 400) 
        self.assertFalse(response.json()['success'])
        self.assertIn('errors', response.json())
        self.assertIn('post_type', response.json().get('errors', {})) 
        self.assertEqual(Post.objects.count(), post_count) # No post created

    def test_create_post_invalid_form(self):
        post_count = Post.objects.count()
        post_data = {'title': 'Missing content'} # Invalid form data
        response = self.client.post(reverse('forum:create_post'), post_data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertIn('errors', response.json())
        self.assertEqual(Post.objects.count(), post_count)

    def test_create_post_too_many_clubs(self):
        post_count = Post.objects.count()
        post_data = {
            'title': 'Too many tags', 'content': 'Valid content', 'post_type': 'discussion',
            'clubs': [self.club1.id, self.club2.id, self.club3.id, uuid.uuid4()] # 4 clubs
        }
        response = self.client.post(reverse('forum:create_post'), post_data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Max 3 clubs allowed')
        self.assertEqual(Post.objects.count(), post_count)

    def test_create_post_invalid_method(self):
        response = self.client.get(reverse('forum:create_post'))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Invalid method')
        
    def test_delete_post_success(self):
        # self.user deletes their own post (post_discuss1)
        post_count = Post.objects.count()
        url = reverse('forum:delete_post', args=[self.post_discuss1.pk])
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Post.objects.count(), post_count - 1)
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(pk=self.post_discuss1.pk)

    def test_delete_post_by_staff(self):
        # Staff deletes other_user's post (post_discuss2)
        self.client.login(username='forum_staff', password='password123')
        post_count = Post.objects.count()
        url = reverse('forum:delete_post', args=[self.post_discuss2.pk])
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Post.objects.count(), post_count - 1)

    def test_delete_post_unauthorized(self):
        # self.user tries to delete other_user's post (post_discuss2)
        post_count = Post.objects.count()
        url = reverse('forum:delete_post', args=[self.post_discuss2.pk])
        response = self.client.delete(url, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['error'], 'Unauthorized')
        self.assertEqual(Post.objects.count(), post_count)

    def test_delete_post_invalid_method(self):
        url = reverse('forum:delete_post', args=[self.post_discuss1.pk])
        response = self.client.post(url) # Should be DELETE
        self.assertEqual(response.status_code, 405) # Method Not Allowed

    def test_create_comment_success(self):
        comment_count = Comment.objects.filter(post=self.post_discuss2).count()
        url = reverse('forum:create_comment', args=[self.post_discuss2.pk])
        data = json.dumps({'content': 'New comment'})
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Comment.objects.filter(post=self.post_discuss2).count(), comment_count + 1)
        new_comment = Comment.objects.latest('created_at')
        self.assertEqual(new_comment.content, 'New comment')
        self.assertEqual(new_comment.author, self.user)
        self.assertEqual(response.json()['comment']['content'], 'New comment')
        self.assertEqual(response.json()['comment']['author'], self.user.username)

    def test_create_comment_invalid_post(self):
        url = reverse('forum:create_comment', args=[9999])
        data = json.dumps({'content': 'New comment'})
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_create_comment_invalid_data(self):
        url = reverse('forum:create_comment', args=[self.post_discuss2.pk])
        data = json.dumps({'wrong_field': 'New comment'}) # Missing 'content'
        response = self.client.post(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])

    def test_update_comment_success(self):
        # self.user updates their own comment (comment2)
        url = reverse('forum:update_comment', args=[self.comment2.pk])
        data = json.dumps({'content': 'Updated comment content'})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.comment2.refresh_from_db()
        self.assertEqual(self.comment2.content, 'Updated comment content')
        self.assertEqual(response.json()['comment']['content'], 'Updated comment content')
        
    def test_update_comment_unauthorized(self):
        # self.user tries to update other_user's comment (comment1)
        url = reverse('forum:update_comment', args=[self.comment1.pk])
        data = json.dumps({'content': 'Updated comment content'})
        response = self.client.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])
        self.comment1.refresh_from_db()
        self.assertNotEqual(self.comment1.content, 'Updated comment content')

    def test_delete_comment_success(self):
        # self.user deletes their own comment (comment2)
        comment_count = Comment.objects.count()
        url = reverse('forum:delete_comment', args=[self.comment2.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Comment.objects.count(), comment_count - 1)
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(pk=self.comment2.pk)

    def test_delete_comment_by_staff(self):
        # Staff deletes other_user's comment (comment1)
        self.client.login(username='forum_staff', password='password123')
        comment_count = Comment.objects.count()
        url = reverse('forum:delete_comment', args=[self.comment1.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(Comment.objects.count(), comment_count - 1)
        
    def test_delete_comment_unauthorized(self):
        # self.user tries to delete other_user's comment (comment1)
        comment_count = Comment.objects.count()
        url = reverse('forum:delete_comment', args=[self.comment1.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json()['success'])
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_update_post_basic_checks(self):
        url = reverse('forum:update_post', args=[self.post_discuss1.pk])
        # Check invalid method
        response_get = self.client.get(url)
        self.assertEqual(response_get.status_code, 400)
        # Check unauthorized
        response_unauth = self.client.post(reverse('forum:update_post', args=[self.post_discuss2.pk])) # Try to update other user's post
        self.assertEqual(response_unauth.status_code, 403)
        # Check basic success possibility (doesn't test actual data change well)
        response_post = self.client.post(url, {'title': 'Updated Title'}) 
        self.assertEqual(response_post.status_code, 200)
        self.assertTrue(response_post.json()['success'])
        self.post_discuss1.refresh_from_db()
        self.assertEqual(self.post_discuss1.title, 'Updated Title') # Verify basic title update worked