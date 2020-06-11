from django.test import TestCase
from django.urls import reverse


class SilvereyeTests(TestCase):
    def test_upload_results(self):
        response = self.client.get(reverse('publisher-hub'))
        self.assertEqual(response.status_code, 200)
