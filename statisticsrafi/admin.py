from django.contrib import admin
from .models import (
    Club, Player, PlayerStatistics, Award,
    UserWatchlist, Vote, PlayerComparison, ClubRanking
)

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'league', 'fifa_ranking']
    list_filter = ['country', 'league']
    search_fields = ['name', 'country']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'club', 'position', 'nationality', 'jersey_number']
    list_filter = ['position', 'club', 'nationality']
    search_fields = ['name', 'club__name']

@admin.register(PlayerStatistics)
class PlayerStatisticsAdmin(admin.ModelAdmin):
    list_display = ['player', 'season', 'goals', 'assists', 'clean_sheets', 'appearances']
    list_filter = ['season', 'player__position']
    search_fields = ['player__name']
    ordering = ['-season', '-goals']

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['title', 'player', 'club', 'award_type', 'season', 'date_awarded']
    list_filter = ['award_type', 'season']
    search_fields = ['player__name', 'club__name', 'title']

@admin.register(UserWatchlist)
class UserWatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'player', 'added_date']
    list_filter = ['added_date']
    search_fields = ['user__username', 'player__name']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'player', 'club', 'season', 'voted_at']
    list_filter = ['category', 'season']
    search_fields = ['user__username', 'player__name', 'club__name']

@admin.register(PlayerComparison)
class PlayerComparisonAdmin(admin.ModelAdmin):
    list_display = ['user', 'player1', 'player2', 'season', 'compared_at']
    list_filter = ['season', 'compared_at']
    search_fields = ['user__username', 'player1__name', 'player2__name']

@admin.register(ClubRanking)
class ClubRankingAdmin(admin.ModelAdmin):
    list_display = ['rank', 'club', 'points', 'continent', 'ranking_date']
    list_filter = ['continent', 'ranking_date']
    search_fields = ['club__name']
    ordering = ['rank']
