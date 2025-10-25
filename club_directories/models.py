from django.db import models
from main.models import CustomUser
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
    
class ClubDetails(models.Model):
    club = models.OneToOneField(
        Club, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        related_name="details"
    )
    
    description = models.TextField(blank=True, null=True)
    history_summary = models.TextField(blank=True, null=True)
    stadium_name = models.CharField(max_length=255, blank=True, null=True)
    stadium_capacity = models.IntegerField(blank=True, null=True)
    manager_name = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"Details for {self.club.name}"

class LeaguePick(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="league_picks")
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="picks_for_league")
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="picked_in_leagues")
    
    class Meta:
        unique_together = ('user', 'league')

    def __str__(self):
        return f"{self.user.username}'s pick for {self.league.name}: {self.club.name}"