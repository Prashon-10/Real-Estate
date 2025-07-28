# Testing Guide

## Testing Strategy

### Testing Pyramid
The application follows a comprehensive testing strategy with multiple layers:

1. **Unit Tests**: Test individual components and functions
2. **Integration Tests**: Test component interactions
3. **System Tests**: Test complete user workflows  
4. **Performance Tests**: Test scalability and response times
5. **Security Tests**: Test for vulnerabilities
6. **User Acceptance Tests**: Test from end-user perspective

## Test Structure

### Directory Organization
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_forms.py
│   └── test_utils.py
├── integration/
│   ├── test_authentication.py
│   ├── test_property_workflow.py
│   └── test_search_integration.py
├── system/
│   ├── test_user_journey.py
│   └── test_api_endpoints.py
├── performance/
│   ├── test_load.py
│   └── test_ai_performance.py
└── fixtures/
    ├── users.json
    ├── properties.json
    └── sample_data.json
```

## Unit Tests

### Model Testing

#### User Model Tests
```python
# tests/unit/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='customer'
        )
    
    def test_user_creation(self):
        """Test user is created correctly"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.user_type, 'customer')
        self.assertTrue(self.user.check_password('testpass123'))
    
    def test_unique_key_generation(self):
        """Test unique key is generated"""
        self.assertIsNotNone(self.user.unique_key)
        self.assertEqual(len(self.user.unique_key), 9)
    
    def test_user_type_methods(self):
        """Test user type checking methods"""
        self.assertTrue(self.user.is_customer())
        self.assertFalse(self.user.is_agent())
        self.assertFalse(self.user.is_admin_user())
    
    def test_agent_user_creation(self):
        """Test agent user creation"""
        agent = User.objects.create_user(
            username='testagent',
            email='agent@example.com',
            password='agentpass123',
            user_type='agent'
        )
        self.assertTrue(agent.is_agent())
        self.assertFalse(agent.is_customer())
```

#### Property Model Tests
```python
from properties.models import Property, PropertyImage, Favorite
from decimal import Decimal

class PropertyModelTest(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user(
            username='agent',
            email='agent@example.com',
            password='pass123',
            user_type='agent'
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='pass123',
            user_type='customer'
        )
        self.property = Property.objects.create(
            title='Test Property',
            address='123 Test St',
            price=Decimal('500000.00'),
            bedrooms=3,
            bathrooms=Decimal('2.5'),
            square_footage=1800,
            description='A nice test property',
            agent=self.agent
        )
    
    def test_property_creation(self):
        """Test property is created correctly"""
        self.assertEqual(self.property.title, 'Test Property')
        self.assertEqual(self.property.agent, self.agent)
        self.assertEqual(self.property.status, 'available')
    
    def test_property_str_method(self):
        """Test string representation"""
        self.assertEqual(str(self.property), 'Test Property')
    
    def test_favorite_creation(self):
        """Test favorite creation and constraints"""
        favorite = Favorite.objects.create(
            user=self.customer,
            property=self.property
        )
        self.assertEqual(favorite.user, self.customer)
        self.assertEqual(favorite.property, self.property)
    
    def test_favorite_unique_constraint(self):
        """Test unique constraint on user-property combination"""
        Favorite.objects.create(user=self.customer, property=self.property)
        
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.customer, property=self.property)
    
    def test_property_sold_removes_favorites(self):
        """Test that favorites are removed when property is sold"""
        Favorite.objects.create(user=self.customer, property=self.property)
        
        # Change status to sold
        self.property.status = 'sold'
        self.property.save()
        
        # Check that favorite is removed
        self.assertFalse(
            Favorite.objects.filter(
                user=self.customer, 
                property=self.property
            ).exists()
        )
```

### View Testing

#### Authentication Views
```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class AuthenticationViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_login_view_post_success(self):
        """Test successful login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('core:dashboard'))
    
    def test_login_view_post_failure(self):
        """Test failed login"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')
    
    def test_logout_redirects(self):
        """Test logout redirects correctly"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertRedirects(response, reverse('accounts:login'))
