import json
from django.core.management.base import BaseCommand
from club_directories.models import Club, ClubDetails

# --- Data for all Serie A clubs ---
SERIE_A_DETAILS = [
    {
        "club_name": "Atalanta",
        "description": "A dynamic club from Bergamo, known for its high-octane attacking style and remarkable recent success.",
        "history_summary": "Under manager Gian Piero Gasperini, Atalanta transformed from a provincial side into a Champions League regular. Their greatest triumph came in 2024, winning the UEFA Europa League, the club's first-ever European trophy.",
        "stadium_name": "Gewiss Stadium",
        "stadium_capacity": 25000,
        "manager_name": "Gian Piero Gasperini"
    },
    {
        "club_name": "AC Milan",
        "description": "A legendary club with a rich European history, second only to Real Madrid in Champions League titles.",
        "history_summary": "The 'Rossoneri' have been home to some of the game's greatest players, including Paolo Maldini, Franco Baresi, and Marco van Basten. Their seven Champions League/European Cup wins are a club hallmark.",
        "stadium_name": "San Siro (Stadio Giuseppe Meazza)",
        "stadium_capacity": 75817,
        "manager_name": "Paulo Fonseca"
    },
    {
        "club_name": "Bologna FC",
        "description": "A historic Italian club, one of the founding members of Serie A, known as the 'Rossoblù'.",
        "history_summary": "Bologna was a dominant force in the 1920s and 30s, winning seven Serie A titles. After decades of mixed fortunes, they had a remarkable resurgence, qualifying for the Champions League in 2024.",
        "stadium_name": "Stadio Renato Dall'Ara",
        "stadium_capacity": 36532,
        "manager_name": "Vincenzo Italiano"
    },
    {
        "club_name": "Cagliari Calcio",
        "description": "The major club from the island of Sardinia, known for its passionate support.",
        "history_summary": "Cagliari's greatest moment came in 1970 when, led by the legendary Riva, they won their first and only Scudetto. The club is a symbol of pride for the island of Sardinia.",
        "stadium_name": "Unipol Domus",
        "stadium_capacity": 16416,
        "manager_name": "Davide Nicola"
    },
    {
        "club_name": "FC Empoli",
        "description": "A small Tuscan club renowned for its excellent youth academy and ability to survive in Serie A.",
        "history_summary": "Empoli is a classic 'provincial' club that has produced a remarkable number of top-level players and managers. They are known for their strong scouting and development model.",
        "stadium_name": "Stadio Carlo Castellani",
        "stadium_capacity": 16180,
        "manager_name": "Roberto D'Aversa"
    },
    {
        "club_name": "Fiorentina",
        "description": "A major club from the beautiful city of Florence, known for its distinctive purple kits.",
        "history_summary": "Known as 'La Viola', Fiorentina has won two Scudetti and is a regular contender for European places. They were recent finalists in the UEFA Europa Conference League.",
        "stadium_name": "Stadio Artemio Franchi",
        "stadium_capacity": 43147,
        "manager_name": "Raffaele Palladino"
    },
    {
        "club_name": "Genoa CFC",
        "description": "The oldest active football club in Italy, with a rich and decorated history.",
        "history_summary": "Founded in 1893, Genoa was the dominant force in the early years of Italian football, winning nine championships. They enjoy a fierce city rivalry with Sampdoria.",
        "stadium_name": "Stadio Luigi Ferraris",
        "stadium_capacity": 33205,
        "manager_name": "Alberto Gilardino"
    },
    {
        "club_name": "Hellas Verona",
        "description": "A historic club from Verona, famous for its passionate fanbase and a miracle Scudetto win.",
        "history_summary": "Hellas Verona achieved one of the greatest underdog stories in football history by winning the 1984-85 Serie A title, a feat considered almost impossible for a non-traditional giant.",
        "stadium_name": "Stadio Marcantonio Bentegodi",
        "stadium_capacity": 31045,
        "manager_name": "Marco Baroni"
    },
    {
        "club_name": "Inter Milan",
        "description": "A historic rival of AC Milan, and the only Italian club to have won a continental treble (2010).",
        "history_summary": "Internazionale, or 'Nerazzurri', are one of Italy's most successful clubs. Their historic treble under José Mourinho in 2009-10 (Serie A, Coppa Italia, Champions League) is a landmark achievement.",
        "stadium_name": "San Siro (Stadio Giuseppe Meazza)",
        "stadium_capacity": 75817,
        "manager_name": "Simone Inzaghi"
    },
    {
        "club_name": "Juventus FC",
        "description": "The most decorated club in Italian football, known as the 'Old Lady' (La Vecchia Signora).",
        "history_summary": "Juventus has won the most Serie A titles (Scudetti) in history. The club dominated the 2010s, winning nine consecutive league titles from 2012 to 2020.",
        "stadium_name": "Allianz Stadium",
        "stadium_capacity": 41507,
        "manager_name": "Thiago Motta"
    },
    {
        "club_name": "Lazio",
        "description": "One of the two major clubs from Rome, known for its sky blue colors and eagle mascot.",
        "history_summary": "Lazio has won two Serie A titles, with their most recent triumph in 2000. They enjoy one of the fiercest rivalries in the world, the 'Derby della Capitale', against AS Roma.",
        "stadium_name": "Stadio Olimpico",
        "stadium_capacity": 70634,
        "manager_name": "Marco Baroni"
    },
    {
        "club_name": "US Lecce",
        "description": "A passionate club from the Salento region of southern Italy, known as the 'Giallorossi'.",
        "history_summary": "Lecce is a well-supported club that frequently moves between Serie A and Serie B. They are known for their distinctive yellow and red kits and the passionate atmosphere at their home stadium.",
        "stadium_name": "Stadio Via del mare",
        "stadium_capacity": 31461,
        "manager_name": "Luca Gotti"
    },
    {
        "club_name": "Monza",
        "description": "A club with a long history that finally achieved its first-ever promotion to Serie A in 2022.",
        "history_summary": "After being acquired by Silvio Berlusconi and Adriano Galliani (formerly of AC Milan), Monza embarked on a rapid rise, climbing from Serie C to Serie A in just a few years.",
        "stadium_name": "Stadio Brianteo",
        "stadium_capacity": 16917,
        "manager_name": "Alessandro Nesta"
    },
    {
        "club_name": "Napoli",
        "description": "A passionate club from the south of Italy, forever associated with its icon, Diego Maradona.",
        "history_summary": "Maradona led Napoli to their first-ever Serie A titles in 1987 and 1990, achievements that are legendary in the city. The club won its third Scudetto in 2022-23.",
        "stadium_name": "Stadio Diego Armando Maradona",
        "stadium_capacity": 54726,
        "manager_name": "Antonio Conte"
    },
    {
        "club_name": "Parma",
        "description": "A club famous for its incredible success in the 1990s, winning multiple European trophies.",
        "history_summary": "Parma was one of the 'Seven Sisters' of Serie A, winning two UEFA Cups and a Cup Winners' Cup. After financial collapse, they made a historic climb back to Serie A.",
        "stadium_name": "Stadio Ennio Tardini",
        "stadium_capacity": 22352,
        "manager_name": "Fabio Pecchia"
    },
    {
        "club_name": "Sassuolo",
        "description": "A modern club known for its attractive, attacking football and distinctive green and black kits.",
        "history_summary": "Sassuolo rose from the lower leagues to become a Serie A mainstay, earning praise for their forward-thinking style and ability to develop talent under managers like Roberto De Zerbi.",
        "stadium_name": "Mapei Stadium – Città del Tricolore",
        "stadium_capacity": 21525,
        "manager_name": "Fabio Grosso"
    },
    {
        "club_name": "Torino FC",
        "description": "A historic club from Turin, forever remembered for the 'Grande Torino' team of the 1940s.",
        "history_summary": "The 'Grande Torino' team, which tragically died in the 1949 Superga air disaster, is considered one of the greatest in Italian history. The club has won seven Serie A titles and enjoys a fierce local rivalry with Juventus.",
        "stadium_name": "Stadio Olimpico Grande Torino",
        "stadium_capacity": 28177,
        "manager_name": "Paolo Vanoli"
    },
    {
        "club_name": "Udinese",
        "description": "A stable Serie A club known for its extensive global scouting network that finds and develops talent.",
        "history_summary": "For decades, Udinese has been a model of smart recruitment, consistently finding hidden gems from around the world and selling them for a profit while remaining competitive.",
        "stadium_name": "Stadio Friuli (Bluenergy Stadium)",
        "stadium_capacity": 25132,
        "manager_name": "Kosta Runjaić"
    },
    {
        "club_name": "AS Roma",
        "description": "A major club from the Italian capital, known for its fiercely loyal fanbase and legendary captain, Francesco Totti.",
        "history_summary": "Roma's 'Giallorossi' supporters are famously passionate. The club won the inaugural UEFA Europa Conference League in 2022 under José Mourinho.",
        "stadium_name": "Stadio Olimpico",
        "stadium_capacity": 70634,
        "manager_name": "Claudio Ranieri"
    },
    {
        "club_name": "Venezia FC",
        "description": "A club from the iconic city of Venice, renowned for its stylish, fashion-forward branding.",
        "history_summary": "Venezia has gained global attention for its beautifully designed kits. On the pitch, they have fought to re-establish themselves in Serie A, playing at the unique Stadio Pier Luigi Penzo.",
        "stadium_name": "Stadio Pier Luigi Penzo",
        "stadium_capacity": 11150,
        "manager_name": "Eusebio Di Francesco"
    }
]


class Command(BaseCommand):
    help = 'Loads club details for Serie A from an embedded list'

    def handle(self, *args, **kwargs):
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE('Starting to load Serie A details...'))

        for item in SERIE_A_DETAILS:
            club_name = item.get('club_name')
            if not club_name:
                self.stdout.write(self.style.WARNING("Skipped item with no 'club_name'."))
                skipped_count += 1
                continue

            try:
                # Find the club in the main Club model
                club = Club.objects.get(name=club_name, league__name="Serie A")
                
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
        
        self.stdout.write(self.style.SUCCESS(f"\n--- Serie A Details Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))