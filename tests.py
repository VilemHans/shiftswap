from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import Company, Shift, ShiftRequest

class DashboardNavigationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.company = Company.objects.create(name="Test Company")
        self.user1 = User.objects.create_user(username="jan", password="password123")
        self.user2 = User.objects.create_user(username="petr", password="password123")
        
        now = timezone.now()
        self.shift1 = Shift.objects.create(
            user=self.user1,
            company=self.company,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=8),
            note="Ranní směna",
            status="assigned"
        )
        self.shift2 = Shift.objects.create(
            user=self.user2,
            company=self.company,
            start_time=now + timedelta(days=2),
            end_time=now + timedelta(days=2, hours=8),
            note="Odpolední směna od Petra",
            status="offered"
        )

    def test_dashboard_requires_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_dashboard_contains_top_left_hamburger_and_drawer(self):
        self.client.force_login(self.user1)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

        content = response.content.decode('utf-8')

        # Check hamburger button (3 lines) and drawer
        self.assertIn('drawerToggleBtn', content)
        self.assertIn('drawerSidebar', content)
        self.assertIn('drawerOverlay', content)

        # Navigation options must be inside the drawer
        self.assertIn('data-drawer-view="shifts"', content)
        self.assertIn('data-drawer-view="calendar"', content)
        self.assertIn('data-drawer-view="market"', content)
        self.assertIn('data-drawer-view="all"', content)

        # Removed from the top bar
        self.assertNotIn('nav-tab', content)
        self.assertNotIn('mobile-nav-btn', content)

        # Check section ids
        self.assertIn('section-shifts', content)
        self.assertIn('section-calendar', content)
        self.assertIn('section-market', content)

        # Check fullcalendar integration
        self.assertIn('calendar-data', content)
        self.assertIn('FullCalendar', content)

    def test_offer_and_cancel_shift(self):
        self.client.force_login(self.user1)
        response = self.client.get(f'/offer/{self.shift1.id}/')
        self.assertEqual(response.status_code, 302)
        self.shift1.refresh_from_db()
        self.assertEqual(self.shift1.status, 'offered')

        response = self.client.get(f'/cancel-offer/{self.shift1.id}/')
        self.assertEqual(response.status_code, 302)
        self.shift1.refresh_from_db()
        self.assertEqual(self.shift1.status, 'assigned')

    def test_request_and_cancel_request_shift(self):
        self.client.force_login(self.user1)
        # Initially user1 sees "Mám zájem o směnu"
        response = self.client.get('/')
        self.assertContains(response, 'Mám zájem o směnu')
        self.assertNotContains(response, 'Zažádáno o směnu')

        # user1 requests shift2
        response = self.client.get(f'/request/{self.shift2.id}/')
        self.assertEqual(response.status_code, 302)

        # Dashboard now marks it as requested
        response = self.client.get('/')
        self.assertContains(response, 'Zažádáno o směnu')
        self.assertContains(response, 'Žádost odeslána')
        self.assertContains(response, 'Zrušit žádost')

        # user1 cancels their request
        response = self.client.get(f'/cancel-request/{self.shift2.id}/')
        self.assertEqual(response.status_code, 302)

        # Dashboard shows it is available again
        response = self.client.get('/')
        self.assertContains(response, 'Mám zájem o směnu')
        self.assertNotContains(response, 'Zažádáno o směnu')
