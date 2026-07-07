from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail, signing
from users.models import UserProfile

class RefactoredAuthFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('users:login')
        self.signup_url = reverse('users:signup')
        
        # Create an existing active user for testing signin
        self.active_username = "testactive"
        self.active_email = "testactive@example.com"
        self.active_password = "activepassword123"
        self.user = User.objects.create_user(
            username=self.active_email, 
            email=self.active_email, 
            password=self.active_password,
            is_active=True
        )
        self.user.profile.username = self.active_username
        self.user.profile.save()

    def test_login_view_get(self):
        """GET request to login page renders correctly and has Email and Password fields."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Username')
        self.assertContains(response, 'Email Address')
        self.assertContains(response, 'Password')

    def test_login_view_signin_non_existent(self):
        """Sign In with non-existent email shows error."""
        response = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account does not exist. Please register first.")

    def test_login_view_signin_wrong_password(self):
        """Sign In with incorrect password shows error."""
        response = self.client.post(self.login_url, {
            'email': self.active_email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Incorrect password. Please try again.")

    def test_login_view_signin_success(self):
        """Sign In with correct credentials logs the user in and redirects to dashboard."""
        response = self.client.post(self.login_url, {
            'email': self.active_email,
            'password': self.active_password
        })
        self.assertRedirects(response, reverse('documents:dashboard'))

    def test_signup_view_get(self):
        """GET request to signup page renders correctly."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'User Registration')

    def test_signup_view_post_existing_email(self):
        """Registering with an already existing email shows error."""
        response = self.client.post(self.signup_url, {
            'first_name': 'New',
            'last_name': 'User',
            'username': 'newuser',
            'email': self.active_email,
            'phone': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account with this email address already exists. Please sign in.")

    def test_signup_form_excludes_passwords(self):
        """Verify that the signup page does not include password fields."""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id_password')
        self.assertNotContains(response, 'id_confirm_password')

    def test_signup_view_post_success(self):
        """Registering a new user creates an inactive account and emails a verification link."""
        new_username = "brandnewuser"
        new_email = "brandnew@example.com"
        
        response = self.client.post(self.signup_url, {
            'first_name': 'Brand',
            'last_name': 'New',
            'username': new_username,
            'email': new_email,
            'phone': '9876543210'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/link_sent.html')
        
        # Verify inactive user is created in DB
        self.assertTrue(User.objects.filter(username=new_email).exists())
        new_user = User.objects.get(username=new_email)
        self.assertFalse(new_user.is_active)
        self.assertEqual(new_user.profile.username, new_username)
        self.assertEqual(new_user.profile.phone, '9876543210')
        self.assertFalse(new_user.profile.is_active)
        
        # Verify verification link email sent
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [new_email])
        self.assertIn("SmartTrack IIMS - Portal Email Verification", sent_email.subject)
        self.assertIn("/auth/verify-link/", sent_email.body)

    def test_verify_link_view_valid(self):
        """Clicking verify-link activates the user, generates and emails a temporary password."""
        # Create an inactive user first
        inactive_email = "inactive@example.com"
        user = User.objects.create_user(
            username=inactive_email,
            email=inactive_email,
            password='oldpassword',
            is_active=False
        )
        user.profile.username = "inactiveuser"
        user.profile.is_active = False
        user.profile.save()

        # Generate verification token
        token = signing.dumps({'email': inactive_email})
        verify_url = reverse('users:verify_link', args=[token])
        
        mail.outbox = [] # Clear mail outbox
        response = self.client.get(verify_url)
        
        # Should redirect to login page
        self.assertRedirects(response, reverse('users:login'))
        
        # Verify user is now active in DB and is marked as using temporary password
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.is_active)
        self.assertTrue(user.profile.is_temp_password)
        
        # Verify second email was sent containing the new temporary password
        self.assertEqual(len(mail.outbox), 1)
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [inactive_email])
        self.assertIn("SmartTrack IIMS - Portal Temporary Password", sent_email.subject)
        self.assertIn("Temporary Password:", sent_email.body)
        
        # Get temporary password and assert it can authenticate
        temp_password = user.profile.password
        self.assertTrue(user.check_password(temp_password))

    def test_login_with_temp_password_sets_popup_flag(self):
        """Logging in with a temporary password sets show_password_change_popup in session."""
        temp_email = "temp@example.com"
        user = User.objects.create_user(
            username=temp_email,
            email=temp_email,
            password='temppassword',
            is_active=True
        )
        user.profile.username = "tempuser"
        user.profile.is_temp_password = True
        user.profile.password = 'temppassword'
        user.profile.save()

        response = self.client.post(self.login_url, {
            'email': temp_email,
            'password': 'temppassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('documents:dashboard'))
        self.assertTrue(self.client.session.get('show_password_change_popup'))

    def test_change_password_popup_view_success(self):
        """POST request to change_password_popup updates the password and clears the popup flag."""
        self.client.login(username=self.active_email, password=self.active_password)
        
        # Mock session flag and is_temp_password status
        session = self.client.session
        session['show_password_change_popup'] = True
        session.save()
        self.user.profile.is_temp_password = True
        self.user.profile.save()

        response = self.client.post(reverse('users:change_password_popup'), {
            'new_password': 'brandnewsecurepass',
            'confirm_password': 'brandnewsecurepass'
        })
        
        self.assertRedirects(response, reverse('documents:dashboard'))
        self.user.refresh_from_db()
        
        # Verify password is updated and temp password flag is cleared
        self.assertTrue(self.user.check_password('brandnewsecurepass'))
        self.assertFalse(self.user.profile.is_temp_password)
        self.assertEqual(self.user.profile.password, 'brandnewsecurepass')
        self.assertFalse(self.client.session.get('show_password_change_popup'))

    def test_duplicate_usernames_different_emails(self):
        """Verify that two users can register with the same username but different email addresses."""
        display_username = "duplicateuser"
        email_1 = "user1@example.com"
        email_2 = "user2@example.com"
        
        # Register user 1
        response1 = self.client.post(self.signup_url, {
            'first_name': 'First',
            'last_name': 'One',
            'username': display_username,
            'email': email_1,
            'phone': '1111111111'
        })
        self.assertEqual(response1.status_code, 200)
        
        # Register user 2 with same username
        response2 = self.client.post(self.signup_url, {
            'first_name': 'Second',
            'last_name': 'Two',
            'username': display_username,
            'email': email_2,
            'phone': '2222222222'
        })
        self.assertEqual(response2.status_code, 200)
        
        # Verify both inactive users are created successfully in the DB
        self.assertTrue(User.objects.filter(username=email_1).exists())
        self.assertTrue(User.objects.filter(username=email_2).exists())
        
        user1 = User.objects.get(username=email_1)
        user2 = User.objects.get(username=email_2)
        
        self.assertEqual(user1.profile.username, display_username)
        self.assertEqual(user2.profile.username, display_username)
