from django.core.management.base import BaseCommand
from statisticsrafi.models import Club, ClubRanking
from datetime import date

# Top 50 clubs with their FIFA rankings
RANKINGS_DATA = [
    {"club_name": "Manchester City", "rank": 1, "points": 2077.5, "continent": "Europe"},
    {"club_name": "Real Madrid", "rank": 2, "points": 2014.0, "continent": "Europe"},
    {"club_name": "FC Bayern München", "rank": 3, "points": 1989.0, "continent": "Europe"},
    {"club_name": "Liverpool", "rank": 4, "points": 1956.5, "continent": "Europe"},
    {"club_name": "FC Barcelona", "rank": 5, "points": 1923.0, "continent": "Europe"},
    {"club_name": "Paris Saint-Germain", "rank": 6, "points": 1891.0, "continent": "Europe"},
    {"club_name": "Chelsea", "rank": 7, "points": 1867.5, "continent": "Europe"},
    {"club_name": "Inter Milan", "rank": 8, "points": 1845.0, "continent": "Europe"},
    {"club_name": "Atletico Madrid", "rank": 9, "points": 1821.5, "continent": "Europe"},
    {"club_name": "Manchester United", "rank": 10, "points": 1798.0, "continent": "Europe"},
    {"club_name": "Borussia Dortmund", "rank": 11, "points": 1775.5, "continent": "Europe"},
    {"club_name": "Juventus FC", "rank": 12, "points": 1752.0, "continent": "Europe"},
    {"club_name": "Arsenal", "rank": 13, "points": 1729.5, "continent": "Europe"},
    {"club_name": "Napoli", "rank": 14, "points": 1706.0, "continent": "Europe"},
    {"club_name": "Tottenham Hotspur", "rank": 15, "points": 1682.5, "continent": "Europe"},
    {"club_name": "AC Milan", "rank": 16, "points": 1659.0, "continent": "Europe"},
    {"club_name": "RB Leipzig", "rank": 17, "points": 1635.5, "continent": "Europe"},
    {"club_name": "Sevilla FC", "rank": 18, "points": 1612.0, "continent": "Europe"},
    {"club_name": "Bayer 04 Leverkusen", "rank": 19, "points": 1588.5, "continent": "Europe"},
    {"club_name": "AS Roma", "rank": 20, "points": 1565.0, "continent": "Europe"},
    {"club_name": "Newcastle United", "rank": 21, "points": 1541.5, "continent": "Europe"},
    {"club_name": "LOSC Lille", "rank": 22, "points": 1518.0, "continent": "Europe"},
    {"club_name": "FC Porto", "rank": 23, "points": 1494.5, "continent": "Europe"},
    {"club_name": "Olympique Lyon", "rank": 24, "points": 1471.0, "continent": "Europe"},
    {"club_name": "Atalanta", "rank": 25, "points": 1447.5, "continent": "Europe"},
    {"club_name": "Benfica", "rank": 26, "points": 1424.0, "continent": "Europe"},
    {"club_name": "Leicester City", "rank": 27, "points": 1400.5, "continent": "Europe"},
    {"club_name": "Villarreal CF", "rank": 28, "points": 1377.0, "continent": "Europe"},
    {"club_name": "West Ham United", "rank": 29, "points": 1353.5, "continent": "Europe"},
    {"club_name": "Sporting CP", "rank": 30, "points": 1330.0, "continent": "Europe"},
    {"club_name": "Real Betis Seville", "rank": 31, "points": 1306.5, "continent": "Europe"},
    {"club_name": "Lazio", "rank": 32, "points": 1283.0, "continent": "Europe"},
    {"club_name": "Olympique Marseille", "rank": 33, "points": 1259.5, "continent": "Europe"},
    {"club_name": "Eintracht Frankfurt", "rank": 34, "points": 1236.0, "continent": "Europe"},
    {"club_name": "Aston Villa", "rank": 35, "points": 1212.5, "continent": "Europe"},
    {"club_name": "Brighton & Hove Albion", "rank": 36, "points": 1189.0, "continent": "Europe"},
    {"club_name": "AS Monaco", "rank": 37, "points": 1165.5, "continent": "Europe"},
    {"club_name": "Fiorentina", "rank": 38, "points": 1142.0, "continent": "Europe"},
    {"club_name": "Valencia CF", "rank": 39, "points": 1118.5, "continent": "Europe"},
    {"club_name": "Real Sociedad San Sebastian", "rank": 40, "points": 1095.0, "continent": "Europe"},
    {"club_name": "VfB Stuttgart", "rank": 41, "points": 1071.5, "continent": "Europe"},
    {"club_name": "OGC Nice", "rank": 42, "points": 1048.0, "continent": "Europe"},
    {"club_name": "Bologna FC", "rank": 43, "points": 1024.5, "continent": "Europe"},
    {"club_name": "Wolverhampton Wanderers", "rank": 44, "points": 1001.0, "continent": "Europe"},
    {"club_name": "Athletic Bilbao", "rank": 45, "points": 977.5, "continent": "Europe"},
    {"club_name": "Crystal Palace", "rank": 46, "points": 954.0, "continent": "Europe"},
    {"club_name": "Everton", "rank": 47, "points": 930.5, "continent": "Europe"},
    {"club_name": "1. FC Union Berlin", "rank": 48, "points": 907.0, "continent": "Europe"},
    {"club_name": "Fulham", "rank": 49, "points": 883.5, "continent": "Europe"},
    {"club_name": "Stade Rennais FC", "rank": 50, "points": 860.0, "continent": "Europe"},
]


class Command(BaseCommand):
    help = 'Loads FIFA club world rankings data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing rankings before loading new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Deleting existing rankings...'))
            ClubRanking.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing rankings deleted.'))

        self.stdout.write(self.style.NOTICE('Loading club rankings...'))
        
        rankings_created = 0
        rankings_updated = 0
        rankings_skipped = 0
        ranking_date = date(2024, 10, 1)  # October 2024 rankings

        for ranking_data in RANKINGS_DATA:
            club_name = ranking_data['club_name']
            
            # Find the club
            try:
                club = Club.objects.get(name=club_name)
            except Club.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  Club '{club_name}' not found. Skipping."))
                rankings_skipped += 1
                continue
            
            # Check if ranking already exists for this club and date
            existing_ranking = ClubRanking.objects.filter(
                club=club,
                ranking_date=ranking_date
            ).first()
            
            if existing_ranking:
                # Update existing ranking
                existing_ranking.rank = ranking_data['rank']
                existing_ranking.points = ranking_data['points']
                existing_ranking.continent = ranking_data['continent']
                existing_ranking.save()
                rankings_updated += 1
                self.stdout.write(f"  Updated: #{ranking_data['rank']} {club_name}")
            else:
                # Create new ranking
                ClubRanking.objects.create(
                    club=club,
                    rank=ranking_data['rank'],
                    points=ranking_data['points'],
                    continent=ranking_data['continent'],
                    ranking_date=ranking_date
                )
                rankings_created += 1
                self.stdout.write(f"  Created: #{ranking_data['rank']} {club_name}")

        self.stdout.write(self.style.SUCCESS(f'\n*** Rankings loading complete! ***'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {rankings_created} rankings'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {rankings_updated} rankings'))
        self.stdout.write(self.style.SUCCESS(f'   Skipped: {rankings_skipped} rankings'))
        self.stdout.write(self.style.SUCCESS(f'   Total rankings in database: {ClubRanking.objects.count()}'))


