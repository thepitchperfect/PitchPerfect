from django.db import models
from main.models import CustomUser
from club_directories.models import Club, League 

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ('discussion', 'Discussion'),
        ('news', 'Official News'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='forum_posts')
    post_type = models.CharField(
        max_length=20, 
        choices=POST_TYPE_CHOICES, 
        default='discussion',
        help_text='Only admins can post Official News'
    )
    
    clubs = models.ManyToManyField(
        Club,
        blank=True,
        related_name='tagged_posts',
        help_text='Tag clubs (can select multiple)'
    )
    
    # Remove hashtag fields - we'll use clubs ManyToMany for filtering
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-post_type', '-created_at']  # News first, then by date
        indexes = [
            models.Index(fields=['-post_type', '-created_at']),
            models.Index(fields=['post_type']),
        ]

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title}"
    
    def get_league(self):
        """Helper method to get league from clubs or direct league tag"""
        if self.league:
            return self.league
        # Get league from first club if exists
        first_club = self.clubs.first()
        return first_club.league if first_club else None
    
    def get_clubs_list(self):
        """Return list of tagged clubs"""
        return list(self.clubs.all())
    
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
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='forum_comments')
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