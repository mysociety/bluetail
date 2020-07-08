from io import StringIO
from django.test import TestCase
from django.core.management import call_command


class TestScanContractsCommand(TestCase):
    def test_it_runs(self):
        # Make sure we've got the flags etc loaded.
        call_command('insert_prototype_data')
        call_command('insert_contracts_finder_data')

        call_command('scan_contracts')
