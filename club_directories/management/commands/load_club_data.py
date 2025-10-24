import json
from django.core.management.base import BaseCommand
from club_directories.models import League, Club

LEAGUES_DATA = {
    "Premier League": {"region": "UK", "logo_path": "images/leagues/premier_league.png"},
    "La Liga": {"region": "Spain", "logo_path": "images/leagues/la_liga.png"},
    "Bundesliga": {"region": "Germany", "logo_path": "images/leagues/bundesliga.png"},
    "Serie A": {"region": "Italy", "logo_path": "images/leagues/serie_a.png"},
    "Ligue 1 McDonald's": {"region": "France", "logo_path": "images/leagues/ligue_1.png"},
    "Primeira Liga": {"region": "Portugal", "logo_path": "images/leagues/primeira_liga.png"},
}

CLUBS_DATA = [
    {"name": "Arsenal", "league_name": "Premier League", "year": 1886, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/320px-Arsenal_FC.svg.png"},
    {"name": "Aston Villa", "league_name": "Premier League", "year": 1874, "logo": "https://football-logos.cc/logos/england/700x700/aston-villa.png"},
    {"name": "AFC Bournemouth", "league_name": "Premier League", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/AFC_Bournemouth_%282013%29.svg/240px-AFC_Bournemouth_%282013%29.svg.png"},
    {"name": "Brentford", "league_name": "Premier League", "year": 1889, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Brentford_FC_crest.svg/300px-Brentford_FC_crest.svg.png"},
    {"name": "Brighton & Hove Albion", "league_name": "Premier League", "year": 1901, "logo": "https://football-logos.cc/logos/england/700x700/brighton.png"},
    {"name": "Burnley", "league_name": "Premier League", "year": 1882, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/Burnley_FC_Logo.svg/300px-Burnley_FC_Logo.svg.png"},
    {"name": "Chelsea", "league_name": "Premier League", "year": 1905, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/300px-Chelsea_FC.svg.png"},
    {"name": "Crystal Palace", "league_name": "Premier League", "year": 1905, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/Crystal_Palace_FC_logo_%282022%29.svg/270px-Crystal_Palace_FC_logo_%282022%29.svg.png"},
    {"name": "Everton", "league_name": "Premier League", "year": 1878, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7c/Everton_FC_logo.svg/315px-Everton_FC_logo.svg.png"},
    {"name": "Fulham", "league_name": "Premier League", "year": 1879, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Fulham_FC_%28shield%29.svg/320px-Fulham_FC_%28shield%29.svg.png"},
    {"name": "Leeds United", "league_name": "Premier League", "year": 1919, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/54/Leeds_United_F.C._logo.svg/300px-Leeds_United_F.C._logo.svg.png"},
    {"name": "Liverpool", "league_name": "Premier League", "year": 1892, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/300px-Liverpool_FC.svg.png"},
    {"name": "Manchester City", "league_name": "Premier League", "year": 1880, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/315px-Manchester_City_FC_badge.svg.png"},
    {"name": "Manchester United", "league_name": "Premier League", "year": 1878, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/300px-Manchester_United_FC_crest.svg.png"},
    {"name": "Newcastle United", "league_name": "Premier League", "year": 1892, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Newcastle_United_Logo.svg/430px-Newcastle_United_Logo.svg.png"},
    {"name": "Nottingham Forest", "league_name": "Premier League", "year": 1865, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/Nottingham_Forest_F.C._logo.svg/300px-Nottingham_Forest_F.C._logo.svg.png"},
    {"name": "Sunderland", "league_name": "Premier League", "year": 1879, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/77/Logo_Sunderland.svg/300px-Logo_Sunderland.svg.png"},
    {"name": "Tottenham Hotspur", "league_name": "Premier League", "year": 1882, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b4/Tottenham_Hotspur.svg/260px-Tottenham_Hotspur.svg.png"},
    {"name": "West Ham United", "league_name": "Premier League", "year": 1895, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/West_Ham_United_FC_logo.svg/278px-West_Ham_United_FC_logo.svg.png"},
    {"name": "Wolverhampton Wanderers", "league_name": "Premier League", "year": 1877, "logo": "https://football-logos.cc/logos/england/700x700/wolves.png"},
    {"name": "Real Madrid", "league_name": "La Liga", "year": 1902, "logo": "https://football-logos.cc/logos/spain/700x700/real-madrid.png"},
    {"name": "FC Barcelona", "league_name": "La Liga", "year": 1899, "logo": "https://football-logos.cc/logos/spain/700x700/barcelona.png"},
    {"name": "Villarreal CF", "league_name": "La Liga", "year": 1923, "logo": "https://football-logos.cc/logos/spain/700x700/villarreal.png"},
    {"name": "Real Betis Seville", "league_name": "La Liga", "year": 1907, "logo": "https://football-logos.cc/logos/spain/700x700/real-betis.png"},
    {"name": "Atletico Madrid", "league_name": "La Liga", "year": 1903, "logo": "https://football-logos.cc/logos/spain/700x700/atletico-madrid.png"},
    {"name": "Sevilla FC", "league_name": "La Liga", "year": 1890, "logo": "https://football-logos.cc/logos/spain/700x700/sevilla.png"},
    {"name": "Elche CF", "league_name": "La Liga", "year": 1923, "logo": "https://football-logos.cc/logos/spain/700x700/elche.png"},
    {"name": "Athletic Bilbao", "league_name": "La Liga", "year": 1898, "logo": "https://football-logos.cc/logos/spain/700x700/athletic-club.png"},
    {"name": "Espanyol Barcelona", "league_name": "La Liga", "year": 1900, "logo": "https://football-logos.cc/logos/spain/700x700/espanyol.png"},
    {"name": "Deportivo Alaves", "league_name": "La Liga", "year": 1921, "logo": "https://football-logos.cc/logos/spain/700x700/deportivo.png"},
    {"name": "Getafe CF", "league_name": "La Liga", "year": 1983, "logo": "https://football-logos.cc/logos/spain/700x700/getafe.png"},
    {"name": "CA Osasuna", "league_name": "La Liga", "year": 1920, "logo": "https://football-logos.cc/logos/spain/700x700/osasuna.png"},
    {"name": "Levante UD", "league_name": "La Liga", "year": 1909, "logo": "https://football-logos.cc/logos/spain/700x700/levante.png"},
    {"name": "Rayo Vallecano", "league_name": "La Liga", "year": 1924, "logo": "https://football-logos.cc/logos/spain/700x700/rayo-vallecano.png"},
    {"name": "Valencia CF", "league_name": "La Liga", "year": 1919, "logo": "https://football-logos.cc/logos/spain/700x700/valencia.png"},
    {"name": "RC Celta de Vigo", "league_name": "La Liga", "year": 1923, "logo": "https://football-logos.cc/logos/spain/700x700/celta.png"},
    {"name": "Real Oviedo", "league_name": "La Liga", "year": 1926, "logo": "https://football-logos.cc/logos/spain/700x700/oviedo.png"},
    {"name": "Girona FC", "league_name": "La Liga", "year": 1930, "logo": "https://football-logos.cc/logos/spain/700x700/girona.png"},
    {"name": "Real Sociedad San Sebastian", "league_name": "La Liga", "year": 1909, "logo": "https://football-logos.cc/logos/spain/700x700/real-sociedad.png"},
    {"name": "RCD Mallorca", "league_name": "La Liga", "year": 1916, "logo": "https://football-logos.cc/logos/spain/700x700/mallorca.png"},
    {"name": "FC Bayern München", "league_name": "Bundesliga", "year": 1900, "logo": "https://football-logos.cc/logos/germany/700x700/bayern-munchen.png"},
    {"name": "Borussia Dortmund", "league_name": "Bundesliga", "year": 1909, "logo": "https://football-logos.cc/logos/germany/700x700/borussia-dortmund.png"},
    {"name": "RB Leipzig", "league_name": "Bundesliga", "year": 2009, "logo": "https://football-logos.cc/logos/germany/700x700/rb-leipzig.png"},
    {"name": "VfB Stuttgart", "league_name": "Bundesliga", "year": 1893, "logo": "https://football-logos.cc/logos/germany/700x700/vfb-stuttgart.png"},
    {"name": "Bayer 04 Leverkusen", "league_name": "Bundesliga", "year": 1904, "logo": "https://football-logos.cc/logos/germany/700x700/bayer-leverkusen.png"},
    {"name": "1. FC Köln", "league_name": "Bundesliga", "year": 1948, "logo": "https://football-logos.cc/logos/germany/700x700/koln.png"},
    {"name": "Eintracht Frankfurt", "league_name": "Bundesliga", "year": 1899, "logo": "https://football-logos.cc/logos/germany/700x700/eintracht-frankfurt.png"},
    {"name": "Sport-Club Freiburg", "league_name": "Bundesliga", "year": 1904, "logo": "https://football-logos.cc/logos/germany/700x700/freiburg.png"},
    {"name": "Hamburger SV", "league_name": "Bundesliga", "year": 1887, "logo": "https://football-logos.cc/logos/germany/700x700/hamburger-sv.png"},
    {"name": "FC St. Pauli", "league_name": "Bundesliga", "year": 1910, "logo": "https://football-logos.cc/logos/germany/700x700/st-pauli.png"},
    {"name": "TSG Hoffenheim", "league_name": "Bundesliga", "year": 1899, "logo": "https://football-logos.cc/logos/germany/700x700/hoffenheim.png"},
    {"name": "SV Werder Bremen", "league_name": "Bundesliga", "year": 1899, "logo": "https://football-logos.cc/logos/germany/700x700/werder-bremen.png"},
    {"name": "1. FC Union Berlin", "league_name": "Bundesliga", "year": 1966, "logo": "https://football-logos.cc/logos/germany/700x700/union-berlin.png"},
    {"name": "FC Augsburg", "league_name": "Bundesliga", "year": 1907, "logo": "https://football-logos.cc/logos/germany/700x700/augsburg.png"},
    {"name": "VfL Wolfsburg", "league_name": "Bundesliga", "year": 1945, "logo": "https://football-logos.cc/logos/germany/700x700/wolfsburg.png"},
    {"name": "1. FSV Mainz 05", "league_name": "Bundesliga", "year": 1905, "logo": "https://football-logos.cc/logos/germany/700x700/mainz-05.png"},
    {"name": "Borussia Mönchengladbach", "league_name": "Bundesliga", "year": 1900, "logo": "https://football-logos.cc/logos/germany/700x700/borussia-monchengladbach.png"},
    {"name": "FC Heidenheim 1846", "league_name": "Bundesliga", "year": 1846, "logo": "https://football-logos.cc/logos/germany/700x700/fc-heidenheim.png"},
    {"name": "Atalanta", "league_name": "Serie A", "year": 1907, "logo": "https://football-logos.cc/logos/italy/700x700/atalanta.png"},
    {"name": "AC Milan", "league_name": "Serie A", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/300px-Logo_of_AC_Milan.svg.png"},
    {"name": "Bologna FC", "league_name": "Serie A", "year": 1909, "logo": "https://football-logos.cc/logos/italy/700x700/bologna.png"},
    {"name": "Cagliari Calcio", "league_name": "Serie A", "year": 1920, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/61/Cagliari_Calcio_1920.svg/350px-Cagliari_Calcio_1920.svg.png"},
    {"name": "FC Empoli", "league_name": "Serie A", "year": 1920, "logo": "https://football-logos.cc/logos/italy/700x700/empoli.png"},
    {"name": "Fiorentina", "league_name": "Serie A", "year": 1926, "logo": "https://football-logos.cc/logos/italy/700x700/fiorentina.png"},
    {"name": "Genoa CFC", "league_name": "Serie A", "year": 1893, "logo": "https://football-logos.cc/logos/italy/700x700/genoa.png"},
    {"name": "Hellas Verona", "league_name": "Serie A", "year": 1903, "logo": "https://football-logos.cc/logos/italy/700x700/verona.png"},
    {"name": "Inter Milan", "league_name": "Serie A", "year": 1908, "logo": "https://football-logos.cc/logos/italy/700x700/inter.png"},
    {"name": "Juventus FC", "league_name": "Serie A", "year": 1897, "logo": "https://football-logos.cc/logos/italy/700x700/juventus.png"},
    {"name": "Lazio", "league_name": "Serie A", "year": 1900, "logo": "https://football-logos.cc/logos/italy/700x700/lazio.png"},
    {"name": "US Lecce", "league_name": "Serie A", "year": 1908, "logo": "https://football-logos.cc/logos/italy/700x700/lecce.png"},
    {"name": "Monza", "league_name": "Serie A", "year": 1912, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/AC_Monza_logo_%282021%29.svg/300px-AC_Monza_logo_%282021%29.svg.png"},
    {"name": "Napoli", "league_name": "Serie A", "year": 1926, "logo": "https://football-logos.cc/logos/italy/700x700/napoli.png"},
    {"name": "Parma", "league_name": "Serie A", "year": 1913, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Logo_Parma_Calcio_1913_%28adozione_2016%29.svg/320px-Logo_Parma_Calcio_1913_%28adozione_2016%29.svg.png"},
    {"name": "Sassuolo", "league_name": "Serie A", "year": 1920, "logo": "https://football-logos.cc/logos/italy/700x700/sassuolo.png"},
    {"name": "Torino FC", "league_name": "Serie A", "year": 1906, "logo": "https://football-logos.cc/logos/italy/700x700/torino.png"},
    {"name": "Udinese", "league_name": "Serie A", "year": 1896, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Udinese_Calcio_logo.svg/420px-Udinese_Calcio_logo.svg.png"},
    {"name": "AS Roma", "league_name": "Serie A", "year": 1927, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/AS_Roma_logo_%282017%29.svg/350px-AS_Roma_logo_%282017%29.svg.png"},
    {"name": "Venezia FC", "league_name": "Serie A", "year": 1907, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/3/39/Venezia_FC_crest.svg/220px-Venezia_FC_crest.svg.png"},
    {"name": "Angers SCO", "league_name": "Ligue 1 McDonald's", "year": 1919, "logo": "https://football-logos.cc/logos/france/700x700/angers.png"},
    {"name": "FC Lorient", "league_name": "Ligue 1 McDonald's", "year": 1926, "logo": "https://football-logos.cc/logos/france/700x700/lorient.png"},
    {"name": "Paris Saint-Germain", "league_name": "Ligue 1 McDonald's", "year": 1970, "logo": "https://football-logos.cc/logos/france/700x700/paris-saint-germain.png"},
    {"name": "Olympique Marseille", "league_name": "Ligue 1 McDonald's", "year": 1899, "logo": "https://football-logos.cc/logos/france/700x700/marseille.png"},
    {"name": "AS Monaco", "league_name": "Ligue 1 McDonald's", "year": 1924, "logo": "https://football-logos.cc/logos/france/700x700/as-monaco.png"},
    {"name": "RC Strasbourg Alsace", "league_name": "Ligue 1 McDonald's", "year": 1906, "logo": "https://football-logos.cc/logos/france/700x700/rc-strasbourg-alsace.png"},
    {"name": "LOSC Lille", "league_name": "Ligue 1 McDonald's", "year": 1944, "logo": "https://football-logos.cc/logos/france/700x700/lille.png"},
    {"name": "OGC Nice", "league_name": "Ligue 1 McDonald's", "year": 1904, "logo": "https://football-logos.cc/logos/france/700x700/nice.png"},
    {"name": "Stade Rennais FC", "league_name": "Ligue 1 McDonald's", "year": 1901, "logo": "https://football-logos.cc/logos/france/700x700/rennes.png"},
    {"name": "Olympique Lyon", "league_name": "Ligue 1 McDonald's", "year": 1899, "logo": "https://football-logos.cc/logos/france/700x700/lyon.png"},
    {"name": "Paris FC", "league_name": "Ligue 1 McDonald's", "year": 1969, "logo": "https://football-logos.cc/logos/france/700x700/paris-fc.png"},
    {"name": "Stade de Reims", "league_name": "Ligue 1 McDonald's", "year": 1931, "logo": "https://football-logos.cc/logos/france/700x700/stade-de-reims.png"}, 
    {"name": "RC Lens", "league_name": "Ligue 1 McDonald's", "year": 1906, "logo": "https://football-logos.cc/logos/france/700x700/rc-lens.png"},
    {"name": "FC Toulouse", "league_name": "Ligue 1 McDonald's", "year": 1937, "logo": "https://football-logos.cc/logos/france/700x700/toulouse.png"}, 
    {"name": "FC Nantes", "league_name": "Ligue 1 McDonald's", "year": 1943, "logo": "https://football-logos.cc/logos/france/700x700/nantes.png"}, 
    {"name": "AJ Auxerre", "league_name": "Ligue 1 McDonald's", "year": 1905, "logo": "https://football-logos.cc/logos/france/700x700/auxerre.png"},
    {"name": "FC Metz", "league_name": "Ligue 1 McDonald's", "year": 1932, "logo": "https://football-logos.cc/logos/france/700x700/fc-metz.png"},
    {"name": "Le Havre AC", "league_name": "Ligue 1 McDonald's", "year": 1872, "logo": "https://football-logos.cc/logos/france/700x700/le-havre-ac.png"},
    {"name": "FC Porto", "league_name": "Primeira Liga", "year": 1893, "logo": "https://football-logos.cc/logos/portugal/700x700/fc-porto.png"},
    {"name": "Sporting CP", "league_name": "Primeira Liga", "year": 1906, "logo": "https://football-logos.cc/logos/portugal/700x700/sporting-cp.png"},
    {"name": "Benfica", "league_name": "Primeira Liga", "year": 1904, "logo": "https://football-logos.cc/logos/portugal/700x700/benfica.png"},
    {"name": "SC Braga", "league_name": "Primeira Liga", "year": 1921, "logo": "https://football-logos.cc/logos/portugal/700x700/sc-braga.png"},
]


class Command(BaseCommand):
    help = 'Loads initial league and club data from a predefined list.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Deleting existing club and league data...'))
        Club.objects.all().delete()
        League.objects.all().delete()

        self.stdout.write(self.style.NOTICE('Creating leagues...'))
        league_objects = {}
        for league_name, league_data in LEAGUES_DATA.items():
            league = League.objects.create(
                name=league_name,
                region=league_data['region'],
                logo_path=league_data['logo_path']
            )
            league_objects[league_name] = league
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {len(league_objects)} leagues.'))

        self.stdout.write(self.style.NOTICE('Creating clubs...'))
        clubs_created_count = 0
        for club_data in CLUBS_DATA:
            league_name = club_data.get('league_name')
            league_obj = league_objects.get(league_name)

            if not league_obj:
                self.stdout.write(self.style.ERROR(f"Could not find league '{league_name}' for club '{club_data['name']}'. Skipping."))
                continue

            Club.objects.create(
                name=club_data['name'],
                league=league_obj,
                founded_year=club_data.get('year'),
                logo_url=club_data.get('logo')
            )
            clubs_created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {clubs_created_count} clubs.'))
        self.stdout.write(self.style.SUCCESS('All data loaded successfully!'))

