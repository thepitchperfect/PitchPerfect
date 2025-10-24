import json
from django.core.management.base import BaseCommand
from club_directories.models import Club, ClubDetails

# --- Data for all Premier League clubs ---
PREMIER_LEAGUE_DETAILS = [
    {
        "club_name": "Arsenal",
        "description": "An iconic North London club known for its attacking style of play and 'Invincibles' season.",
        "history_summary": "Founded in 1886, Arsenal has a rich history, including 13 league titles. The tenure of manager Arsène Wenger redefined the club, culminating in an undefeated league season in 2003–04.",
        "stadium_name": "Emirates Stadium",
        "stadium_capacity": 60704,
        "manager_name": "Mikel Arteta"
    },
    {
        "club_name": "Aston Villa",
        "description": "A historic club from Birmingham, one of the founding members of the Football League in 1888.",
        "history_summary": "Aston Villa has a proud history, including winning the 1982 European Cup. They play their home games at the iconic Villa Park.",
        "stadium_name": "Villa Park",
        "stadium_capacity": 42657,
        "manager_name": "Unai Emery"
    },
    {
        "club_name": "AFC Bournemouth",
        "description": "A south coast club known for its attractive, attacking style of play and remarkable rise through the leagues.",
        "history_summary": "Known as 'The Cherries', Bournemouth had a fairytale ascent from the bottom of League Two to the Premier League in just over five years, solidifying their top-flight status in the 2010s.",
        "stadium_name": "Vitality Stadium",
        "stadium_capacity": 11307,
        "manager_name": "Andoni Iraola"
    },
    {
        "club_name": "Brentford",
        "description": "A West London club renowned for its modern, data-driven approach to recruitment and tactics.",
        "history_summary": "After a long absence from the top flight, Brentford returned in 2021. The club's 'Moneyball' strategy has earned them widespread acclaim and established them as a competitive Premier League side.",
        "stadium_name": "Gtech Community Stadium",
        "stadium_capacity": 17250,
        "manager_name": "Thomas Frank"
    },
    {
        "club_name": "Brighton & Hove Albion",
        "description": "A progressive south coast club known for its stylish, possession-based football and excellent recruitment.",
        "history_summary": "Brighton achieved promotion to the Premier League in 2017. Under managers like Graham Potter and Roberto De Zerbi, they have become known for their attractive tactical approach and qualifying for European football.",
        "stadium_name": "Amex Stadium",
        "stadium_capacity": 31876,
        "manager_name": "Fabian Hürzeler"
    },
    {
        "club_name": "Burnley",
        "description": "A historic club from Lancashire, one of the founding members of the Football League.",
        "history_summary": "Known as 'The Clarets', Burnley have been champions of England twice. They have enjoyed several spells in the Premier League, known for their pragmatic and resilient style of play.",
        "stadium_name": "Turf Moor",
        "stadium_capacity": 21944,
        "manager_name": "Scott Parker"
    },
    {
        "club_name": "Chelsea",
        "description": "A top London club that has enjoyed significant domestic and European success in the 21st century.",
        "history_summary": "Transformed by new ownership in 2003, Chelsea became a Premier League powerhouse. The club has won the UEFA Champions League twice, in 2012 and 2021.",
        "stadium_name": "Stamford Bridge",
        "stadium_capacity": 40343,
        "manager_name": "Enzo Maresca"
    },
    {
        "club_name": "Crystal Palace",
        "description": "A South London club known for its passionate fanbase at Selhurst Park and flair players.",
        "history_summary": "Palace have a long history in England's top divisions. They are known for their 'Eagles' nickname and have reached two FA Cup finals.",
        "stadium_name": "Selhurst Park",
        "stadium_capacity": 25486,
        "manager_name": "Oliver Glasner"
    },
    {
        "club_name": "Everton",
        "description": "A historic club from Liverpool with a long-standing presence in English top-flight football.",
        "history_summary": "Known as 'The Toffees', Everton are one of the founding members of the Football League and have competed in the top division for a record number of seasons. They play at Goodison Park.",
        "stadium_name": "Goodison Park",
        "stadium_capacity": 39414,
        "manager_name": "Sean Dyche"
    },
    {
        "club_name": "Fulham",
        "description": "London's oldest professional football club, playing at the historic Craven Cottage on the banks of the Thames.",
        "history_summary": "Fulham have a long and varied history, including a memorable run to the UEFA Europa League final in 2010. Craven Cottage is one of the most unique and historic grounds in England.",
        "stadium_name": "Craven Cottage",
        "stadium_capacity": 24500,
        "manager_name": "Marco Silva"
    },
    {
        "club_name": "Leeds United",
        "description": "A club with a passionate one-city fanbase, known for its intense, high-energy style of play.",
        "history_summary": "Leeds' most successful era was under manager Don Revie in the 1960s and 70s. They won their last top-flight title in 1992 and are famous for the atmosphere at Elland Road.",
        "stadium_name": "Elland Road",
        "stadium_capacity": 37608,
        "manager_name": "Daniel Farke"
    },
    {
        "club_name": "Liverpool",
        "description": "A historic club with a passionate fanbase, known for its European success and 'You'll Never Walk Alone' anthem.",
        "history_summary": "Liverpool dominated English and European football in the 1970s and 80s. The club has seen a modern resurgence, winning its first Premier League title in 2020 under manager Jürgen Klopp.",
        "stadium_name": "Anfield",
        "stadium_capacity": 61276,
        "manager_name": "Arne Slot"
    },
    {
        "club_name": "Manchester City",
        "description": "A dominant force in modern English football, known for its technical, possession-based style.",
        "history_summary": "After being acquired in 2008, Manchester City rose to become one of Europe's elite. Under Pep Guardiola, they achieved a historic treble in the 2022-23 season.",
        "stadium_name": "Etihad Stadium",
        "stadium_capacity": 53400,
        "manager_name": "Pep Guardiola"
    },
    {
        "club_name": "Manchester United",
        "description": "One of the most widely supported football clubs in the world, with a storied history of success.",
        "history_summary": "Known as the 'Red Devils', the club's golden era came under manager Sir Alex Ferguson, who won 13 Premier League titles. The club is synonymous with legends like George Best, Sir Bobby Charlton, and David Beckham.",
        "stadium_name": "Old Trafford",
        "stadium_capacity": 74310,
        "manager_name": "Erik ten Hag"
    },
    {
        "club_name": "Newcastle United",
        "description": "A club with a famously passionate fanbase, known as the 'Toon Army', based in the North East.",
        "history_summary": "Newcastle have a proud history and enjoyed particular success in the 1990s with their 'Entertainers' team. Following a 2021 takeover, the club has re-emerged as a contender for European places.",
        "stadium_name": "St. James' Park",
        "stadium_capacity": 52305,
        "manager_name": "Eddie Howe"
    },
    {
        "club_name": "Nottingham Forest",
        "description": "A historic club famous for its back-to-back European Cup victories in 1979 and 1980.",
        "history_summary": "Led by the legendary manager Brian Clough, Forest's rise from the Second Division to become champions of Europe in successive seasons is one of football's greatest stories.",
        "stadium_name": "City Ground",
        "stadium_capacity": 30404,
        "manager_name": "Nuno Espírito Santo"
    },
    {
        "club_name": "Sunderland",
        "description": "A major club from the North East with a passionate fanbase and a rich industrial heritage.",
        "history_summary": "Known as the 'Black Cats', Sunderland has a storied history as six-time champions of England. They play their games at the impressive Stadium of Light.",
        "stadium_name": "Stadium of Light",
        "stadium_capacity": 49000,
        "manager_name": "Régis Le Bris"
    },
    {
        "club_name": "Tottenham Hotspur",
        "description": "A North London club known for its attacking football and state-of-the-art stadium.",
        "history_summary": "Spurs have a reputation for playing attractive football. They were the first British club to win a major European trophy in 1963 and were Champions League finalists in 2019.",
        "stadium_name": "Tottenham Hotspur Stadium",
        "stadium_capacity": 62850,
        "manager_name": "Ange Postecoglou"
    },
    {
        "club_name": "West Ham United",
        "description": "An East London club with a passionate following, known as the 'Academy of Football'.",
        "history_summary": "Known as 'The Hammers', West Ham won the UEFA Europa Conference League in 2023. The club is famous for producing England's 1966 World Cup-winning trio: Bobby Moore, Geoff Hurst, and Martin Peters.",
        "stadium_name": "London Stadium",
        "stadium_capacity": 62500,
        "manager_name": "Julen Lopetegui"
    },
    {
        "club_name": "Wolverhampton Wanderers",
        "description": "A historic Midlands club, known as 'Wolves', with a distinct gold and black kit.",
        "history_summary": "Wolves were a dominant force in the 1950s, winning three league titles. They have re-established themselves as a solid Premier League club with a strong Portuguese influence.",
        "stadium_name": "Molineux Stadium",
        "stadium_capacity": 31750,
        "manager_name": "Gary O'Neil"
    }
]


class Command(BaseCommand):
    help = 'Loads club details for the Premier League from an embedded list'

    def handle(self, *args, **kwargs):
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE('Starting to load Premier League details...'))

        for item in PREMIER_LEAGUE_DETAILS:
            club_name = item.get('club_name')
            if not club_name:
                self.stdout.write(self.style.WARNING("Skipped item with no 'club_name'."))
                skipped_count += 1
                continue

            try:
                # Find the club in the main Club model
                club = Club.objects.get(name=club_name, league__name="Premier League")
                
                # Create or update the ClubDetails entry
                details, created = ClubDetails.objects.update_or_create(
                    club=club,
                    defaults={
                        'description': item.get('description'),
                        'history_summary': item.get('history_summary'),
                        'stadium_name': item.get('stadium_name'),
                        'stadium_capacity': item.get('stadium_capacity'),
                        'manager_name': item.get('manager_name'),
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Club.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Warning: Club '{club_name}' not found in database. Skipping."))
                skipped_count += 1
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing {club_name}: {e}"))
                skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(f"\n--- Premier League Details Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))