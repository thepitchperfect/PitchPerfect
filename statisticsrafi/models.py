from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from club_directories.models import Club, League

User = get_user_model()

    
    
    
class Award(models.Model):
    """Player Awards and Achievements"""
    AWARD_TYPES = [
        ('TEAM_OTY', 'Team of the Year'),
        ('TEAM_POTM', 'Team of the Month'),
        ('TEAM_POTW', 'Team of the Week'),
        ('OTHER', 'Other Award'),
    ]
    
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='awards', null=True, blank=True)
    award_type = models.CharField(max_length=20, choices=AWARD_TYPES)
    title = models.CharField(max_length=200)
    season = models.CharField(max_length=10)
    date_awarded = models.DateField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        club_name = self.club.name if self.club else "No Club"
        return f"{club_name} - {self.title} ({self.season})"
    
    class Meta:
        ordering = ['-date_awarded']


class Vote(models.Model):
    """User votes for Player/Team of the Week/Month/Season"""
    VOTE_CATEGORY = [
        ('TEAM_WEEK', 'Team of the Week'),
        ('TEAM_MONTH', 'Team of the Month'),
        ('TEAM_SEASON', 'Team of the Season'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    category = models.CharField(max_length=20, choices=VOTE_CATEGORY)
    season = models.CharField(max_length=10)
    week_number = models.IntegerField(null=True, blank=True, help_text="Week number for weekly votes")
    month_number = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)], help_text="Month number for monthly votes")
    voted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        target = self.club.name if self.club else "No Club"
        return f"{self.user.username} voted {target} for {self.category}"
    
    class Meta:
        unique_together = ['user', 'category', 'season', 'week_number', 'month_number']
        ordering = ['-voted_at']




class ClubRanking(models.Model):
    """FIFA Club World Rankings"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='rankings')
    rank = models.IntegerField(validators=[MinValueValidator(1)])
    points = models.DecimalField(max_digits=10, decimal_places=2)
    continent = models.CharField(max_length=50)
    ranking_date = models.DateField()
    previous_rank = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.club.name} - Rank {self.rank} ({self.ranking_date})"
    
    class Meta:
        ordering = ['rank']
        unique_together = ['club', 'ranking_date']


class TeamStatistics(models.Model):
    """Team/Club Statistics for a season"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='team_statistics')
    season = models.CharField(max_length=10, default='2025/26')
    
    # Match Results
    wins = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    draws = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    losses = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # xG Stats
    xg_for_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Expected Goals For per Match")
    xg_against_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Expected Goals Against per Match")
    
    # Goals
    scored_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Goals Scored per Match")
    conceded_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Goals Conceded per Match")
    avg_match_goals = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Average Match Goals")
    
    # Clean Sheets & Scoring
    clean_sheets_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Clean Sheets %")
    failed_to_score_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Failed to Score %")
    
    # Possession & Shots
    possession_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Average Possession %")
    shots_taken_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Shots Taken per Match")
    shots_conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Shots Conversion Rate %")
    
    # Fouls
    fouls_committed_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fouls Committed per Match")
    fouled_against_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Fouled Against per Match")
    
    # Penalties
    penalties_won = models.CharField(max_length=20, blank=True, help_text="Penalties Won (e.g., '2 in 8')")
    penalties_conceded = models.CharField(max_length=20, blank=True, help_text="Penalties Conceded (e.g., '0 in 8')")
    
    # Set Pieces
    goal_kicks_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Goal Kicks per Match")
    throw_ins_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Throw-ins per Match")
    free_kicks_per_match = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Free-Kicks per Match")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.club.name} - {self.season} Statistics"
    
    @property
    def matches_played(self):
        return self.wins + self.draws + self.losses
    
    @property
    def win_percentage(self):
        total = self.matches_played
        if total > 0:
            return round((self.wins / total) * 100, 1)
        return 0
    
    class Meta:
        unique_together = ['club', 'season']
        ordering = ['-season', 'club__name']
        verbose_name_plural = "Team Statistics"


class ClubVote(models.Model):
    """Vote for Club of the Season"""
    SEASON_CHOICES = [
        ('2023/24', '2023/24'),
        ('2024/25', '2024/25'),
        ('2025/26', '2025/26'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_votes')
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='club_votes')
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, default='2025/26')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} voted for {self.club.name} ({self.season})"
    
    class Meta:
        unique_together = ['user', 'season']  # One vote per user per season
        ordering = ['-created_at']