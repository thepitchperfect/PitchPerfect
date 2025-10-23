from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Club(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    league = models.CharField(max_length=200)
    logo_url = models.URLField(blank=True, null=True)
    founded_year = models.IntegerField(null=True, blank=True)
    stadium = models.CharField(max_length=200, blank=True)
    fifa_ranking = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class League(models.Model):
    name = models.CharField(max_length=255, unique=True)
    region = models.CharField(max_length=100)
    logo_path = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name

class Player(models.Model):
    """Football Player"""
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]
    
    name = models.CharField(max_length=200)
    club = models.ForeignKey(Club, on_delete=models.SET_NULL, null=True, related_name='players')
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    nationality = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    height = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, help_text="Height in meters")
    market_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Market value in millions")
    jersey_number = models.IntegerField(null=True, blank=True)
    photo_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.club})"
    
    class Meta:
        ordering = ['name']


class PlayerStatistics(models.Model):
    """Season statistics for a player"""
    SEASON_CHOICES = [
        ('2023/24', '2023/24'),
        ('2024/25', '2024/25'),
        ('2025/26', '2025/26'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='statistics')
    season = models.CharField(max_length=10, choices=SEASON_CHOICES)
    
    # Match Stats
    appearances = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    minutes_played = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Offensive Stats
    goals = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    assists = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    shots = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    shots_on_target = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Defensive Stats (for GK and defenders mainly)
    clean_sheets = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    tackles = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    interceptions = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Discipline
    yellow_cards = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    red_cards = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # Performance Rating
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.player.name} - {self.season}"
    
    class Meta:
        unique_together = ['player', 'season']
        ordering = ['-season', '-goals']
        verbose_name_plural = "Player Statistics"


class Award(models.Model):
    """Player Awards and Achievements"""
    AWARD_TYPES = [
        ('POTY', 'Player of the Year'),
        ('POTM', 'Player of the Month'),
        ('POTW', 'Player of the Week'),
        ('GOLDEN_BOOT', 'Golden Boot'),
        ('GOLDEN_GLOVE', 'Golden Glove'),
        ('TEAM_OTY', 'Team of the Year'),
        ('TEAM_POTM', 'Team of the Month'),
        ('TEAM_POTW', 'Team of the Week'),
        ('OTHER', 'Other Award'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='awards', null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='awards', null=True, blank=True)
    award_type = models.CharField(max_length=20, choices=AWARD_TYPES)
    title = models.CharField(max_length=200)
    season = models.CharField(max_length=10)
    date_awarded = models.DateField()
    description = models.TextField(blank=True)
    
    def __str__(self):
        if self.player:
            return f"{self.player.name} - {self.title} ({self.season})"
        return f"{self.club.name} - {self.title} ({self.season})"
    
    class Meta:
        ordering = ['-date_awarded']


class UserWatchlist(models.Model):
    """User's favorite players watchlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='watched_by')
    added_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Personal notes about the player")
    
    def __str__(self):
        return f"{self.user.username} - {self.player.name}"
    
    class Meta:
        unique_together = ['user', 'player']
        ordering = ['-added_date']


class Vote(models.Model):
    """User votes for Player/Team of the Week/Month/Season"""
    VOTE_CATEGORY = [
        ('PLAYER_WEEK', 'Player of the Week'),
        ('PLAYER_MONTH', 'Player of the Month'),
        ('PLAYER_SEASON', 'Player of the Season'),
        ('TEAM_WEEK', 'Team of the Week'),
        ('TEAM_MONTH', 'Team of the Month'),
        ('TEAM_SEASON', 'Team of the Season'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    category = models.CharField(max_length=20, choices=VOTE_CATEGORY)
    season = models.CharField(max_length=10)
    week_number = models.IntegerField(null=True, blank=True, help_text="Week number for weekly votes")
    month_number = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(12)], help_text="Month number for monthly votes")
    voted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        target = self.player.name if self.player else self.club.name
        return f"{self.user.username} voted {target} for {self.category}"
    
    class Meta:
        unique_together = ['user', 'category', 'season', 'week_number', 'month_number']
        ordering = ['-voted_at']


class PlayerComparison(models.Model):
    """Store user's player comparisons for history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comparisons')
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='comparison_player1')
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='comparison_player2')
    season = models.CharField(max_length=10)
    compared_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player1.name} vs {self.player2.name} ({self.season})"
    
    class Meta:
        ordering = ['-compared_at']


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