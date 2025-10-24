import json
from django.core.management.base import BaseCommand
from club_directories.models import Club, ClubDetails

# --- Data for all La Liga clubs ---
LA_LIGA_DETAILS = [
    {
        "club_name": "Real Madrid",
        "description": "Arguably the most successful club in European history, synonymous with 'Galácticos' and trophies.",
        "history_summary": "Real Madrid has a record 15 UEFA Champions League titles. The club's identity was built by legends like Alfredo Di Stéfano, Ferenc Puskás, Zinedine Zidane, and Cristiano Ronaldo.",
        "stadium_name": "Santiago Bernabéu",
        "stadium_capacity": 85000,
        "manager_name": "Carlo Ancelotti"
    },
    {
        "club_name": "FC Barcelona",
        "description": "A world-renowned club famous for its 'tiki-taka' philosophy and legendary La Masia academy.",
        "history_summary": "Barcelona's identity was shaped by Johan Cruyff as both player and manager. The era of Pep Guardiola, featuring Lionel Messi, Xavi, and Iniesta, is considered one of the greatest in football history.",
        "stadium_name": "Camp Nou",
        "stadium_capacity": 99354,
        "manager_name": "Hansi Flick"
    },
    {
        "club_name": "Villarreal CF",
        "description": "Known as the 'Yellow Submarine', a successful small-town club that consistently competes in Europe.",
        "history_summary": "From a small city, Villarreal has become a La Liga staple, known for playing attractive football. Their greatest achievement came in 2021 when they won the UEFA Europa League.",
        "stadium_name": "Estadio de la Cerámica",
        "stadium_capacity": 23008,
        "manager_name": "Marcelino"
    },
    {
        "club_name": "Real Betis Seville",
        "description": "One of Seville's two major clubs, known for its passionate green-and-white-clad fanbase.",
        "history_summary": "Betis won the La Liga title in 1935 and have won the Copa del Rey three times, most recently in 2022. They enjoy a fierce city rivalry with Sevilla FC.",
        "stadium_name": "Benito Villamarín",
        "stadium_capacity": 60721,
        "manager_name": "Manuel Pellegrini"
    },
    {
        "club_name": "Atletico Madrid",
        "description": "A fierce competitor known for its passionate support and resilient, defensive style under Diego Simeone.",
        "history_summary": "Known as 'Los Colchoneros' (The Mattress Makers), Atlético has consistently challenged the duopoly of Real Madrid and Barcelona, winning La Liga several times, most recently in 2021.",
        "stadium_name": "Metropolitano Stadium",
        "stadium_capacity": 70460,
        "manager_name": "Diego Simeone"
    },
    {
        "club_name": "Sevilla FC",
        "description": "The other major club from Seville, regarded as specialists in the UEFA Europa League.",
        "history_summary": "Sevilla holds the record for the most Europa League titles, showcasing their incredible prowess in knockout competitions. Their rivalry with Real Betis, 'El Gran Derbi', is one of Spain's most intense.",
        "stadium_name": "Ramón Sánchez Pizjuán",
        "stadium_capacity": 43883,
        "manager_name": "García Pimienta"
    },
    {
        "club_name": "Elche CF",
        "description": "A club from the Valencian community, recognizable by its distinctive green-striped kit.",
        "history_summary": "Elche has spent numerous seasons in La Liga, often battling bravely against relegation. They play at the large Estadio Martínez Valero.",
        "stadium_name": "Estadio Martínez Valero",
        "stadium_capacity": 31388,
        "manager_name": "Sebastián Beccacece"
    },
    {
        "club_name": "Athletic Bilbao",
        "description": "A unique club from the Basque Country, famous for its 'cantera' policy of only using Basque players.",
        "history_summary": "This policy has made Athletic a symbol of Basque pride. The club is one of only three (along with Real Madrid and Barcelona) to have never been relegated from La Liga.",
        "stadium_name": "San Mamés",
        "stadium_capacity": 53331,
        "manager_name": "Ernesto Valverde"
    },
    {
        "club_name": "Espanyol Barcelona",
        "description": "Barcelona's 'other' club, with a long history in La Liga and a strong rivalry with FC Barcelona.",
        "history_summary": "Known as the 'Periquitos' (The Budgies), Espanyol has a proud history, though often overshadowed by its city rival. They have won the Copa del Rey four times.",
        "stadium_name": "Stage Front Stadium",
        "stadium_capacity": 40000,
        "manager_name": "Manolo González"
    },
    {
        "club_name": "Deportivo Alaves",
        "description": "A resilient Basque club from Vitoria-Gasteiz, known for being tough to beat at home.",
        "history_summary": "Alavés are famous for their remarkable run to the 2001 UEFA Cup final, where they lost 5-4 to Liverpool in a thriller. They play at the historic Mendizorrotza stadium.",
        "stadium_name": "Mendizorrotza",
        "stadium_capacity": 19840,
        "manager_name": "Luis García Plaza"
    },
    {
        "club_name": "Getafe CF",
        "description": "A club from the Madrid suburbs, known for a tough, pragmatic, and highly competitive style of play.",
        "history_summary": "Getafe established themselves as a La Liga regular in the 2000s. Under manager José Bordalás, they have become known for a highly disciplined and difficult-to-play-against identity.",
        "stadium_name": "Coliseum Alfonso Pérez",
        "stadium_capacity": 16500,
        "manager_name": "José Bordalás"
    },
    {
        "club_name": "CA Osasuna",
        "description": "A club from Pamplona, Navarra, known for their intense and fiery home support at El Sadar.",
        "history_summary": "Osasuna, meaning 'Health' in Basque, are known for their grit. They reached the Copa del Rey final in 2023 and have a reputation for being one of the toughest away games in Spain.",
        "stadium_name": "El Sadar",
        "stadium_capacity": 23516,
        "manager_name": "Jagoba Arrasate"
    },
    {
        "club_name": "Levante UD",
        "description": "A club from Valencia, known as 'Granotes' (The Frogs), with a history of playing entertaining football.",
        "history_summary": "Levante are the 'other' club in the city of Valencia and enjoy a local derby with Valencia CF. They have had several successful spells in La Liga, often playing an attractive, attacking style.",
        "stadium_name": "Ciutat de València",
        "stadium_capacity": 26354,
        "manager_name": "Julián Calero"
    },
    {
        "club_name": "Rayo Vallecano",
        "description": "A Madrid-based club from the working-class neighborhood of Vallecas, known for its strong community identity.",
        "history_summary": "Rayo is famous for its unique stadium (with a wall at one end) and its passionate, left-leaning fanbase. The club is a symbol of its neighborhood.",
        "stadium_name": "Vallecas",
        "stadium_capacity": 14708,
        "manager_name": "Iñigo Pérez"
    },
    {
        "club_name": "Valencia CF",
        "description": "A historic Spanish giant, known for its iconic Mestalla stadium and a world-class youth academy.",
        "history_summary": "Valencia has won La Liga six times and reached two consecutive Champions League finals in 2000 and 2001. Their academy, 'Paterna', has produced stars like David Silva and Isco.",
        "stadium_name": "Mestalla",
        "stadium_capacity": 49430,
        "manager_name": "Rubén Baraja"
    },
    {
        "club_name": "RC Celta de Vigo",
        "description": "A historic club from Galicia in northwest Spain, known for its technical players and strong regional identity.",
        "history_summary": "Celta has a history of playing attractive football, led by club legends like Iago Aspas. They play at the Balaídos stadium, located near the Atlantic coast.",
        "stadium_name": "Balaídos",
        "stadium_capacity": 24791,
        "manager_name": "Claudio Giráldez"
    },
    {
        "club_name": "Real Oviedo",
        "description": "A historic club from Asturias with a passionate following, currently fighting to return to La Liga.",
        "history_summary": "Real Oviedo was a La Liga regular for many years but fell to the fourth tier due to financial issues. They have since recovered and are a prominent force in the Segunda División.",
        "stadium_name": "Carlos Tartiere",
        "stadium_capacity": 30500,
        "manager_name": "Luis Carrión"
    },
    {
        "club_name": "Girona FC",
        "description": "A Catalan club that has seen a meteoric rise, culminating in a historic 2023-24 season.",
        "history_summary": "Part of the City Football Group, Girona gained promotion to La Liga in 2017. Under manager Míchel, they shocked Spain by challenging for the title and qualifying for the Champions League.",
        "stadium_name": "Montilivi",
        "stadium_capacity": 14624,
        "manager_name": "Míchel"
    },
    {
        "club_name": "Real Sociedad San Sebastian",
        "description": "A proud Basque club renowned for its world-class 'Zubieta' academy and technical style of play.",
        "history_summary": "Real Sociedad won back-to-back La Liga titles in the early 1980s. Today, under manager Imanol Alguacil, they are known for promoting academy talents and playing beautiful football.",
        "stadium_name": "Reale Arena (Anoeta)",
        "stadium_capacity": 39313,
        "manager_name": "Imanol Alguacil"
    },
    {
        "club_name": "RCD Mallorca",
        "description": "An island club from Mallorca that is known for its strong defense and passionate home support.",
        "history_summary": "Mallorca's golden era was in the late 90s/early 00s, winning the Copa del Rey in 2003. They were surprise finalists in the 2024 Copa del Rey.",
        "stadium_name": "Son Moix",
        "stadium_capacity": 23142,
        "manager_name": "Jagoba Arrasate"
    }
]


class Command(BaseCommand):
    help = 'Loads club details for La Liga from an embedded list'

    def handle(self, *args, **kwargs):
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE('Starting to load La Liga details...'))

        for item in LA_LIGA_DETAILS:
            club_name = item.get('club_name')
            if not club_name:
                self.stdout.write(self.style.WARNING("Skipped item with no 'club_name'."))
                skipped_count += 1
                continue

            try:
                # Find the club in the main Club model
                club = Club.objects.get(name=club_name, league__name="La Liga")
                
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
        
        self.stdout.write(self.style.SUCCESS(f"\n--- La Liga Details Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))