from django.db import models
from django.contrib.auth.models import User
from club_directories.models import Club, League  

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('discussion', 'Discussion'),
        ('news', 'Official News'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    post_type = models.CharField(
        max_length=20, 
        choices=POST_TYPE_CHOICES, 
        default='discussion',
        help_text='Only admins can post Official News'
    )
    
    # Optional club tag
    club = models.ForeignKey(
        Club, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='forum_posts',
        help_text='Tag a club (optional)'
    )
    
    # Hashtags for filtering (stored as comma-separated or use TaggableManager)
    league_tags = models.CharField(
        max_length=500, 
        blank=True,
        help_text='League hashtags (comma-separated, e.g., #PremierLeague, #LaLiga)'
    )
    club_tags = models.CharField(
        max_length=500, 
        blank=True,
        help_text='Club hashtags (comma-separated, e.g., #ManchesterUnited, #Barcelona)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['club']),
            models.Index(fields=['post_type']),
        ]

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title}"
    
    def get_league(self):
        """Helper method to get league from club or direct league tag"""
        if self.league:
            return self.league
        return self.club.league if self.club else None
    
    def get_league_tags_list(self):
        """Return league tags as a list"""
        return [tag.strip() for tag in self.league_tags.split(',') if tag.strip()]
    
    def get_club_tags_list(self):
        """Return club tags as a list"""
        return [tag.strip() for tag in self.club_tags.split(',') if tag.strip()]
    
    def is_official_news(self):
        """Check if post is official news"""
        return self.post_type == 'news'


class PostImage(models.Model):
    """Model to store multiple images per post"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0, help_text='Display order of images')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']
        indexes = [
            models.Index(fields=['post', 'order']),
        ]

    def __str__(self):
        return f"Image for {self.post.title}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
        ]

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'