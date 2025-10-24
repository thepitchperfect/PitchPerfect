from django.core.management.base import BaseCommand
from club_directories.models import Club
from statisticsrafi.models import Award
from datetime import date

# Club Awards Data - Major achievements for top clubs
CLUB_AWARDS = [
    # Manchester City
    {"club_name": "Manchester City", "award_type": "TEAM_OTY", "title": "Premier League Champions", "season": "2023/24", "date": "2024-05-19", "description": "Won the Premier League title for the 4th consecutive year"},
    {"club_name": "Manchester City", "award_type": "OTHER", "title": "UEFA Champions League Winners", "season": "2022/23", "date": "2023-06-10", "description": "Won the Champions League, completing the treble"},
    
    # Real Madrid
    {"club_name": "Real Madrid", "award_type": "OTHER", "title": "UEFA Champions League Winners", "season": "2023/24", "date": "2024-06-01", "description": "Record 15th Champions League title"},
    {"club_name": "Real Madrid", "award_type": "TEAM_OTY", "title": "La Liga Champions", "season": "2023/24", "date": "2024-05-25", "description": "Won La Liga title"},
    {"club_name": "Real Madrid", "award_type": "OTHER", "title": "FIFA Club World Cup Winners", "season": "2023/24", "date": "2024-02-11", "description": "Won the Club World Cup"},
    
    # FC Bayern München
    {"club_name": "FC Bayern München", "award_type": "TEAM_OTY", "title": "Bundesliga Champions", "season": "2023/24", "date": "2024-05-18", "description": "Won the Bundesliga title"},
    {"club_name": "FC Bayern München", "award_type": "OTHER", "title": "DFB-Pokal Winners", "season": "2023/24", "date": "2024-05-25", "description": "Won the German Cup"},
    
    # Liverpool
    {"club_name": "Liverpool", "award_type": "OTHER", "title": "EFL Cup Winners", "season": "2023/24", "date": "2024-02-25", "description": "Won the League Cup"},
    {"club_name": "Liverpool", "award_type": "OTHER", "title": "FA Cup Winners", "season": "2023/24", "date": "2024-05-25", "description": "Won the FA Cup"},
    
    # FC Barcelona
    {"club_name": "FC Barcelona", "award_type": "TEAM_OTY", "title": "La Liga Champions", "season": "2022/23", "date": "2023-05-28", "description": "Won La Liga title"},
    
    # Paris Saint-Germain
    {"club_name": "Paris Saint-Germain", "award_type": "TEAM_OTY", "title": "Ligue 1 Champions", "season": "2023/24", "date": "2024-05-12", "description": "Won Ligue 1 title"},
    
    # Chelsea
    {"club_name": "Chelsea", "award_type": "OTHER", "title": "UEFA Conference League Winners", "season": "2023/24", "date": "2024-05-29", "description": "Won the Conference League"},
    
    # Inter Milan
    {"club_name": "Inter Milan", "award_type": "TEAM_OTY", "title": "Serie A Champions", "season": "2023/24", "date": "2024-04-22", "description": "Won Serie A title"},
    {"club_name": "Inter Milan", "award_type": "OTHER", "title": "Coppa Italia Winners", "season": "2022/23", "date": "2023-05-24", "description": "Won the Italian Cup"},
    
    # Atletico Madrid
    {"club_name": "Atletico Madrid", "award_type": "TEAM_OTY", "title": "La Liga Champions", "season": "2020/21", "date": "2021-05-22", "description": "Won La Liga title"},
    
    # Manchester United
    {"club_name": "Manchester United", "award_type": "OTHER", "title": "EFL Cup Winners", "season": "2022/23", "date": "2023-02-26", "description": "Won the League Cup"},
    
    # Borussia Dortmund
    {"club_name": "Borussia Dortmund", "award_type": "OTHER", "title": "DFB-Pokal Winners", "season": "2023/24", "date": "2024-05-25", "description": "Won the German Cup"},
    
    # Juventus FC
    {"club_name": "Juventus FC", "award_type": "OTHER", "title": "Coppa Italia Winners", "season": "2023/24", "date": "2024-05-15", "description": "Won the Italian Cup"},
    
    # Arsenal
    {"club_name": "Arsenal", "award_type": "OTHER", "title": "FA Cup Winners", "season": "2019/20", "date": "2020-08-01", "description": "Won the FA Cup"},
    
    # Napoli
    {"club_name": "Napoli", "award_type": "TEAM_OTY", "title": "Serie A Champions", "season": "2022/23", "date": "2023-05-04", "description": "First Serie A title in 33 years"},
    
    # Tottenham Hotspur
    {"club_name": "Tottenham Hotspur", "award_type": "OTHER", "title": "Premier League Runner-up", "season": "2022/23", "date": "2023-05-28", "description": "Finished 2nd in Premier League"},
    
    # AC Milan
    {"club_name": "AC Milan", "award_type": "TEAM_OTY", "title": "Serie A Champions", "season": "2021/22", "date": "2022-05-22", "description": "Won Serie A title"},
    
    # RB Leipzig
    {"club_name": "RB Leipzig", "award_type": "OTHER", "title": "DFB-Pokal Winners", "season": "2022/23", "date": "2023-06-03", "description": "Won the German Cup"},
    
    # Sevilla FC
    {"club_name": "Sevilla FC", "award_type": "OTHER", "title": "UEFA Europa League Winners", "season": "2022/23", "date": "2023-05-31", "description": "Record 7th Europa League title"},
    
    # Bayer 04 Leverkusen
    {"club_name": "Bayer 04 Leverkusen", "award_type": "TEAM_OTY", "title": "Bundesliga Champions", "season": "2023/24", "date": "2024-04-14", "description": "First Bundesliga title - Unbeaten season"},
    {"club_name": "Bayer 04 Leverkusen", "award_type": "OTHER", "title": "DFB-Pokal Winners", "season": "2023/24", "date": "2024-05-25", "description": "Won the German Cup - Completing the double"},
    
    # AS Roma
    {"club_name": "AS Roma", "award_type": "OTHER", "title": "UEFA Europa Conference League Winners", "season": "2021/22", "date": "2022-05-25", "description": "Won the inaugural Conference League"},
    
    # Newcastle United
    {"club_name": "Newcastle United", "award_type": "OTHER", "title": "EFL Cup Winners", "season": "2022/23", "date": "2023-02-26", "description": "First major trophy in decades"},
    
    # LOSC Lille
    {"club_name": "LOSC Lille", "award_type": "TEAM_OTY", "title": "Ligue 1 Champions", "season": "2020/21", "date": "2021-05-23", "description": "Won Ligue 1 title"},
    
    # FC Porto
    {"club_name": "FC Porto", "award_type": "TEAM_OTY", "title": "Primeira Liga Champions", "season": "2023/24", "date": "2024-05-11", "description": "Won the Portuguese league"},
    
    # Olympique Lyon
    {"club_name": "Olympique Lyon", "award_type": "OTHER", "title": "Coupe de France Winners", "season": "2023/24", "date": "2024-05-25", "description": "Won the French Cup"},
    
    # Atalanta
    {"club_name": "Atalanta", "award_type": "OTHER", "title": "UEFA Europa League Winners", "season": "2023/24", "date": "2024-05-22", "description": "First major European trophy"},
    
    # Benfica
    {"club_name": "Benfica", "award_type": "TEAM_OTY", "title": "Primeira Liga Champions", "season": "2022/23", "date": "2023-05-13", "description": "Won the Portuguese league"},
    
    # Villarreal CF
    {"club_name": "Villarreal CF", "award_type": "OTHER", "title": "UEFA Europa League Winners", "season": "2020/21", "date": "2021-05-26", "description": "First major European trophy"},
    
    # West Ham United
    {"club_name": "West Ham United", "award_type": "OTHER", "title": "UEFA Europa Conference League Winners", "season": "2022/23", "date": "2023-06-07", "description": "Won the Conference League"},
    
    # Sporting CP
    {"club_name": "Sporting CP", "award_type": "TEAM_OTY", "title": "Primeira Liga Champions", "season": "2020/21", "date": "2021-05-11", "description": "First league title in 19 years"},
    
    # Real Betis Seville
    {"club_name": "Real Betis Seville", "award_type": "OTHER", "title": "Copa del Rey Winners", "season": "2021/22", "date": "2022-04-23", "description": "Won the Spanish Cup"},
    
    # Lazio
    {"club_name": "Lazio", "award_type": "OTHER", "title": "Coppa Italia Winners", "season": "2018/19", "date": "2019-05-15", "description": "Won the Italian Cup"},
    
    # Olympique Marseille
    {"club_name": "Olympique Marseille", "award_type": "OTHER", "title": "UEFA Champions League Winners", "season": "1992/93", "date": "1993-05-26", "description": "Only French club to win Champions League"},
    
    # Eintracht Frankfurt
    {"club_name": "Eintracht Frankfurt", "award_type": "OTHER", "title": "UEFA Europa League Winners", "season": "2021/22", "date": "2022-05-18", "description": "Won the Europa League"},
    
    # Aston Villa
    {"club_name": "Aston Villa", "award_type": "OTHER", "title": "UEFA Europa Conference League Winners", "season": "2023/24", "date": "2024-05-29", "description": "Won the Conference League"},
]


