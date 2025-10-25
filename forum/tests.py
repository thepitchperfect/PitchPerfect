
from django.test import TestCase
from django.urls import reverse
from main.models import CustomUser
from club_directories.models import Club, League
from .models import Post, Comment
import json

class ForumModelTests(TestCase):
	def setUp(self):
		self.league = League.objects.create(name="Premier League", region="England")
		self.club = Club.objects.create(name="Chelsea", league=self.league)
		self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", full_name="Test User", password="pass1234")

	def test_post_creation(self):
		post = Post.objects.create(title="Test Post", content="Hello world!", author=self.user)
		post.clubs.add(self.club)
		self.assertEqual(Post.objects.count(), 1)
		self.assertEqual(post.title, "Test Post")
		self.assertIn(self.club, post.clubs.all())

	def test_comment_creation(self):
		post = Post.objects.create(title="Test Post", content="Hello world!", author=self.user)
		comment = Comment.objects.create(post=post, author=self.user, content="Nice post!")
		self.assertEqual(post.comments.count(), 1)
		self.assertEqual(comment.content, "Nice post!")

class ForumViewTests(TestCase):
	def setUp(self):
		self.league = League.objects.create(name="Premier League", region="England")
		self.club = Club.objects.create(name="Chelsea", league=self.league)
		self.user = CustomUser.objects.create_user(username="testuser", email="test@example.com", full_name="Test User", password="pass1234")
		self.post = Post.objects.create(title="Test Post", content="Hello world!", author=self.user)
		self.post.clubs.add(self.club)
		self.admin = CustomUser.objects.create_user(username="adminuser", email="admin@example.com", full_name="Admin User", password="adminpass", is_staff=True)
		self.comment = Comment.objects.create(post=self.post, author=self.user, content="Nice post!")

	def test_get_post_data_authorized(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:get_post_data', args=[self.post.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_get_post_data_unauthorized(self):
		other_user = CustomUser.objects.create_user(username="other", email="other@example.com", full_name="Other", password="otherpass")
		self.client.login(username="other", password="otherpass")
		url = reverse('forum:get_post_data', args=[self.post.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 403)

	def test_create_post_discussion(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:create_post')
		data = {
			"title": "New Discussion",
			"content": "Some content",
			"post_type": "discussion",
			"club_ids": [str(self.club.id)],
			"images": []
		}
		response = self.client.post(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_create_post_news_admin_only(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:create_post')
		data = {
			"title": "News Post",
			"content": "News content",
			"post_type": "news",
			"club_ids": [str(self.club.id)],
			"images": []
		}
		response = self.client.post(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 403)
		self.client.login(username="adminuser", password="adminpass")
		response = self.client.post(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_update_post_authorized(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:update_post', args=[self.post.id])
		data = {"title": "Updated Title", "content": "Updated content", "club_ids": [str(self.club.id)], "images": []}
		response = self.client.put(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_update_post_unauthorized(self):
		other_user = CustomUser.objects.create_user(username="other", email="other@example.com", full_name="Other", password="otherpass")
		self.client.login(username="other", password="otherpass")
		url = reverse('forum:update_post', args=[self.post.id])
		data = {"title": "Updated Title"}
		response = self.client.put(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 403)

	def test_delete_post_authorized(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:delete_post', args=[self.post.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_delete_post_unauthorized(self):
		other_user = CustomUser.objects.create_user(username="other", email="other@example.com", full_name="Other", password="otherpass")
		self.client.login(username="other", password="otherpass")
		url = reverse('forum:delete_post', args=[self.post.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 403)

	def test_create_comment(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:create_comment', args=[self.post.id])
		data = {"content": "New comment"}
		response = self.client.post(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_update_comment_authorized(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:update_comment', args=[self.comment.id])
		data = {"content": "Updated comment"}
		response = self.client.put(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_update_comment_unauthorized(self):
		self.client.login(username="adminuser", password="adminpass")
		url = reverse('forum:update_comment', args=[self.comment.id])
		data = {"content": "Updated comment"}
		response = self.client.put(url, data=json.dumps(data), content_type="application/json")
		self.assertEqual(response.status_code, 403)

	def test_delete_comment_authorized(self):
		self.client.login(username="testuser", password="pass1234")
		url = reverse('forum:delete_comment', args=[self.comment.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json().get('success'))

	def test_delete_comment_unauthorized(self):
		self.client.login(username="adminuser", password="adminpass")
		url = reverse('forum:delete_comment', args=[self.comment.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 200)  # Admin can delete
		# Now try with a random user
		new_comment = Comment.objects.create(post=self.post, author=self.admin, content="Admin comment")
		other_user = CustomUser.objects.create_user(username="other", email="other@example.com", full_name="Other", password="otherpass")
		self.client.login(username="other", password="otherpass")
		url = reverse('forum:delete_comment', args=[new_comment.id])
		response = self.client.delete(url)
		self.assertEqual(response.status_code, 403)

	def test_forum_home_view(self):
		url = reverse('forum:forum_home')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Test Post")

	def test_post_detail_view(self):
		url = reverse('forum:post_detail', args=[self.post.id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, self.post.title)

	def test_filter_by_club(self):
		url = reverse('forum:forum_home') + f'?clubs={self.club.id}'
		response = self.client.get(url)
		self.assertContains(response, self.post.title)

	def test_create_post_permission(self):
		url = reverse('forum:forum_home')
		response = self.client.get(url)
		self.assertContains(response, "Login")
