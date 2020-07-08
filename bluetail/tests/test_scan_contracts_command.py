from io import StringIO
from django.test import TestCase
from django.core.management import call_command


class TestScanContractsCommand(TestCase):
    def test_it_runs(self):
        # Make sure we've got the flags etc loaded.
        call_command('insert_example_data')

        # Send stdout/err to this StringIO object so it doesn't clutter test output.
        null = StringIO()
        call_command('scan_contracts', stdout=null, stderr=null)
