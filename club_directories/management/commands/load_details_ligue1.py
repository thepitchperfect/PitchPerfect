import json
from django.core.management.base import BaseCommand
from club_directories.models import Club, ClubDetails

# --- Data for all Ligue 1 McDonald's clubs ---
LIGUE_1_DETAILS = [
    {
        "club_name": "Angers SCO",
        "description": "A competitive club from western France, known as 'Les Scoïstes'.",
        "history_summary": "Angers has a history of bouncing between the top two divisions. They are known for their solid team structure and have produced notable talents over the years.",
        "stadium_name": "Stade Raymond Kopa",
        "stadium_capacity": 18752,
        "manager_name": "Alexandre Dujeux"
    },
    {
        "club_name": "FC Lorient",
        "description": "A club from the Brittany region, known for its attractive style of play and distinctive orange kits.",
        "history_summary": "Known as 'Les Merlus' (The Hakes), Lorient won the Coupe de France in 2002. They are recognized for their commitment to an attacking, possession-based philosophy.",
        "stadium_name": "Stade du Moustoir",
        "stadium_capacity": 18110,
        "manager_name": "Olivier Pantaloni"
    },
    {
        "club_name": "Paris Saint-Germain",
        "description": "The dominant force in modern French football, backed by Qatari ownership and global superstars.",
        "history_summary": "Founded in 1970, PSG was transformed in 2011. It has since attracted players like Zlatan Ibrahimović, Neymar, Kylian Mbappé, and Lionel Messi, winning numerous Ligue 1 titles.",
        "stadium_name": "Parc des Princes",
        "stadium_capacity": 47929,
        "manager_name": "Luis Enrique"
    },
    {
        "club_name": "Olympique Marseille",
        "description": "A historic club with a massive, passionate following, and the only French club to win the Champions League.",
        "history_summary": "L'OM's 1993 Champions League victory is their crowning achievement. The club's intense rivalry with PSG, 'Le Classique', is the biggest in French football.",
        "stadium_name": "Stade Vélodrome",
        "stadium_capacity": 67394,
        "manager_name": "Roberto De Zerbi"
    },
    {
        "club_name": "AS Monaco",
        "description": "A club from the principality of Monaco, known for developing world-class talent and competing at the top of Ligue 1.",
        "history_summary": "Despite its small location, Monaco has a history of success, including 8 league titles and a Champions League final appearance in 2004. They famously won the title in 2017 with a young Kylian Mbappé.",
        "stadium_name": "Stade Louis II",
        "stadium_capacity": 16360,
        "manager_name": "Adi Hütter"
    },
    {
        "club_name": "RC Strasbourg Alsace",
        "description": "A historic club from the Alsace region, known for its passionate fanbase and blue and white colors.",
        "history_summary": "Strasbourg has won the Ligue 1 title once, in 1979. After financial troubles, they climbed from the fifth tier back to the top flight, winning the Coupe de la Ligue in 2019.",
        "stadium_name": "Stade de la Meinau",
        "stadium_capacity": 26109,
        "manager_name": "Patrick Vieira"
    },
    {
        "club_name": "LOSC Lille",
        "description": "A top club from northern France, known for its strong defense and superb talent development.",
        "history_summary": "Lille has won four Ligue 1 titles, famously beating PSG to the punch in 2011 (with Eden Hazard) and again in 2021. They are a consistent competitor for European places.",
        "stadium_name": "Decathlon Arena - Stade Pierre-Mauroy",
        "stadium_capacity": 50186,
        "manager_name": "Bruno Génésio"
    },
    {
        "club_name": "OGC Nice",
        "description": "A club from the French Riviera, owned by INEOS, with ambitions to compete at the top of the league.",
        "history_summary": "Nice was a dominant force in the 1950s, winning four league titles. They have seen a resurgence with new investment, regularly challenging for European qualification.",
        "stadium_name": "Allianz Riviera",
        "stadium_capacity": 36178,
        "manager_name": "Franck Haise"
    },
    {
        "club_name": "Stade Rennais FC",
        "description": "A Breton club renowned for having one of the best youth academies in all of Europe.",
        "history_summary": "Rennes' academy has produced a host of stars, including Ousmane Dembélé and Eduardo Camavinga. The club won its first major trophy in 48 years with the Coupe de France in 2019.",
        "stadium_name": "Roazhon Park",
        "stadium_capacity": 29778,
        "manager_name": "Julien Stéphan"
    },
    {
        "club_name": "Olympique Lyon",
        "description": "A club that completely dominated French football in the 2000s and is renowned for its academy.",
        "history_summary": "Lyon won a record seven consecutive Ligue 1 titles from 2002 to 2008. Its academy is one of Europe's best, producing talents like Karim Benzema and Alexandre Lacazette.",
        "stadium_name": "Groupama Stadium",
        "stadium_capacity": 59186,
        "manager_name": "Pierre Sage"
    },
    {
        "club_name": "Paris FC",
        "description": "The 'other' club from Paris, co-existing with PSG and building its own identity.",
        "history_summary": "Paris FC actually merged with Stade Saint-Germain to form PSG in 1970, but split two years later. They have spent most of their history in the lower leagues but are now regulars in Ligue 2, pushing for promotion.",
        "stadium_name": "Stade Charléty",
        "stadium_capacity": 19151,
        "manager_name": "Stéphane Gilli"
    },
    {
        "club_name": "Stade de Reims",
        "description": "A legendary club of French football, a dominant force in the 1950s and two-time European Cup finalist.",
        "history_summary": "Led by the legendary Raymond Kopa, Reims was one of Europe's best teams, reaching the first-ever European Cup final in 1956. They have re-established themselves as a stable Ligue 1 side.",
        "stadium_name": "Stade Auguste-Delaune",
        "stadium_capacity": 20546,
        "manager_name": "Luka Elsner"
    },
    {
        "club_name": "RC Lens",
        "description": "A historic club from northern France, famous for its passionate 'Sang et Or' (Blood and Gold) supporters.",
        "history_summary": "Lens won the Ligue 1 title in 1998. After a period in the second tier, they returned and spectacularly finished second in 2022-23, just one point behind PSG, to qualify for the Champions League.",
        "stadium_name": "Stade Bollaert-Delelis",
        "stadium_capacity": 38223,
        "manager_name": "Will Still"
    },
    {
        "club_name": "FC Toulouse",
        "description": "A club from the south of France known as 'Les Violets' due to their purple kits.",
        "history_summary": "Toulouse has spent most of its recent history in Ligue 1. Their greatest modern achievement was winning the Coupe de France in 2023, earning them a spot in the Europa League.",
        "stadium_name": "Stadium de Toulouse",
        "stadium_capacity": 33150,
        "manager_name": "Carles Martínez Novell"
    },
    {
        "club_name": "FC Nantes",
        "description": "A historic French club with eight Ligue 1 titles, famous for its 'jeu à la nantaise' (Nantes-style play).",
        "history_summary": "Nantes was a dominant force for decades, renowned for its fluid, one-touch attacking football. They won the Coupe de France as recently as 2022.",
        "stadium_name": "Stade de la Beaujoire",
        "stadium_capacity": 35322,
        "manager_name": "Antoine Kombouaré"
    },
    {
        "club_name": "AJ Auxerre",
        "description": "A legendary club from a small town, famous for its long-time manager Guy Roux.",
        "history_summary": "Under Guy Roux, who managed the club for an astonishing 44 years, Auxerre rose from a small regional team to win a historic Ligue 1 and Coupe de France double in 1996.",
        "stadium_name": "Stade de l'Abbé-Deschamps",
        "stadium_capacity": 17924,
        "manager_name": "Christophe Pélissier"
    },
    {
        "club_name": "FC Metz",
        "description": "A club from the Lorraine region, known for its strong academy and frequent spells in Ligue 1.",
        "history_summary": "Metz has a reputation as a 'yo-yo club', moving between the top two divisions. Its academy is well-regarded, having produced players like Miralem Pjanić and Sadio Mané.",
        "stadium_name": "Stade Saint-Symphorien",
        "stadium_capacity": 28786,
        "manager_name": "Stéphane Le Mignan"
    },
    {
        "club_name": "Le Havre AC",
        "description": "The oldest active professional football club in France, based in the port city of Le Havre.",
        "history_summary": "Founded in 1872, 'Le club doyen' (the senior club) has a rich history and is also known for an excellent academy that produced talents like Paul Pogba and Riyad Mahrez.",
        "stadium_name": "Stade Océane",
        "stadium_capacity": 25178,
        "manager_name": "Didier Digard"
    }
]


class Command(BaseCommand):
    help = "Loads club details for Ligue 1 McDonald's from an embedded list"

    def handle(self, *args, **kwargs):
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE("Starting to load Ligue 1 McDonald's details..."))

        for item in LIGUE_1_DETAILS:
            club_name = item.get('club_name')
            if not club_name:
                self.stdout.write(self.style.WARNING("Skipped item with no 'club_name'."))
                skipped_count += 1
                continue

            try:
                # Find the club in the main Club model
                club = Club.objects.get(name=club_name, league__name="Ligue 1 McDonald's")
                
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
        
        self.stdout.write(self.style.SUCCESS(f"\n--- Ligue 1 McDonald's Details Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))