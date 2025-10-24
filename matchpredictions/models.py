from django.db import models
from django.conf import settings
import uuid


# 🏆 League Model
class League(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=100)
    logo_path = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


# ⚽ Club Model
class Club(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, related_name="clubs")
    logo_url = models.URLField(blank=True, null=True, max_length=500)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


# 🎯 Match Model
class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)
    home_team = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='away_matches')
    match_date = models.DateTimeField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('upcoming', 'Upcoming'),
            ('ongoing', 'Ongoing'),
            ('finished', 'Finished'),
        ],
        default='upcoming'
    )

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.league.name})"

    @property
    def total_votes(self):
        return self.votes.count()

    @property
    def vote_summary(self):
        total = self.votes.count()
        if total == 0:
            return {"home_win": 0, "away_win": 0, "draw": 0}
        return {
            "home_win": round((self.votes.filter(prediction='home_win').count() / total) * 100, 1),
            "away_win": round((self.votes.filter(prediction='away_win').count() / total) * 100, 1),
            "draw": round((self.votes.filter(prediction='draw').count() / total) * 100, 1),
        }


# 🗳️ Vote Model
class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='votes')
    prediction = models.CharField(
        max_length=10,
        choices=[
            ('home_win', 'Home Win'),
            ('away_win', 'Away Win'),
            ('draw', 'Draw'),
        ]
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'match')

    def __str__(self):
        return f"{self.user.username} → {self.match} ({self.prediction})"
