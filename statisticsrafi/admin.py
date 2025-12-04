from django.contrib import admin
from .models import (
    Award,
    Vote, ClubRanking, TeamStatistics, ClubVote
)
from club_directories.models import Club, League

@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ['name', 'league', 'founded_year']
    list_filter = ['league']
    search_fields = ['name', 'league__name']

@admin.register(Award)
class AwardAdmin(admin.ModelAdmin):
    list_display = ['title', 'club', 'award_type', 'season', 'date_awarded']
    list_filter = ['award_type', 'season']
    search_fields = ['club__name', 'title']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'club', 'season', 'voted_at']
    list_filter = ['category', 'season']
    search_fields = ['user__username', 'club__name']

@admin.register(ClubRanking)
class ClubRankingAdmin(admin.ModelAdmin):
    list_display = ['rank', 'club', 'points', 'continent', 'ranking_date']
    list_filter = ['continent', 'ranking_date']
    search_fields = ['club__name']
    ordering = ['rank']

@admin.register(TeamStatistics)
class TeamStatisticsAdmin(admin.ModelAdmin):
    list_display = ['club', 'season', 'wins', 'draws', 'losses', 'possession_avg', 'scored_per_match']
    list_filter = ['season', 'club__league']
    search_fields = ['club__name']
    ordering = ['club__name']

@admin.register(ClubVote)
class ClubVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'club', 'season', 'created_at']
    list_filter = ['season', 'created_at']
    search_fields = ['user__username', 'club__name']
    ordering = ['-created_at']
