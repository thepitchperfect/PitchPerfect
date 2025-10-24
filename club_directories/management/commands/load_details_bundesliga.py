import json
from django.core.management.base import BaseCommand
from club_directories.models import Club, ClubDetails

# --- Data for all Bundesliga clubs ---
BUNDESLIGA_DETAILS = [
    {
        "club_name": "FC Bayern München",
        "description": "The most dominant and successful club in German football history, a perennial European contender.",
        "history_summary": "Bayern has won over 30 Bundesliga titles, including a record 11 consecutive titles from 2013 to 2023. Legends like Franz Beckenbauer, Gerd Müller, and Karl-Heinz Rummenigge defined the club.",
        "stadium_name": "Allianz Arena",
        "stadium_capacity": 75024,
        "manager_name": "Vincent Kompany"
    },
    {
        "club_name": "Borussia Dortmund",
        "description": "A major German club known for its passionate 'Yellow Wall' (Südtribüne) and focus on developing young talent.",
        "history_summary": "Dortmund won the UEFA Champions League in 1997. Under Jürgen Klopp, they won back-to-back Bundesliga titles in 2011 and 2012, cementing their status as Bayern's main rivals.",
        "stadium_name": "Signal Iduna Park",
        "stadium_capacity": 81365,
        "manager_name": "Nuri Şahin"
    },
    {
        "club_name": "RB Leipzig",
        "description": "A modern club that rose rapidly through the German leagues to become a Champions League regular.",
        "history_summary": "Founded in 2009, the club's fast-paced, high-pressing style has made them a consistent top-four team in the Bundesliga and winners of the DFB-Pokal.",
        "stadium_name": "Red Bull Arena",
        "stadium_capacity": 47069,
        "manager_name": "Marco Rose"
    },
    {
        "club_name": "VfB Stuttgart",
        "description": "A historic club from southwestern Germany, known for its passionate fanbase and strong youth academy.",
        "history_summary": "Stuttgart has won the Bundesliga five times, most recently in 2007. The club is a founding member of the Bundesliga and plays in the impressive Mercedes-Benz Arena.",
        "stadium_name": "Mercedes-Benz Arena",
        "stadium_capacity": 60058,
        "manager_name": "Sebastian Hoeneß"
    },
    {
        "club_name": "Bayer 04 Leverkusen",
        "description": "A top-tier club that famously won its first-ever Bundesliga title in 2023-24 with an undefeated season.",
        "history_summary": "Historically nicknamed 'Neverkusen' for finishing as runners-up many times, the club shattered this reputation under Xabi Alonso by completing one of the most dominant seasons in German history.",
        "stadium_name": "BayArena",
        "stadium_capacity": 30210,
        "manager_name": "Xabi Alonso"
    },
    {
        "club_name": "1. FC Köln",
        "description": "A major club from Cologne, known for its passionate supporters and billy goat mascot, 'Hennes'.",
        "history_summary": "Köln was the first-ever winner of the Bundesliga in 1963-64. The club enjoys a fierce rivalry with nearby Borussia Mönchengladbach and is a yo-yo club between the first and second divisions.",
        "stadium_name": "RheinEnergieStadion",
        "stadium_capacity": 49698,
        "manager_name": "Gerhard Struber"
    },
    {
        "club_name": "Eintracht Frankfurt",
        "description": "A historic club with one of Germany's most passionate and well-traveled fanbases.",
        "history_summary": "Frankfurt's modern highlight was winning the UEFA Europa League in 2022, marking their return to Europe's elite. They reached the European Cup final in 1960, losing to Real Madrid.",
        "stadium_name": "Deutsche Bank Park",
        "stadium_capacity": 58000,
        "manager_name": "Dino Toppmöller"
    },
    {
        "club_name": "Sport-Club Freiburg",
        "description": "A respected club from the Black Forest, known for its smart management, fan ownership, and long-serving managers.",
        "history_summary": "Under legendary manager Volker Finke and later Christian Streich, Freiburg has built a reputation as a stable, overachieving club that frequently develops talent and competes in Europe.",
        "stadium_name": "Europa-Park Stadion",
        "stadium_capacity": 34700,
        "manager_name": "Julian Schuster"
    },
    {
        "club_name": "Hamburger SV",
        "description": "A giant of German football from the port city of Hamburg, currently fighting to return to the top flight.",
        "history_summary": "Hamburger SV won the European Cup in 1983. They were famously the only club to have played in every single Bundesliga season since its founding, until their first-ever relegation in 2018.",
        "stadium_name": "Volksparkstadion",
        "stadium_capacity": 57000,
        "manager_name": "Steffen Baumgart"
    },
    {
        "club_name": "FC St. Pauli",
        "description": "A Hamburg-based club world-famous for its unique, left-leaning social culture and 'Kult' status.",
        "history_summary": "Based in the St. Pauli quarter, the club is more famous for its fanbase and social activism than its on-pitch success. They enjoy a fierce city derby with Hamburger SV.",
        "stadium_name": "Millerntor-Stadion",
        "stadium_capacity": 29546,
        "manager_name": "Alexander Blessin"
    },
    {
        "club_name": "TSG Hoffenheim",
        "description": "A modern club from a small village, backed by software billionaire Dietmar Hopp.",
        "history_summary": "Hoffenheim achieved a remarkable rise, climbing from the fifth tier to the Bundesliga in just eight seasons. They are now an established top-flight side known for their attacking football.",
        "stadium_name": "PreZero Arena",
        "stadium_capacity": 30150,
        "manager_name": "Pellegrino Matarazzo"
    },
    {
        "club_name": "SV Werder Bremen",
        "description": "A historic club from northern Germany, known for its green and white colors and attacking traditions.",
        "history_summary": "Werder Bremen has won the Bundesliga four times and enjoyed a long-standing rivalry with Bayern Munich. They won a league and cup double in 2003-04.",
        "stadium_name": "Weserstadion",
        "stadium_capacity": 42100,
        "manager_name": "Ole Werner"
    },
    {
        "club_name": "1. FC Union Berlin",
        "description": "A club from the German capital with a passionate, dedicated fanbase and a 'cult' following.",
        "history_summary": "From East Berlin, Union has a storied history of resistance. Their rise to the Bundesliga in 2019, and subsequent qualification for the Champions League, is a modern football fairytale.",
        "stadium_name": "Stadion An der Alten Försterei",
        "stadium_capacity": 22012,
        "manager_name": "Bo Svensson"
    },
    {
        "club_name": "FC Augsburg",
        "description": "A Bavarian club that has established itself as a resilient and competitive Bundesliga side.",
        "history_summary": "After reaching the Bundesliga for the first time in 2011, Augsburg has successfully fought to maintain its top-flight status, earning a reputation as a tough survivor.",
        "stadium_name": "WWK Arena",
        "stadium_capacity": 30660,
        "manager_name": "Jess Thorup"
    },
    {
        "club_name": "VfL Wolfsburg",
        "description": "A club from Lower Saxony, backed by the Volkswagen automotive company.",
        "history_summary": "Wolfsburg's greatest achievement was winning the Bundesliga in 2008-09, led by the prolific striking duo of Grafite and Edin Džeko. They are consistently in the mix for European places.",
        "stadium_name": "Volkswagen Arena",
        "stadium_capacity": 28917,
        "manager_name": "Ralph Hasenhüttl"
    },
    {
        "club_name": "1. FSV Mainz 05",
        "description": "A club known for its carnival spirit and for launching the managerial careers of Jürgen Klopp and Thomas Tuchel.",
        "history_summary": "Mainz 05 has established itself as a Bundesliga regular, known for its high-energy, 'Gegenpressing' style of football that was popularized at the club.",
        "stadium_name": "Mewa Arena",
        "stadium_capacity": 33305,
        "manager_name": "Bo Henriksen"
    },
    {
        "club_name": "Borussia Mönchengladbach",
        "description": "A legendary German club that was a dominant force in the 1970s, winning five Bundesliga titles.",
        "history_summary": "Known as 'Die Fohlen' (The Foals) for their fast, attacking style in the 70s, Gladbach was Bayern Munich's greatest rival. They remain a major club with a large fanbase.",
        "stadium_name": "Borussia-Park",
        "stadium_capacity": 54042,
        "manager_name": "Gerardo Seoane"
    },
    {
        "club_name": "FC Heidenheim 1846",
        "description": "A club known for its remarkable and steady climb to the Bundesliga under one manager.",
        "history_summary": "Under long-serving manager Frank Schmidt, Heidenheim made an incredible journey from the lower leagues, culminating in their first-ever promotion to the Bundesliga in 2023.",
        "stadium_name": "Voith-Arena",
        "stadium_capacity": 15000,
        "manager_name": "Frank Schmidt"
    }
]


class Command(BaseCommand):
    help = 'Loads club details for the Bundesliga from an embedded list'

    def handle(self, *args, **kwargs):
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE('Starting to load Bundesliga details...'))

        for item in BUNDESLIGA_DETAILS:
            club_name = item.get('club_name')
            if not club_name:
                self.stdout.write(self.style.WARNING("Skipped item with no 'club_name'."))
                skipped_count += 1
                continue

            try:
                # Find the club in the main Club model
                club = Club.objects.get(name=club_name, league__name="Bundesliga")
                
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
        
        self.stdout.write(self.style.SUCCESS(f"\n--- Bundesliga Details Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))