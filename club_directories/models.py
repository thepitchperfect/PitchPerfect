from django.db import models
from django.contrib.auth.models import User 
import uuid

class League(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=100)
    logo_path = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="clubs")
    founded_year = models.IntegerField(null=True, blank=True)
    logo_url = models.URLField(blank=True, null=True, max_length=500) 
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class FavoriteClub(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorite_clubs")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="favorited_by")
    
    class Meta:
        unique_together = ('user', 'club')

    def __str__(self):
        return f"{self.user.username}'s favorite: {self.club.name}"