class Command(BaseCommand):
    help = 'Loads club awards data into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing club awards before loading new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Deleting existing club awards...'))
            Award.objects.filter(club__isnull=False).delete()
            self.stdout.write(self.style.SUCCESS('Existing club awards deleted.'))

        self.stdout.write(self.style.NOTICE('Loading club awards...'))
        
        awards_created = 0
        awards_updated = 0
        awards_skipped = 0

        for award_data in CLUB_AWARDS:
            club_name = award_data['club_name']
            
            # Find the club
            try:
                club = Club.objects.get(name=club_name)
            except Club.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"  Club '{club_name}' not found. Skipping award: {award_data['title']}"))
                awards_skipped += 1
                continue
            
            # Parse the date
            date_parts = award_data['date'].split('-')
            award_date = date(int(date_parts[0]), int(date_parts[1]), int(date_parts[2]))
            
            # Check if award already exists
            existing_award = Award.objects.filter(
                club=club,
                title=award_data['title'],
                season=award_data['season']
            ).first()
            
            if existing_award:
                # Update existing award
                existing_award.award_type = award_data['award_type']
                existing_award.date_awarded = award_date
                existing_award.description = award_data['description']
                existing_award.save()
                awards_updated += 1
                self.stdout.write(f"  Updated: {club_name} - {award_data['title']}")
            else:
                # Create new award
                Award.objects.create(
                    club=club,
                    award_type=award_data['award_type'],
                    title=award_data['title'],
                    season=award_data['season'],
                    date_awarded=award_date,
                    description=award_data['description']
                )
                awards_created += 1
                self.stdout.write(f"  Created: {club_name} - {award_data['title']}")

        self.stdout.write(self.style.SUCCESS(f'\n*** Awards loading complete! ***'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {awards_created} awards'))
        self.stdout.write(self.style.SUCCESS(f'   Updated: {awards_updated} awards'))
        self.stdout.write(self.style.SUCCESS(f'   Skipped: {awards_skipped} awards'))
        self.stdout.write(self.style.SUCCESS(f'   Total club awards in database: {Award.objects.filter(club__isnull=False).count()}'))


