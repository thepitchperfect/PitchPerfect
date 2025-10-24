import json
from django.core.management.base import BaseCommand
from club_directories.models import Club, ClubDetails

# --- Data for all Primeira Liga clubs ---
PRIMEIRA_LIGA_DETAILS = [
    {
        "club_name": "FC Porto",
        "description": "One of Portugal's 'Big Three' clubs, with a strong history of domestic and European success.",
        "history_summary": "Porto has won the UEFA Champions League twice, first in 1987 and most famously in 2004 under manager José Mourinho. They are known for their exceptional scouting network.",
        "stadium_name": "Estádio do Dragão",
        "stadium_capacity": 50033,
        "manager_name": "Vítor Bruno"
    },
    {
        "club_name": "Sporting CP",
        "description": "A 'Big Three' club from Lisbon, famous for its world-class academy that produced Cristiano Ronaldo.",
        "history_summary": "Sporting's academy is legendary, having also produced Luís Figo and Rafael Leão. They broke a 19-year title drought by winning the Primeira Liga in 2020-21.",
        "stadium_name": "Estádio José Alvalade",
        "stadium_capacity": 50095,
        "manager_name": "Rúben Amorim"
    },
    {
        "club_name": "Benfica",
        "description": "The most decorated and widely supported club in Portugal, also one of the 'Big Three'.",
        "history_summary": "Based in Lisbon, Benfica has won the most Primeira Liga titles. They won back-to-back European Cups in 1961 and 1962, led by the legendary Eusébio.",
        "stadium_name": "Estádio da Luz",
        "stadium_capacity": 64642,
        "manager_name": "Roger Schmidt"
    },
    {
        "club_name": "SC Braga",
        "description": "A top Portuguese club that consistently challenges the 'Big Three' for domestic honors and European places.",
        "history_summary": "Known as 'Os Arcebispos' (The Archbishops), Braga has established itself as the 'best of the rest' in Portugal. They reached the UEFA Europa League final in 2011.",
        "stadium_name": "Estádio Municipal de Braga",
        "stadium_capacity": 30286,
        "manager_name": "Artur Jorge"
    }
]


class Command(BaseCommand):
    help = 'Loads club details for the Primeira Liga from an embedded list'

    def handle(self, *args, **kwargs):
        
        created_count = 0
        updated_count = 0
        skipped_count = 0

        self.stdout.write(self.style.NOTICE('Starting to load Primeira Liga details...'))

        for item in PRIMEIRA_LIGA_DETAILS:
            club_name = item.get('club_name')
            if not club_name:
                self.stdout.write(self.style.WARNING("Skipped item with no 'club_name'."))
                skipped_count += 1
                continue

            try:
                # Find the club in the main Club model
                club = Club.objects.get(name=club_name, league__name="Primeira Liga")
                
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
        
        self.stdout.write(self.style.SUCCESS(f"\n--- Primeira Liga Details Summary ---"))
        self.stdout.write(self.style.SUCCESS(f"Successfully created: {created_count}"))
        self.stdout.write(self.style.SUCCESS(f"Successfully updated: {updated_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))