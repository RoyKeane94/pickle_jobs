from django.test import TestCase
import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from .models import Company, EmployeeProfile, EmployerProfile

User = get_user_model()

class AccountViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('accounts:login')
        self.register_url = reverse('accounts:register')
        self.logout_url = reverse('accounts:logout')
        self.employee_dashboard_url = reverse('employee:dashboard')
        self.employer_dashboard_url = reverse('employer:dashboard')

        # Generate unique email addresses using UUID
        unique_id_emp = uuid.uuid4()
        unique_id_er = uuid.uuid4()
        self.employee_email = f'testemployee_{unique_id_emp}@example.com'
        self.employer_email = f'testemployer_{unique_id_er}@example.com'
        self.password = 'password123'

        # Create Employee User and Profile
        self.employee_user = User.objects.create_user(
            username=f'employee_{unique_id_emp}',
            email=self.employee_email,
            password=self.password,
            first_name='Test',
            last_name='Employee',
            user_type='employee'
        )
        EmployeeProfile.objects.create(user=self.employee_user)

        # Create Company
        self.company = Company.objects.create(name='Test Company')

        # Create Employer User and Profile
        self.employer_user = User.objects.create_user(
            username=f'employer_{unique_id_er}',
            email=self.employer_email,
            password=self.password,
            first_name='Test',
            last_name='Employer',
            user_type='employer'
        )
        EmployerProfile.objects.create(user=self.employer_user, company=self.company)

        # Registration data
        self.employee_reg_data = {
            'email': f'newemployee_{uuid.uuid4()}@example.com',
            'first_name': 'New',
            'last_name': 'Employee',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'user_type': 'employee'
        }
        self.employer_reg_data = {
            'email': f'newemployer_{uuid.uuid4()}@example.com',
            'first_name': 'New',
            'last_name': 'Employer',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'user_type': 'employer',
            'company_name': 'New Test Company',
            'company_description': 'A description for the new test company.'
        }


    # --- Login View Tests ---
    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertIn('form', response.context)

    def test_login_view_post_employee_success(self):
        response = self.client.post(self.login_url, {
            'username': self.employee_email,
            'password': self.password
        })
        self.assertRedirects(response, self.employee_dashboard_url)
        self._assert_user_logged_in(self.employee_user.pk)

    def test_login_view_post_employer_success(self):
        response = self.client.post(self.login_url, {
            'username': self.employer_email,
            'password': self.password
        })
        self.assertRedirects(response, self.employer_dashboard_url)
        self._assert_user_logged_in(self.employer_user.pk)

    def test_login_view_post_fail_wrong_password(self):
        response = self.client.post(self.login_url, {
            'username': self.employee_email,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertFormError(response.context['form'], None, 'Please enter a correct email and password. Note that both fields may be case-sensitive.')
        self._assert_user_not_logged_in()

    def test_login_view_post_fail_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertFormError(response.context['form'], None, 'Please enter a correct email and password. Note that both fields may be case-sensitive.')
        self._assert_user_not_logged_in()

    def test_login_view_get_authenticated_employee(self):
        self.client.login(username=self.employee_email, password=self.password)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.employee_dashboard_url)

    def test_login_view_get_authenticated_employer(self):
        self.client.login(username=self.employer_email, password=self.password)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.employer_dashboard_url)


    # --- Register View Tests ---
    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertIn('form', response.context)

    def test_register_view_post_employee_success(self):
        user_count_before = User.objects.count()
        response = self.client.post(self.register_url, self.employee_reg_data)
        self.assertEqual(User.objects.count(), user_count_before + 1)
        new_user = User.objects.get(email=self.employee_reg_data['email'])
        self.assertRedirects(response, self.employee_dashboard_url)
        self._assert_user_logged_in(new_user.pk)
        self.assertTrue(EmployeeProfile.objects.filter(user=new_user).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Account created successfully!")

    def test_register_view_post_employer_success(self):
        user_count_before = User.objects.count()
        company_count_before = Company.objects.count()
        response = self.client.post(self.register_url, self.employer_reg_data)
        self.assertEqual(User.objects.count(), user_count_before + 1)
        # Check if a new company was created or an existing one was used (depends on form logic)
        # Assuming the form creates a new company if the name is new
        self.assertTrue(Company.objects.filter(name=self.employer_reg_data['company_name']).exists())
        new_user = User.objects.get(email=self.employer_reg_data['email'])
        self.assertRedirects(response, self.employer_dashboard_url)
        self._assert_user_logged_in(new_user.pk)
        self.assertTrue(EmployerProfile.objects.filter(user=new_user).exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Account created successfully!")

    def test_register_view_post_fail_password_mismatch(self):
        data = self.employee_reg_data.copy()
        data['confirm_password'] = 'mismatchedpassword'
        user_count_before = User.objects.count()
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertFormError(response.context['form'], 'confirm_password', "The two password fields didn't match.")
        self.assertEqual(User.objects.count(), user_count_before)
        self._assert_user_not_logged_in()

    def test_register_view_post_fail_email_exists(self):
        data = self.employee_reg_data.copy()
        data['email'] = self.employee_email # Use existing employee email
        user_count_before = User.objects.count()
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertTemplateUsed(response, 'accounts/register.html')
        self.assertFormError(response.context['form'], 'email', 'A user with that email already exists.')
        self.assertEqual(User.objects.count(), user_count_before)
        self._assert_user_not_logged_in()

    def test_register_view_get_authenticated_employee(self):
        self.client.login(username=self.employee_email, password=self.password)
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.employee_dashboard_url)

    def test_register_view_get_authenticated_employer(self):
        self.client.login(username=self.employer_email, password=self.password)
        response = self.client.get(self.register_url)
        self.assertRedirects(response, self.employer_dashboard_url)

    # --- Logout View Tests ---
    def test_logout_view_success(self):
        self.client.login(username=self.employee_email, password=self.password)
        self._assert_user_logged_in(self.employee_user.pk) # Pre-check
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        self._assert_user_not_logged_in()
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have been successfully logged out.")

    def test_logout_view_not_logged_in(self):
        response = self.client.get(self.logout_url)
        # Redirects to LOGIN_URL by default if @login_required were used,
        # but logout view itself doesn't require login
        # It simply calls logout() which is idempotent
        self.assertRedirects(response, self.login_url)
        self._assert_user_not_logged_in()
        # No message should be displayed if the user wasn't logged in
        messages = list(get_messages(response.wsgi_request))
        # Check if any messages are present, could be 0 or 1 depending on middleware setup
        # But the specific logout success message shouldn't be there.
        self.assertTrue(all(str(m) != "You have been successfully logged out." for m in messages))


    # --- Helper Assertions ---
    def _assert_user_logged_in(self, user_pk):
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertEqual(self.client.session['_auth_user_id'], str(user_pk))

    def _assert_user_not_logged_in(self):
        self.assertFalse('_auth_user_id' in self.client.session)
