from django.test import Client, TestCase
from django.core.management import call_command
from django.urls import reverse

from bluetail.models import OCDSReleaseJSON, OCDSParty


class TestTendererPage(TestCase):
   def setUp(self):
       call_command('insert_prototype_data')
       self.client = Client()

   def test_flag_rendering(self):
       url = reverse('ocds-tenderer', kwargs={
           "ocid": "ocds-123abc-PROC-20-0001",
           "tenderer_id": "PROC-20-0001/a",
       })
       response = self.client.get(url)

       self.assertEqual(response.status_code, 200)
       self.assertContains(response, 'Synomus Technology Services Ltd')
       self.assertContains(response, 'Invalid company ID')
