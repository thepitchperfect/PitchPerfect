import openpyxl
from django.core.management.base import BaseCommand
from club_directories.models import Club
from statisticsrafi.models import TeamStatistics
from decimal import Decimal


class Command(BaseCommand):
    help = 'Load team statistics from Excel file'

    def handle(self, *args, **options):
        file_path = 'statisticsrafi/assets/all_club_team_stats.xlsx'
        
        try:
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            # Get all rows (skip header)
            rows = list(ws.rows)[1:]  # Skip the header row
            
            loaded_count = 0
            skipped_count = 0
            
            # Special name mappings for clubs with different names in Excel vs Database
            name_mappings = {
                'reial-club-deportiu-espanyol': 'Espanyol Barcelona',
                'rennes': 'Stade Rennais FC',
                'koln': '1. FC Köln',
                'fc-bayern-munchen': 'FC Bayern München',
                '1-fsv-mainz-05': '1. FSV Mainz 05',
                'borussia-vfl-monchengladbach': 'Borussia Mönchengladbach',
                'fc-st-pauli': 'FC St. Pauli',
                'le-havre': 'Le Havre AC',
                'olympique-de-marseille': 'Olympique Marseille',
                'paris-saint-germain-fc': 'Paris Saint-Germain',
                'real-club-celta-de-vigo': 'RC Celta de Vigo',
                'real-club-deportivo-mallorca': 'RCD Mallorca',
                'real-sociedad': 'Real Sociedad San Sebastian',
                'sporting-braga': 'SC Braga',
            }
            
            for row in rows:
                team_name = row[0].value
                if not team_name:
                    continue
                
                # Check if this is a special case
                if team_name.lower() in name_mappings:
                    try:
                        club = Club.objects.get(name=name_mappings[team_name.lower()])
                    except Club.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Club not found: {team_name} (mapped to: {name_mappings[team_name.lower()]})'))
                        skipped_count += 1
                        continue
                else:
                    # Normalize team name (remove hyphens, capitalize properly)
                    normalized_name = team_name.replace('-', ' ').title()
                    
                    # Try to find the club
                    club = None
                    try:
                        # Try exact match first
                        club = Club.objects.get(name__iexact=normalized_name)
                    except Club.DoesNotExist:
                        # Try with original name
                        try:
                            club = Club.objects.get(name__iexact=team_name)
                        except Club.DoesNotExist:
                            # Try partial match
                            clubs = Club.objects.filter(name__icontains=normalized_name.split()[0])
                            if clubs.exists():
                                club = clubs.first()
                            else:
                                self.stdout.write(self.style.WARNING(f'Club not found: {team_name} (tried: {normalized_name})'))
                                skipped_count += 1
                                continue
                
                def parse_percentage(value):
                    """Convert percentage string like '75%' to decimal like 75.00"""
                    if value and isinstance(value, str):
                        return Decimal(value.replace('%', '').strip())
                    elif value and isinstance(value, (int, float)):
                        return Decimal(str(value))
                    return None
                
                def parse_decimal(value):
                    """Convert string to decimal"""
                    if value:
                        try:
                            return Decimal(str(value))
                        except:
                            return None
                    return None
                
                def parse_int_from_percentage(value):
                    """Convert percentage like '75%' to count out of 8 games"""
                    if value and isinstance(value, str) and '%' in value:
                        percentage = float(value.replace('%', '').strip())
                        # Assuming 8 games played, calculate number of games
                        return int(round(percentage / 100 * 8))
                    return 0
                
                # Create or update team statistics
                team_stats, created = TeamStatistics.objects.update_or_create(
                    club=club,
                    season='2025/26',
                    defaults={
                        'wins': parse_int_from_percentage(row[1].value),
                        'draws': parse_int_from_percentage(row[2].value),
                        'losses': parse_int_from_percentage(row[3].value),
                        'xg_for_per_match': parse_decimal(row[4].value),
                        'xg_against_per_match': parse_decimal(row[5].value),
                        'scored_per_match': parse_decimal(row[6].value),
                        'conceded_per_match': parse_decimal(row[7].value),
                        'avg_match_goals': parse_decimal(row[8].value),
                        'clean_sheets_percentage': parse_percentage(row[9].value),
                        'failed_to_score_percentage': parse_percentage(row[10].value),
                        'possession_avg': parse_percentage(row[11].value),
                        'shots_taken_per_match': parse_decimal(row[12].value),
                        'shots_conversion_rate': parse_percentage(row[13].value),
                        'fouls_committed_per_match': parse_decimal(row[14].value),
                        'fouled_against_per_match': parse_decimal(row[15].value),
                        'penalties_won': str(row[16].value or ''),
                        'penalties_conceded': str(row[17].value or ''),
                        'goal_kicks_per_match': parse_decimal(row[18].value),
                        'throw_ins_per_match': parse_decimal(row[19].value),
                        'free_kicks_per_match': parse_decimal(row[20].value),
                    }
                )
                
                action = "Created" if created else "Updated"
                self.stdout.write(self.style.SUCCESS(f'{action} statistics for {club.name}'))
                loaded_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'\n✓ Successfully loaded {loaded_count} team statistics'))
            if skipped_count > 0:
                self.stdout.write(self.style.WARNING(f'⚠ Skipped {skipped_count} teams (club not found)'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading team statistics: {str(e)}'))
            import traceback
            traceback.print_exc()
