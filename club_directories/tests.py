import json
import uuid
from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.db.utils import IntegrityError
from main.models import CustomUser
from .models import League, Club, ClubDetails, LeaguePick
from .views import show_club_directory, get_club_details, set_league_pick

class ClubDirectoriesTests(TestCase):

    def setUp(self):
        """Set up initial data for all tests."""
        self.client = Client()
        
        # Create a test user using the direct import
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            password='password123',
            email='test@example.com',
            full_name='Test User'
            ) 
        
        # Create leagues
        self.league1 = League.objects.create(name="Premier League", region="UK", logo_path="path/pl.png")
        self.league2 = League.objects.create(name="La Liga", region="Spain", logo_path="path/ll.png")
        
        # Create clubs
        self.club1 = Club.objects.create(league=self.league1, name="Arsenal", founded_year=1886)
        self.club2 = Club.objects.create(league=self.league1, name="Chelsea", founded_year=1905)
        self.club3 = Club.objects.create(league=self.league2, name="Real Madrid", founded_year=1902)
        
        # Create club details for one club (to test both cases)
        self.details1 = ClubDetails.objects.create(
            club=self.club1,
            description="Test description",
            history_summary="Test history",
            stadium_name="Test Stadium",
            stadium_capacity=50000,
            manager_name="Test Manager"
        )
        
        # Store URLs for easy access
        self.directory_url = reverse('club_directories:show_club_directory')
        self.details_url = reverse('club_directories:get_club_details', args=[self.club1.id])
        self.set_pick_url = reverse('club_directories:set_league_pick')
    # Model Tests
    def test_league_str(self):
        """Test the string representation of the League model."""
        self.assertEqual(str(self.league1), "Premier League")

    def test_club_str(self):
        """Test the string representation of the Club model."""
        self.assertEqual(str(self.club1), "Arsenal")

    def test_club_details_str(self):
        """Test the string representation of the ClubDetails model."""
        self.assertEqual(str(self.details1), f"Details for {self.club1.name}")

    def test_league_pick_str(self):
        """Test the string representation of the LeaguePick model."""
        pick = LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club1)
        self.assertEqual(str(pick), f"{self.user.username}'s pick for {self.league1.name}: {self.club1.name}")

    def test_league_pick_unique_constraint(self):
        """Test the 'unique_together' constraint on LeaguePick."""
        LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club1)
        # Try to create another pick for the same user and league
        with self.assertRaises(IntegrityError):
            LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club2)

    # URL Tests
    def test_directory_url_resolves(self):
        """Test that the root directory URL resolves to the correct view."""
        view = resolve(self.directory_url)
        self.assertEqual(view.func, show_club_directory)

    def test_club_details_url_resolves(self):
        """Test that the club details URL resolves to the correct view."""
        view = resolve(self.details_url)
        self.assertEqual(view.func, get_club_details)

    def test_set_pick_url_resolves(self):
        """Test that the set league pick URL resolves to the correct view."""
        view = resolve(self.set_pick_url)
        self.assertEqual(view.func, set_league_pick)

    # View: show_club_directory
    def test_show_club_directory_unauthenticated(self):
        """Test the main page for an unauthenticated user."""
        response = self.client.get(self.directory_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_directories/directory.html')
        self.assertIn('league_picks_data', response.context)
        self.assertEqual(response.context['league_picks_data'], {})

    def test_show_club_directory_authenticated_no_picks(self):
        """Test the main page for an authenticated user with no picks."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.directory_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'club_directories/directory.html')
        # Authenticated user has picks data, but it should be empty
        self.assertIn('league_picks_data', response.context)
        self.assertEqual(response.context['league_picks_data'], {})

    def test_show_club_directory_authenticated_with_picks(self):
        """Test the main page for an authenticated user with picks."""
        self.client.login(username='testuser', password='password123')
        LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club1)
        
        response = self.client.get(self.directory_url)
        self.assertEqual(response.status_code, 200)
        
        picks_data = response.context['league_picks_data']
        self.assertIn(str(self.league1.id), picks_data)
        self.assertEqual(picks_data[str(self.league1.id)]['clubId'], str(self.club1.id))
        self.assertEqual(picks_data[str(self.league1.id)]['clubName'], self.club1.name)
        
        # Check that the data is passed to the json_script
        self.assertContains(response, 'id="league-picks-data"')

    # View: get_club_details
    def test_get_club_details_valid_with_details(self):
        """Test getting JSON for a club that HAS a ClubDetails entry."""
        response = self.client.get(self.details_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], str(self.club1.id))
        self.assertEqual(data['name'], self.club1.name)
        # Check that it pulled from the real ClubDetails object
        self.assertEqual(data['description'], "Test description")
        self.assertEqual(data['stadium_name'], "Test Stadium")
        self.assertEqual(data['manager_name'], "Test Manager")

    def test_get_club_details_valid_no_details(self):
        """Test getting JSON for a club that DOES NOT have a ClubDetails entry."""
        # club3 was created without details
        url = reverse('club_directories:get_club_details', args=[self.club3.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], str(self.club3.id))
        # Check that it fell back to the placeholder description
        self.assertIn("A football club founded in", data['description'])
        self.assertEqual(data['stadium_name'], "N/A")

    def test_get_club_details_invalid_404(self):
        """Test that an invalid club UUID returns a 404."""
        invalid_uuid = uuid.uuid4()
        url = reverse('club_directories:get_club_details', args=[invalid_uuid])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_club_details_is_league_pick(self):
        """Test that 'is_league_pick' is true if the user has picked the club."""
        self.client.login(username='testuser', password='password123')
        LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club1)
        response = self.client.get(self.details_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['is_league_pick'])
            
    def test_get_club_details_is_not_league_pick(self):
        """Test that 'is_league_pick' is false if the user has not picked the club."""
        self.client.login(username='testuser', password='password123')
        # User has no picks
        response = self.client.get(self.details_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_league_pick'])
        
    def test_get_club_details_is_not_league_pick_unauthenticated(self):
        """Test that 'is_league_pick' is false for an unauthenticated user."""
        response = self.client.get(self.details_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['is_league_pick'])

    # View: set_league_pick
    def test_set_league_pick_unauthenticated(self):
        """Test that an unauthenticated user is redirected to the login page."""
        response = self.client.post(self.set_pick_url, {'club_id': self.club1.id})
        # @login_required decorator redirects to the login URL
        self.assertEqual(response.status_code, 302)
        # Check if it redirects to the login URL specified in your settings
        # or in directory.html, which is 'main:login'
        self.assertIn(reverse('main:login'), response.url)

    def test_set_league_pick_not_post(self):
        """Test that a GET request is not allowed (405)."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(self.set_pick_url)
        # @require_POST decorator returns 405 Method Not Allowed
        self.assertEqual(response.status_code, 405)

    def test_set_new_pick_success(self):
        """Test successfully setting a new league pick."""
        self.client.login(username='testuser', password='password123')
        self.assertEqual(LeaguePick.objects.count(), 0)
        
        response = self.client.post(self.set_pick_url, {'club_id': self.club1.id, 'league_id': self.league1.id})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LeaguePick.objects.count(), 1)
        pick = LeaguePick.objects.first()
        self.assertEqual(pick.club, self.club1)
        self.assertEqual(pick.user, self.user)
        
        data = response.json()
        self.assertEqual(data['status'], 'set')
        self.assertEqual(data['league_id'], str(self.league1.id))
        self.assertEqual(data['club_data']['clubId'], str(self.club1.id))

    def test_change_pick_success(self):
        """Test successfully changing an existing league pick."""
        self.client.login(username='testuser', password='password123')
        LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club1)
        self.assertEqual(LeaguePick.objects.count(), 1)
        
        # Change pick from club1 to club2 (same league)
        response = self.client.post(self.set_pick_url, {'club_id': self.club2.id, 'league_id': self.league1.id})
        
        self.assertEqual(response.status_code, 200)
        # Count is still 1, but the club is updated
        self.assertEqual(LeaguePick.objects.count(), 1)
        pick = LeaguePick.objects.first()
        self.assertEqual(pick.club, self.club2) # Test update_or_create logic
        self.assertEqual(response.json()['club_data']['clubId'], str(self.club2.id))

    def test_clear_pick_success(self):
        """Test successfully clearing a league pick."""
        self.client.login(username='testuser', password='password123')
        LeaguePick.objects.create(user=self.user, league=self.league1, club=self.club1)
        self.assertEqual(LeaguePick.objects.count(), 1)

        # Clear the pick by sending 'NONE'
        response = self.client.post(self.set_pick_url, {'club_id': 'NONE', 'league_id': self.league1.id})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LeaguePick.objects.count(), 0) # Pick should be deleted
        data = response.json()
        self.assertEqual(data['status'], 'cleared')
        self.assertEqual(data['league_id'], str(self.league1.id))

    def test_set_pick_bad_request_missing_ids(self):
        """Test that missing IDs in the POST data returns a 400."""
        self.client.login(username='testuser', password='password123')
        
        # No club_id or league_id
        response = self.client.post(self.set_pick_url, {})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'Club or League ID is required.')

    def test_set_pick_bad_request_clear_no_league(self):
        """Test that clearing a pick without a league_id returns a 400."""
        self.client.login(username='testuser', password='password123')

        # Clear pick with no league_id
        response = self.client.post(self.set_pick_url, {'club_id': 'NONE'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['message'], 'League ID is required to clear a pick.')

    def test_set_pick_club_not_found(self):
        """Test that a non-existent club_id returns a 404."""
        self.client.login(username='testuser', password='password123')
        invalid_uuid = uuid.uuid4()
        response = self.client.post(self.set_pick_url, {'club_id': invalid_uuid, 'league_id': self.league1.id})
        self.assertEqual(response.status_code, 404)

    def test_clear_pick_league_not_found(self):
        """Test that a non-existent league_id when clearing returns a 404."""
        self.client.login(username='testuser', password='password123')
        invalid_uuid = uuid.uuid4()
        response = self.client.post(self.set_pick_url, {'club_id': 'NONE', 'league_id': invalid_uuid})
        self.assertEqual(response.status_code, 404)