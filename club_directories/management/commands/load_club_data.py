import json
from django.core.management.base import BaseCommand
from club_directories.models import League, Club

LEAGUES_DATA = {
    "Premier League": {"region": "UK", "logo_path": "images/leagues/premier_league.png"},
    "La Liga": {"region": "Spain", "logo_path": "images/leagues/la_liga.png"},
    "Bundesliga": {"region": "Germany", "logo_path": "images/leagues/bundesliga.png"},
    "Serie A": {"region": "Italy", "logo_path": "images/leagues/serieabc.png"},
    "Ligue 1 McDonald's": {"region": "France", "logo_path": "images/leagues/ligue_1.png"},
    "Primeira Liga": {"region": "Portugal", "logo_path": "images/leagues/primeira_liga.png"},
}

CLUBS_DATA = [
    # Premier League
    {"name": "Arsenal", "league_name": "Premier League", "year": 1886, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/53/Arsenal_FC.svg/270px-Arsenal_FC.svg.png"},
    {"name": "Aston Villa", "league_name": "Premier League", "year": 1874, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Aston_Villa_FC_new_crest.svg/320px-Aston_Villa_FC_new_crest.svg.png"},
    {"name": "AFC Bournemouth", "league_name": "Premier League", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/AFC_Bournemouth_%282013%29.svg/240px-AFC_Bournemouth_%282013%29.svg.png"},
    {"name": "Brentford", "league_name": "Premier League", "year": 1889, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2a/Brentford_FC_crest.svg/300px-Brentford_FC_crest.svg.png"},
    {"name": "Brighton & Hove Albion", "league_name": "Premier League", "year": 1901, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d0/Brighton_and_Hove_Albion_FC_crest.svg/315px-Brighton_and_Hove_Albion_FC_crest.svg.png"},
    {"name": "Burnley", "league_name": "Premier League", "year": 1982, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/Burnley_FC_Logo.svg/300px-Burnley_FC_Logo.svg.png"},
    {"name": "Chelsea", "league_name": "Premier League", "year": 1905, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/323px-Chelsea_FC.svg.png"},
    {"name": "Crystal Palace", "league_name": "Premier League", "year": 1905, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a2/Crystal_Palace_FC_logo_%282022%29.svg/278px-Crystal_Palace_FC_logo_%282022%29.svg.png"},
    {"name": "Everton", "league_name": "Premier League", "year": 1878, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7c/Everton_FC_logo.svg/315px-Everton_FC_logo.svg.png"},
    {"name": "Fulham", "league_name": "Premier League", "year": 1979, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Fulham_FC_%28shield%29.svg/320px-Fulham_FC_%28shield%29.svg.png"},
    {"name": "Leeds United", "league_name": "Premier League", "year": 1919, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/54/Leeds_United_F.C._logo.svg/255px-Leeds_United_F.C._logo.svg.png"},
    {"name": "Liverpool", "league_name": "Premier League", "year": 1892, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/Liverpool_FC.svg/300px-Liverpool_FC.svg.png"},
    {"name": "Manchester City", "league_name": "Premier League", "year": 1880, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/eb/Manchester_City_FC_badge.svg/315px-Manchester_City_FC_badge.svg.png"},
    {"name": "Manchester United", "league_name": "Premier League", "year": 1878, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7a/Manchester_United_FC_crest.svg/300px-Manchester_United_FC_crest.svg.png"},
    {"name": "Newcastle United", "league_name": "Premier League", "year": 1881, "logo": "https://cdn.freebiesupply.com/logos/large/2x/newcastle-united-logo-png-transparent.png"},
    {"name": "Nottingham Forest", "league_name": "Premier League", "year": 1865, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/e/e5/Nottingham_Forest_F.C._logo.svg/180px-Nottingham_Forest_F.C._logo.svg.png"},
    {"name": "Sunderland", "league_name": "Premier League", "year": 1879, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/77/Logo_Sunderland.svg/390px-Logo_Sunderland.svg.png"},
    {"name": "Tottenham Hotspur", "league_name": "Premier League", "year": 1882, "logo": "https://th.bing.com/th/id/R.c465d167d3f7591a1da6964d6fb222d6?rik=epfyyGvwvi3OWw&riu=http%3a%2f%2flogos-download.com%2fwp-content%2fuploads%2f2016%2f05%2fTottenham_Hotspur_logo_crest_logotype.png&ehk=PTNZIqgoxQX9C164pPgpBAG9WfwVYtcF%2bjJuIHcmTdk%3d&risl=&pid=ImgRaw&r=0"},
    {"name": "West Ham United", "league_name": "Premier League", "year": 1895, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/West_Ham_United_FC_logo.svg/278px-West_Ham_United_FC_logo.svg.png"},
    {"name": "Wolverhampton Wanderers", "league_name": "Premier League", "year": 1877, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c9/Wolverhampton_Wanderers_FC_crest.svg/330px-Wolverhampton_Wanderers_FC_crest.svg.png"},
    
    # La Liga
    {"name": "Real Madrid", "league_name": "La Liga", "year": 1902, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/56/Real_Madrid_CF.svg/255px-Real_Madrid_CF.svg.png"},
    {"name": "FC Barcelona", "league_name": "La Liga", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/FC_Barcelona_%28crest%29.svg/345px-FC_Barcelona_%28crest%29.svg.png"},
    {"name": "Villarreal CF", "league_name": "La Liga", "year": 1923, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/b/b9/Villarreal_CF_logo-en.svg/278px-Villarreal_CF_logo-en.svg.png"},
    {"name": "Real Betis Seville", "league_name": "La Liga", "year": 1907, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/13/Real_betis_logo.svg/345px-Real_betis_logo.svg.png"},
    {"name": "Atletico Madrid", "league_name": "La Liga", "year": 1903, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Atletico_Madrid_Logo_2024.svg/330px-Atletico_Madrid_Logo_2024.svg.png"},
    {"name": "Sevilla FC", "league_name": "La Liga", "year": 1890, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/3/3b/Sevilla_FC_logo.svg/255px-Sevilla_FC_logo.svg.png"},
    {"name": "Elche CF", "league_name": "La Liga", "year": 1923, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/Elche_CF_logo.svg/255px-Elche_CF_logo.svg.png"},
    {"name": "Athletic Bilbao", "league_name": "La Liga", "year": 1898, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/9/98/Club_Athletic_Bilbao_logo.svg/270px-Club_Athletic_Bilbao_logo.svg.png"},
    {"name": "Espanyol Barcelona", "league_name": "La Liga", "year": 1900, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/9/92/RCD_Espanyol_crest.svg/320px-RCD_Espanyol_crest.svg.png"},
    {"name": "Deportivo Alaves", "league_name": "La Liga", "year": 1921, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f8/Deportivo_Alaves_logo_%282020%29.svg/315px-Deportivo_Alaves_logo_%282020%29.svg.png"},
    {"name": "Getafe CF", "league_name": "La Liga", "year": 1983, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/4/46/Getafe_logo.svg/300px-Getafe_logo.svg.png"},
    {"name": "CA Osasuna", "league_name": "La Liga", "year": 1920, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/3/38/CA_Osasuna_2024_crest.svg/330px-CA_Osasuna_2024_crest.svg.png"},
    {"name": "Levante UD", "league_name": "La Liga", "year": 1909, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7b/Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg/270px-Levante_Uni%C3%B3n_Deportiva%2C_S.A.D._logo.svg.png"},
    {"name": "Rayo Vallecano", "league_name": "La Liga", "year": 1924, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/d/d8/Rayo_Vallecano_logo.svg/315px-Rayo_Vallecano_logo.svg.png"},
    {"name": "Valencia CF", "league_name": "La Liga", "year": 1919, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Valenciacf.svg/278px-Valenciacf.svg.png"},
    {"name": "RC Celta de Vigo", "league_name": "La Liga", "year": 1923, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/12/RC_Celta_de_Vigo_logo.svg/225px-RC_Celta_de_Vigo_logo.svg.png"},
    {"name": "Real Oviedo", "league_name": "La Liga", "year": 1926, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/6e/Real_Oviedo_logo.svg/240px-Real_Oviedo_logo.svg.png"},
    {"name": "Girona FC", "league_name": "La Liga", "year": 1930, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/Girona_FC_Logo.svg/300px-Girona_FC_Logo.svg.png"},
    {"name": "Real Sociedad San Sebastian", "league_name": "La Liga", "year": 1909, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f1/Real_Sociedad_logo.svg/278px-Real_Sociedad_logo.svg.png"},
    {"name": "RCD Mallorca", "league_name": "La Liga", "year": 1916, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/e/e0/Rcd_mallorca.svg/580px-Rcd_mallorca.svg.png"},

    # Bundesliga
    {"name": "FC Bayern München", "league_name": "Bundesliga", "year": 1900, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/FC_Bayern_M%C3%BCnchen_logo_%282024%29.svg/768px-FC_Bayern_M%C3%BCnchen_logo_%282024%29.svg.png"},
    {"name": "Borussia Dortmund", "league_name": "Bundesliga", "year": 1909, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/768px-Borussia_Dortmund_logo.svg.png"},
    {"name": "RB Leipzig", "league_name": "Bundesliga", "year": 2009, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/0/04/RB_Leipzig_2014_logo.svg/1024px-RB_Leipzig_2014_logo.svg.png"},
    {"name": "VfB Stuttgart", "league_name": "Bundesliga", "year": 1893, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/VfB_Stuttgart_1893_Logo.svg/706px-VfB_Stuttgart_1893_Logo.svg.png"},
    {"name": "Bayer 04 Leverkusen", "league_name": "Bundesliga", "year": 1904, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/59/Bayer_04_Leverkusen_logo.svg/992px-Bayer_04_Leverkusen_logo.svg.png"},
    {"name": "1. FC Köln", "league_name": "Bundesliga", "year": 1948, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg/675px-1._FC_Koeln_Logo_2014%E2%80%93.svg.png"},
    {"name": "Eintracht Frankfurt", "league_name": "Bundesliga", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/7/7e/Eintracht_Frankfurt_crest.svg/768px-Eintracht_Frankfurt_crest.svg.png"},
    {"name": "Sport-Club Freiburg", "league_name": "Bundesliga", "year": 1904, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Freiburger_FC_Logo.svg/573px-Freiburger_FC_Logo.svg.png"},
    {"name": "Hamburger SV", "league_name": "Bundesliga", "year": 1887, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f7/Hamburger_SV_logo.svg/1024px-Hamburger_SV_logo.svg.png"},
    {"name": "FC St. Pauli", "league_name": "Bundesliga", "year": 1910, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/8/8f/FC_St._Pauli_logo_%282018%29.svg/768px-FC_St._Pauli_logo_%282018%29.svg.png"},
    {"name": "TSG Hoffenheim", "league_name": "Bundesliga", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Logo_TSG_Hoffenheim.svg/643px-Logo_TSG_Hoffenheim.svg.png"},
    {"name": "SV Werder Bremen", "league_name": "Bundesliga", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/SV-Werder-Bremen-Logo.svg/510px-SV-Werder-Bremen-Logo.svg.png"},
    {"name": "1. FC Union Berlin", "league_name": "Bundesliga", "year": 1966, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/1._FC_Union_Berlin_Logo.svg/1024px-1._FC_Union_Berlin_Logo.svg.png"},
    {"name": "FC Augsburg", "league_name": "Bundesliga", "year": 1907, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/c5/FC_Augsburg_logo.svg/589px-FC_Augsburg_logo.svg.png"},
    {"name": "VfL Wolfsburg", "league_name": "Bundesliga", "year": 1945, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/VfL_Wolfsburg_Logo.svg/768px-VfL_Wolfsburg_Logo.svg.png"},
    {"name": "1. FSV Mainz 05", "league_name": "Bundesliga", "year": 1905, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/8/83/Mainz_05_crest.svg/826px-Mainz_05_crest.svg.png"},
    {"name": "Borussia Mönchengladbach", "league_name": "Bundesliga", "year": 1900, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Borussia_M%C3%B6nchengladbach_logo.svg/500px-Borussia_M%C3%B6nchengladbach_logo.svg.png"},
    {"name": "1. FC Heidenheim 1846", "league_name": "Bundesliga", "year": 1846, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/1._FC_Heidenheim_1846.svg/623px-1._FC_Heidenheim_1846.svg.png"},

    # Serie A
    {"name": "Atalanta", "league_name": "Serie A", "year": 1907, "logo": "https://img.legaseriea.it/vimages/62cfd69d/atalanta.png?webp&q=70&size=-x319.5"},
    {"name": "AC Milan", "league_name": "Serie A", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Logo_of_AC_Milan.svg/330px-Logo_of_AC_Milan.svg.png"},
    {"name": "Bologna FC", "league_name": "Serie A", "year": 1909, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Bologna_F.C._1909_logo.svg/280px-Bologna_F.C._1909_logo.svg.png"},
    {"name": "Cagliari Calcio", "league_name": "Serie A", "year": 1920, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/61/Cagliari_Calcio_1920.svg/350px-Cagliari_Calcio_1920.svg.png"},
    {"name": "FC Empoli", "league_name": "Serie A", "year": 1920, "logo": "https://logodetimes.com/times/empoli-football-club/empoli-football-club-2048.png"},
    {"name": "Fiorentina", "league_name": "Serie A", "year": 1926, "logo": "https://tse2.mm.bing.net/th/id/OIP.k4uSu8p-0uU9XA2w2kIghQHaK1?cb=12&rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Genoa CFC", "league_name": "Serie A", "year": 1893, "logo": "https://vectorseek.com/wp-content/uploads/2023/06/Genoa-C.F.C.-Logo-Vector.jpg"},
    {"name": "Hellas Verona", "league_name": "Serie A", "year": 1903, "logo": "https://tse4.mm.bing.net/th/id/OIP.CYJ7h7ZMuHzbsz-kd4R2eQHaHa?cb=12&rs=1&pid=ImgDetMain&o=7&rm=3"},
    {"name": "Inter Milan", "league_name": "Serie A", "year": 1908, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/05/FC_Internazionale_Milano_2021.svg/500px-FC_Internazionale_Milano_2021.svg.png"},
    {"name": "Juventus FC", "league_name": "Serie A", "year": 1897, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg/260px-Juventus_FC_-_logo_black_%28Italy%2C_2020%29.svg.png"},
    {"name": "Lazio", "league_name": "Serie A", "year": 1900, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/S.S._Lazio_badge.svg/500px-S.S._Lazio_badge.svg.png"},
    {"name": "US Lecce", "league_name": "Serie A", "year": 1908, "logo": "https://i.pinimg.com/originals/2e/0f/49/2e0f49c2f17876d1537e6ffc97680eff.jpg"},
    {"name": "Monza", "league_name": "Serie A", "year": 1912, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/a/a7/AC_Monza_logo_%282021%29.svg/320px-AC_Monza_logo_%282021%29.svg.png"},
    {"name": "Napoli", "league_name": "Serie A", "year": 1926, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/SSC_Napoli_2024_%28deep_blue_navy%29.svg/500px-SSC_Napoli_2024_%28deep_blue_navy%29.svg.png"},
    {"name": "Parma", "league_name": "Serie A", "year": 1913, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/Logo_Parma_Calcio_1913_%28adozione_2016%29.svg/320px-Logo_Parma_Calcio_1913_%28adozione_2016%29.svg.png"},
    {"name": "Sassuolo", "league_name": "Serie A", "year": 1920, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/1/1c/US_Sassuolo_Calcio_logo.svg/380px-US_Sassuolo_Calcio_logo.svg.png"},
    {"name": "Torino FC", "league_name": "Serie A", "year": 1906, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2e/Torino_FC_Logo.svg/340px-Torino_FC_Logo.svg.png"},
    {"name": "Udinese", "league_name": "Serie A", "year": 1896, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/c/ce/Udinese_Calcio_logo.svg/420px-Udinese_Calcio_logo.svg.png"},
    {"name": "AS Roma", "league_name": "Serie A", "year": 1927, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f7/AS_Roma_logo_%282017%29.svg/350px-AS_Roma_logo_%282017%29.svg.png"},
    {"name": "Venezia FC", "league_name": "Serie A", "year": 1907, "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/3/39/Venezia_FC_crest.svg/420px-Venezia_FC_crest.svg.png"},
    
    # Ligue 1 McDonald's
    {"name": "Angers SCO", "league_name": "Ligue 1 McDonald's", "year": 1919, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/9/9c/Angers_SCO_logoo.svg/644px-Angers_SCO_logoo.svg.png"},
    {"name": "FC Lorient", "league_name": "Ligue 1 McDonald's", "year": 1926, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/4/4c/FC_Lorient_logo.svg/538px-FC_Lorient_logo.svg.png"},
    {"name": "Paris Saint-Germain", "league_name": "Ligue 1 McDonald's", "year": 1970, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/c/ca/Paris_Saint-Germain_F.CC..svg/768px-Paris_Saint-Germain_F.CC..svg.png"},
    {"name": "Olympique Marseille", "league_name": "Ligue 1 McDonald's", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Olympique_Marseille_logo.svg/593px-Olympique_Marseille_logo.svg.png"},
    {"name": "AS Monaco", "league_name": "Ligue 1 McDonald's", "year": 1924, "logo": "https://upload.wikimedia.org/wikipedia/id/6/6e/AS_Monaco_%282013%29.png"},
    {"name": "RC Strasbourg Alsace", "league_name": "Ligue 1 McDonald's", "year": 1906, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/8/80/Racing_Club_de_Strasbourg_logo.svg/768px-Racing_Club_de_Strasbourg_logo.svg.png"},
    {"name": "LOSC Lille", "league_name": "Ligue 1 McDonald's", "year": 1944, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/3/3f/Lille_OSC_2018_logo.svg/808px-Lille_OSC_2018_logo.svg.png"},
    {"name": "OGC Nice", "league_name": "Ligue 1 McDonald's", "year": 1904, "logo": "https://upload.wikimedia.org/wikipedia/id/0/05/OGC_Nice_logo.png"},
    {"name": "Stade Rennais FC", "league_name": "Ligue 1 McDonald's", "year": 1901, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/9/93/Stade_Rennais_FCC.svg/696px-Stade_Rennais_FCC.svg.png"},
    {"name": "Olympique Lyon", "league_name": "Ligue 1 McDonald's", "year": 1899, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/c/c6/Olympique_Lyonnais.svg/662px-Olympique_Lyonnais.svg.png"},
    {"name": "Paris FC", "league_name": "Ligue 1 McDonald's", "year": 1969, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/d/db/Logo_Paris_FC_2011.svg/647px-Logo_Paris_FC_2011.svg.png"},
    {"name": "Stade Brestois 29", "league_name": "Ligue 1 McDonald's", "year": 1903, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/0/05/Stade_Brestois_29_logo.svg/634px-Stade_Brestois_29_logo.svg.png"},
    {"name": "RC Lens", "league_name": "Ligue 1 McDonald's", "year": 1906, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/c/cc/RC_Lens_logo.svg/579px-RC_Lens_logo.svg.png"},
    {"name": "FC Toulouse", "league_name": "Ligue 1 McDonald's", "year": 1937, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/6/63/Toulouse_FC_2018_logo.svg/768px-Toulouse_FC_2018_logo.svg.png"},
    {"name": "FC Nantes", "league_name": "Ligue 1 McDonald's", "year": 1943, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Logo_FC_Nantes_%28avec_fond%29_-_2019.svg/596px-Logo_FC_Nantes_%28avec_fond%29_-_2019.svg.png"},
    {"name": "AJ Auxerre", "league_name": "Ligue 1 McDonald's", "year": 1905, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/5/51/AJAuxerreLogo.svg/608px-AJAuxerreLogo.svg.png"},
    {"name": "FC Metz", "league_name": "Ligue 1 McDonald's", "year": 1932, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/FC_Metz_2021_Logo.svg/537px-FC_Metz_2021_Logo.svg.png"},
    {"name": "Le Havre AC", "league_name": "Ligue 1 McDonald's", "year": 1872, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/c/c9/Le_Havre_AC_logo0.svg/630px-Le_Havre_AC_logo0.svg.png"},
    
    # Primeira Liga
    {"name": "FC Porto", "league_name": "Primeira Liga", "year": 1893, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/f/f1/FC_Porto.svg/576px-FC_Porto.svg.png"},
    {"name": "Sporting CP", "league_name": "Primeira Liga", "year": 1906, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/e/e1/Sporting_Clube_de_Portugal_%28Logo%29.svg/573px-Sporting_Clube_de_Portugal_%28Logo%29.svg.png"},
    {"name": "Benfica", "league_name": "Primeira Liga", "year": 1904, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/a/a2/SL_Benfica_logo.svg/775px-SL_Benfica_logo.svg.png"},
    {"name": "SC Braga", "league_name": "Primeira Liga", "year": 1921, "logo": "https://upload.wikimedia.org/wikipedia/id/thumb/7/79/S.C._Braga_logo.svg/655px-S.C._Braga_logo.svg.png"},
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