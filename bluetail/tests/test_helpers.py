import csv
import os

from django.conf import settings
from django.test import TestCase

from bluetail import models
from bluetail.helpers import FlagHelperFunctions
from bluetail.tests.fixtures import insert_flags, insert_flag_attachments


class TestFlagHelperFunctions(TestCase):

    helper = FlagHelperFunctions()

    def setUp(self):
        insert_flags()
        insert_flag_attachments()

    def test_get_flags_for_scheme_and_id(self):
        scheme, id = ("GB-LAC", "1602647563")
        flags = self.helper.get_flags_for_scheme_and_id(scheme, id)
        assert any(flag.flag_name == "company_id_invalid" for flag in flags)