```

#### Property Views
```python
class PropertyViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.agent = User.objects.create_user(
            username='agent',
            password='pass123',
            user_type='agent'
        )
        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )
        self.property = Property.objects.create(
            title='Test Property',
            address='123 Test St',
            price=Decimal('500000.00'),
            bedrooms=3,
            bathrooms=Decimal('2.5'),
            square_footage=1800,
            description='Test description',
            agent=self.agent
        )
    
    def test_property_list_view(self):
        """Test property list view"""
        response = self.client.get(reverse('properties:property_list'))
        self.assertEqual(response.status_code, 302)  # Redirects to login
        
        # Test with logged in user
        self.client.login(username='customer', password='pass123')
        response = self.client.get(reverse('properties:property_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Property')
    
    def test_property_detail_view(self):
        """Test property detail view"""
        self.client.login(username='customer', password='pass123')
        response = self.client.get(
            reverse('properties:property_detail', kwargs={'pk': self.property.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.property.title)
        self.assertContains(response, self.property.description)
    
    def test_property_create_view_agent_only(self):
        """Test only agents can create properties"""
        # Test with customer (should be forbidden)
        self.client.login(username='customer', password='pass123')
        response = self.client.get(reverse('properties:property_create'))
        self.assertEqual(response.status_code, 403)
        
        # Test with agent (should work)
        self.client.login(username='agent', password='pass123')
        response = self.client.get(reverse('properties:property_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_toggle_favorite_ajax(self):
        """Test favorite toggle functionality"""
        self.client.login(username='customer', password='pass123')
        
        # Add to favorites
        response = self.client.post(
            reverse('properties:toggle_favorite', kwargs={'pk': self.property.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_favorite'])
        
        # Remove from favorites
        response = self.client.post(
            reverse('properties:toggle_favorite', kwargs={'pk': self.property.pk}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        data = response.json()
        self.assertFalse(data['is_favorite'])
```

### Form Testing

```python
from accounts.forms import CustomerRegistrationForm, AgentRegistrationForm
from properties.forms import PropertyForm

class FormTest(TestCase):
    def test_customer_registration_form_valid(self):
        """Test valid customer registration form"""
        form_data = {
            'username': 'newcustomer',
            'email': 'customer@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        }
        form = CustomerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_customer_registration_form_password_mismatch(self):
        """Test password mismatch in registration form"""
        form_data = {
            'username': 'newcustomer',
            'email': 'customer@example.com',
            'password1': 'complexpass123',
            'password2': 'differentpass123'
        }
        form = CustomerRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_property_form_valid(self):
        """Test valid property form"""
        form_data = {
            'title': 'New Property',
            'address': '456 New St',
            'price': '600000.00',
            'bedrooms': 4,
            'bathrooms': '3.0',
            'square_footage': 2000,
            'description': 'A beautiful new property',
            'status': 'available'
        }
        form = PropertyForm(data=form_data)
        self.assertTrue(form.is_valid())
```

## Integration Tests

### Search Integration
```python
from search.models import SearchHistory, Recommendation
from search.views import search_properties

class SearchIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            user_type='customer'
        )
        self.agent = User.objects.create_user(
            username='agent',
            password='pass123',
            user_type='agent'
        )
        
        # Create test properties
        Property.objects.create(
            title='Modern Downtown Apartment',
            address='123 Downtown Ave',
            price=Decimal('450000.00'),
            bedrooms=2,
            bathrooms=Decimal('2.0'),
            square_footage=1200,
            description='Beautiful modern apartment in downtown area',
            agent=self.agent
        )
        
        Property.objects.create(
            title='Suburban Family Home',
            address='456 Suburb St',
            price=Decimal('650000.00'),
            bedrooms=4,
            bathrooms=Decimal('3.0'),
            square_footage=2400,
            description='Spacious family home with large backyard',
            agent=self.agent
        )
    
    def test_search_creates_history(self):
        """Test that search creates search history"""
        self.client.login(username='testuser', password='pass123')
        
        response = self.client.get(reverse('search:search'), {'q': 'downtown apartment'})
        self.assertEqual(response.status_code, 200)
        
        # Check search history was created
        self.assertTrue(
            SearchHistory.objects.filter(
                user=self.user,
                query='downtown apartment'
            ).exists()
        )
    
    def test_semantic_search_results(self):
        """Test semantic search returns relevant results"""
        self.client.login(username='testuser', password='pass123')
        
        response = self.client.get(reverse('search:search'), {'q': 'city center flat'})
        self.assertEqual(response.status_code, 200)
        
        # Should find the downtown apartment even though exact words don't match
        self.assertContains(response, 'Modern Downtown Apartment')
    
    def test_property_view_creates_search_history(self):
        """Test viewing property details creates search history"""
        self.client.login(username='testuser', password='pass123')
        
        property_obj = Property.objects.first()
        response = self.client.get(
            reverse('properties:property_detail', kwargs={'pk': property_obj.pk})
        )
        
        # Check search history entry was created
        self.assertTrue(
            SearchHistory.objects.filter(
                user=self.user,
                property=property_obj
            ).exists()
        )
```

### Messaging Integration
```python
from properties.models import PropertyMessage

class MessagingIntegrationTest(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer',
            password='pass123',
            user_type='customer'
        )
        self.agent = User.objects.create_user(
            username='agent',
            password='pass123',
            user_type='agent'
        )
        self.property = Property.objects.create(
            title='Test Property',
            address='123 Test St',
            price=Decimal('500000.00'),
            bedrooms=3,
            bathrooms=Decimal('2.5'),
            square_footage=1800,
            description='Test property',
            agent=self.agent
        )
    
    def test_send_message_workflow(self):
        """Test complete message sending workflow"""
        self.client.login(username='customer', password='pass123')
        
        # Send message
        response = self.client.post(
            reverse('properties:send_message', kwargs={'property_id': self.property.pk}),
            {'message': 'I am interested in this property'}
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check message was created
        message = PropertyMessage.objects.get(
            property=self.property,
            sender=self.customer
        )
        self.assertEqual(message.content, 'I am interested in this property')
        self.assertFalse(message.read)
    
    def test_agent_message_inbox(self):
        """Test agent can view message inbox"""
        # Create a message
        PropertyMessage.objects.create(
            property=self.property,
            sender=self.customer,
            content='Test message'
        )
        
        self.client.login(username='agent', password='pass123')
        response = self.client.get(reverse('properties:message_inbox'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test message')
```

## System Tests

### User Journey Tests
```python
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CustomerJourneyTest(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()  # Requires chromedriver
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def test_complete_customer_journey(self):
        """Test complete customer registration to property inquiry"""
        
        # 1. Register new customer
        self.selenium.get(f'{self.live_server_url}/accounts/register/customer/')
        
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('testcustomer')
        
        email_input = self.selenium.find_element(By.NAME, 'email')
        email_input.send_keys('customer@test.com')
        
        # Fill other required fields...
        
        submit_button = self.selenium.find_element(By.TYPE, 'submit')
        submit_button.click()
        
        # 2. Login
        self.selenium.get(f'{self.live_server_url}/accounts/login/')
        
        username_input = self.selenium.find_element(By.NAME, 'username')
        username_input.send_keys('testcustomer')
        
        password_input = self.selenium.find_element(By.NAME, 'password')
        password_input.send_keys('testpass123')
        
        submit_button = self.selenium.find_element(By.TYPE, 'submit')
        submit_button.click()
        
        # 3. Search for properties
        search_input = self.selenium.find_element(By.NAME, 'q')
        search_input.send_keys('downtown apartment')
        search_input.submit()
        
        # 4. View property details
        property_link = self.selenium.find_element(By.CLASS_NAME, 'property-card')
        property_link.click()
        
        # 5. Add to favorites
        favorite_button = self.selenium.find_element(By.CLASS_NAME, 'favorite-btn')
        favorite_button.click()
        
        # Wait for AJAX response
        WebDriverWait(self.selenium, 10).until(
            EC.text_to_be_present_in_element(
                (By.CLASS_NAME, 'favorite-btn'),
                'Remove from Favorites'
            )
        )
        
        # 6. Send message to agent
        message_textarea = self.selenium.find_element(By.NAME, 'message')
        message_textarea.send_keys('I am interested in viewing this property')
        
        send_button = self.selenium.find_element(By.CLASS_NAME, 'send-message-btn')
        send_button.click()
        
        # Verify success message
        success_message = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'alert-success'))
        )
        self.assertIn('message has been sent', success_message.text)
```

## Performance Tests

### Load Testing
```python
import time
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

class PerformanceTest(TestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123'
        )
        
        # Create multiple properties for testing
        self.agent = User.objects.create_user(
            username='agent',
            password='pass123',
            user_type='agent'
        )
        
        for i in range(100):
            Property.objects.create(
                title=f'Property {i}',
                address=f'{i} Test Street',
                price=Decimal('500000.00'),
                bedrooms=3,
                bathrooms=Decimal('2.0'),
                square_footage=1500,
                description=f'Test property number {i}',
                agent=self.agent
            )
    
    def test_property_list_performance(self):
        """Test property list view performance"""
        self.client.login(username='testuser', password='pass123')
        
        start_time = time.time()
        response = self.client.get(reverse('properties:property_list'))
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 2.0)  # Should load in under 2 seconds
    
    def test_search_performance(self):
        """Test search performance with many properties"""
        self.client.login(username='testuser', password='pass123')
        
        start_time = time.time()
        response = self.client.get(reverse('search:search'), {'q': 'test property'})
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 3.0)  # Search should complete in under 3 seconds
    
    @override_settings(DEBUG=False)
    def test_database_query_count(self):
        """Test database query efficiency"""
        self.client.login(username='testuser', password='pass123')
        
        with self.assertNumQueries(5):  # Should use minimal queries
            response = self.client.get(reverse('properties:property_list'))
            self.assertEqual(response.status_code, 200)
```

### AI Performance Tests
```python
from unittest.mock import patch, MagicMock

class AIPerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='pass123',
            user_type='customer'
        )
    
    @patch('search.views.model')
    def test_semantic_search_timeout(self, mock_model):
        """Test semantic search handles timeouts gracefully"""
        # Mock model to simulate timeout
        mock_model.encode.side_effect = TimeoutError("Model timeout")
        
        self.client.login(username='testuser', password='pass123')
        
        # Should fallback to basic search without error
        response = self.client.get(reverse('search:search'), {'q': 'test query'})
        self.assertEqual(response.status_code, 200)
    
    @patch('search.views.model')
    def test_recommendation_generation_performance(self, mock_model):
        """Test recommendation generation performance"""
        mock_model.encode.return_value = [[0.1, 0.2, 0.3]]
        
        start_time = time.time()
        
        # Trigger recommendation generation
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('search:recommendations'))
        
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 5.0)  # Should complete in under 5 seconds
```

## Security Tests

### Authentication Security
```python
class SecurityTest(TestCase):
    def test_password_strength_validation(self):
        """Test password strength requirements"""
        weak_passwords = [
            'password',
            '123456',
            'abc123',
            'password123'
        ]
        
        for weak_password in weak_passwords:
            form_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'password1': weak_password,
                'password2': weak_password
            }
            form = CustomerRegistrationForm(data=form_data)
            self.assertFalse(form.is_valid())
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        malicious_query = "'; DROP TABLE properties_property; --"
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('search:search'), {'q': malicious_query})
        
        # Should not cause any errors and properties should still exist
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Property.objects.exists())
    
    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        xss_script = '<script>alert("XSS")</script>'
        
        # Try to inject script in property description
        agent = User.objects.create_user(
            username='agent',
            password='pass123',
            user_type='agent'
        )
        
        property_obj = Property.objects.create(
            title='Test Property',
            address='123 Test St',
            price=Decimal('500000.00'),
            bedrooms=3,
            bathrooms=Decimal('2.0'),
            square_footage=1500,
            description=xss_script,
            agent=agent
        )
        
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(
            reverse('properties:property_detail', kwargs={'pk': property_obj.pk})
        )
        
        # Script should be escaped in the response
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;script&gt;')
    
    def test_unauthorized_access_protection(self):
        """Test protection against unauthorized access"""
        agent = User.objects.create_user(
            username='agent',
            password='pass123',
            user_type='agent'
        )
        
        other_agent = User.objects.create_user(
            username='other_agent',
            password='pass123',
            user_type='agent'
        )
        
        property_obj = Property.objects.create(
            title='Test Property',
            address='123 Test St',
            price=Decimal('500000.00'),
            bedrooms=3,
            bathrooms=Decimal('2.0'),
            square_footage=1500,
            description='Test description',
            agent=agent
        )
        
        # Other agent should not be able to edit this property
        self.client.login(username='other_agent', password='pass123')
        response = self.client.get(
            reverse('properties:property_update', kwargs={'pk': property_obj.pk})
        )
        
        self.assertEqual(response.status_code, 302)  # Should redirect
```

## Test Execution

### Running Tests

#### All Tests
```bash
# Run all tests
python manage.py test

# Run with verbose output
python manage.py test --verbosity=2

# Run tests in parallel
python manage.py test --parallel

# Run specific test module
python manage.py test tests.unit.test_models
```

#### Coverage Reports
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html

# View coverage in browser
open htmlcov/index.html
```

#### Performance Testing
```bash
# Install testing tools
pip install locust pytest-benchmark

# Run performance tests
python manage.py test tests.performance

# Run load tests with Locust
locust -f tests/load_tests.py --host=http://localhost:8000
```

### Continuous Integration

#### GitHub Actions Test Workflow
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage
    
    - name: Run tests
      run: |
        coverage run --source='.' manage.py test
        coverage xml
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost/postgres
        REDIS_URL: redis://localhost:6379/0
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Test Data Management

#### Fixtures
```python
# tests/fixtures/sample_data.py
from django.core.management.base import BaseCommand
from accounts.models import User
from properties.models import Property
from decimal import Decimal

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Create test users
        agent = User.objects.create_user(
            username='test_agent',
            email='agent@test.com',
            password='testpass123',
            user_type='agent'
        )
        
        customer = User.objects.create_user(
            username='test_customer',
            email='customer@test.com',
            password='testpass123',
            user_type='customer'
        )
        
        # Create test properties
        properties_data = [
            {
                'title': 'Downtown Luxury Condo',
                'address': '100 Downtown Plaza',
                'price': Decimal('750000.00'),
                'bedrooms': 2,
                'bathrooms': Decimal('2.0'),
                'square_footage': 1400,
                'description': 'Beautiful luxury condo in the heart of downtown'
            },
            {
                'title': 'Suburban Family Home',
                'address': '200 Maple Street',
                'price': Decimal('550000.00'),
                'bedrooms': 4,
                'bathrooms': Decimal('3.0'),
                'square_footage': 2200,
                'description': 'Perfect family home with large backyard'
            }
        ]
        
        for data in properties_data:
            Property.objects.create(agent=agent, **data)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created test data')
        )
```

#### Factory Boy Integration
```python
# tests/factories.py
import factory
from factory.django import DjangoModelFactory
from accounts.models import User
from properties.models import Property
from decimal import Decimal

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    user_type = 'customer'

class AgentFactory(UserFactory):
    user_type = 'agent'
    phone_number = factory.Faker('phone_number')
    bio = factory.Faker('text', max_nb_chars=200)

class PropertyFactory(DjangoModelFactory):
    class Meta:
        model = Property
    
    title = factory.Faker('catch_phrase')
    address = factory.Faker('address')
    price = factory.LazyFunction(lambda: Decimal(str(factory.Faker('random_int', min=200000, max=1000000).generate())))
    bedrooms = factory.Faker('random_int', min=1, max=5)
    bathrooms = factory.LazyFunction(lambda: Decimal(str(factory.Faker('random_int', min=1, max=4).generate())))
    square_footage = factory.Faker('random_int', min=800, max=3000)
    description = factory.Faker('text', max_nb_chars=500)
    agent = factory.SubFactory(AgentFactory)
```

## Testing Best Practices

### Test Organization
- **Descriptive Names**: Use clear, descriptive test method names
- **Single Responsibility**: Each test should test one specific functionality
- **Independent Tests**: Tests should not depend on each other
- **Fast Execution**: Keep tests fast to encourage frequent running

### Data Management
- **Use Factories**: Use Factory Boy for generating test data
- **Clean State**: Ensure clean database state between tests
- **Minimal Data**: Create only the data needed for each test

### Assertions
- **Specific Assertions**: Use specific assertion methods
- **Error Messages**: Include meaningful error messages
- **Edge Cases**: Test boundary conditions and edge cases

### Maintenance
- **Regular Updates**: Keep tests updated with code changes
- **Refactoring**: Refactor tests to reduce duplication
- **Documentation**: Document complex test scenarios
- **Review**: Include tests in code review process
