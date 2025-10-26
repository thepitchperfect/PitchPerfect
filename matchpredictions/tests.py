from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils.timezone import make_aware

from matchpredictions.models import Match, Vote
from matchpredictions.forms import MatchForm
from club_directories.models import League, Club

User = get_user_model()


class MatchPredictionViewTests(TestCase):
    """Full test suite for match prediction views and templates"""

    def setUp(self):
        self.client = Client()

        # --- Create test users (your CustomUser requires email + full_name) ---
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            full_name="Test User",
            password="12345"
        )

        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            full_name="Admin User",
            password="12345"
        )

        # --- Create League and Clubs ---
        self.league = League.objects.create(name="Premier League")
        self.home_team = Club.objects.create(name="Chelsea", league=self.league)
        self.away_team = Club.objects.create(name="Arsenal", league=self.league)

        # --- Create Match with required fields (match_date!) ---
        self.match = Match.objects.create(
            league=self.league,
            home_team=self.home_team,
            away_team=self.away_team,
            status="upcoming",
            match_date=make_aware(datetime.now() + timedelta(days=1))
        )

    
    #  MAIN PAGE TESTS
    

    def test_main_page_loads(self):
        """Main page should load successfully"""
        response = self.client.get(reverse("matchpredictions:main"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Match Predictions")

    def test_main_page_displays_matches(self):
        """Main page should display match info"""
        response = self.client.get(reverse("matchpredictions:main"))
        self.assertContains(response, self.home_team.name)
        self.assertContains(response, self.away_team.name)
        self.assertContains(response, self.league.name)

    def test_search_filter(self):
        """Search filter should show relevant matches"""
        response = self.client.get(reverse("matchpredictions:main"), {"search": "Chelsea"})
        self.assertContains(response, "Chelsea")

        response = self.client.get(reverse("matchpredictions:main"), {"search": "Barcelona"})
        self.assertNotContains(response, "Chelsea")

    def test_league_filter(self):
        """League filter should show matches from the selected league"""
        response = self.client.get(reverse("matchpredictions:main"), {"league": self.league.id})
        self.assertContains(response, self.league.name)

    def test_requires_login_to_vote(self):
        """Non-logged users should see 'Login to Vote' button"""
        response = self.client.get(reverse("matchpredictions:main"))
        self.assertContains(response, "Login to Vote")

    def test_authenticated_user_sees_vote_now(self):
        """Logged-in users should see 'Vote Now'"""
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("matchpredictions:main"))
        self.assertContains(response, "Vote Now")

    # 
    #  ADMIN / MATCH FORM TESTS
    

    def test_admin_can_access_add_match_form(self):
        """Admins can access Add Match form"""
        self.client.login(username="admin", password="12345")
        response = self.client.get(reverse("matchpredictions:match_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ("Add Match" in response.content.decode()) or ("Add New Match" in response.content.decode())
        )

    def test_admin_can_create_match(self):
        """Admins can create a match via the form"""
        self.client.login(username="admin", password="12345")
        response = self.client.post(
            reverse("matchpredictions:match_create"),
            {
                "league": self.league.id,
                "home_team": self.home_team.id,
                "away_team": self.away_team.id,
                "status": "upcoming",
                "match_date": make_aware(datetime.now() + timedelta(days=3)),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Match.objects.filter(home_team=self.home_team, away_team=self.away_team).exists()
        )

    def test_non_admin_cannot_access_add_form(self):
        """Regular users cannot access Add Match form"""
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("matchpredictions:match_create"))
        self.assertNotEqual(response.status_code, 200)

    
    #  EDGE CASES
    

    def test_empty_match_list_message(self):
        """If there are no matches, show an empty message"""
        Match.objects.all().delete()
        response = self.client.get(reverse("matchpredictions:main"))
        self.assertContains(response, "No matches available")

    
    #  MATCH DETAILS PAGE TESTS
    

    def test_match_detail_page_loads(self):
        """Match details page should load and show both teams"""
        response = self.client.get(reverse("matchpredictions:match_detail", args=[self.match.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.home_team.name)
        self.assertContains(response, self.away_team.name)
        self.assertContains(response, "Cast Your Prediction")

    def test_guest_sees_login_prompt_on_detail_page(self):
        """Guests should see login message"""
        response = self.client.get(reverse("matchpredictions:match_detail", args=[self.match.id]))
        self.assertContains(response, "Login")
        self.assertContains(response, "participate in match predictions")

    def test_logged_in_user_sees_vote_buttons(self):
        """Logged-in users can see vote buttons"""
        self.client.login(username="testuser", password="12345")
        response = self.client.get(reverse("matchpredictions:match_detail", args=[self.match.id]))
        self.assertContains(response, "Win")
        self.assertContains(response, "Draw")

    def test_unauthenticated_vote_redirects_to_login(self):
        """Unauthenticated users trying to vote are redirected to login"""
        vote_url = reverse("matchpredictions:vote_match", args=[self.match.id])
        response = self.client.post(vote_url, {"prediction": "home_win"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

    def test_authenticated_vote_works_and_shows_message(self):
        """Authenticated users can vote and see confirmation"""
        self.client.login(username="testuser", password="12345")
        vote_url = reverse("matchpredictions:vote_match", args=[self.match.id])
        response = self.client.post(vote_url, {"prediction": "home_win"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Match.objects.filter(votes__user=self.user, votes__prediction="home_win").exists()
        )

    
    # Vote Edit, Delete, Form Validation
    

    def test_vote_edit_view_allows_user(self):
        """Logged-in user can access edit vote page"""
        self.client.login(username="testuser", password="12345")
        Vote.objects.create(match=self.match, user=self.user, prediction="home_win")
        response = self.client.get(reverse("matchpredictions:edit_vote", args=[self.match.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
        "Edit Your Vote" in response.content.decode() or "Edit Vote" in response.content.decode(),
        "Edit vote page should render correctly"
    )


    def test_vote_delete_view_removes_vote(self):
        """User can delete their vote"""
        self.client.login(username="testuser", password="12345")
        vote = Vote.objects.create(match=self.match, user=self.user, prediction="draw")
        response = self.client.post(reverse("matchpredictions:delete_vote", args=[self.match.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Vote.objects.filter(id=vote.id).exists())

    

