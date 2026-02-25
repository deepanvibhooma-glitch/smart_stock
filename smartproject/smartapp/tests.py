from django.test import TestCase
from django.urls import reverse
from .models import Category
import json

class CategoryTests(TestCase):
    def test_api_add_category(self):
        url = reverse('api_add_category')
        data = {
            'name': 'Test Category',
            'description': 'Test Description'
        }
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['category']['name'], 'Test Category')
        self.assertTrue(Category.objects.filter(name='Test Category').exists())

    def test_api_add_category_no_name(self):
        url = reverse('api_add_category')
        data = {
            'description': 'Test Description'
        }
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
