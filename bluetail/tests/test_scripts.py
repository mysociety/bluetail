import os
import subprocess
from unittest import skip

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

SCRIPTS_DIR = os.path.join(settings.BASE_DIR, "script")


class TestFlagHelperFunctions(TestCase):

    def setUp(self):
        pass

    @skip("Only for local testing")
    def test_script_setup(self):
        db = settings.DATABASES["default"]
        test_db_url = "postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}".format(
            USER=db["USER"],
            PASSWORD=db["PASSWORD"],
            HOST=db["HOST"],
            PORT=db["PORT"],
            NAME=db["NAME"],
        )
        my_env = os.environ.copy()
        my_env["DATABASE_URL"] = test_db_url

        setup_script_path = os.path.join(SCRIPTS_DIR, "setup")

        subprocess.call(setup_script_path, env=my_env, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

        # We could use call_command() here instead, or test both
        # call_command(setup_script_path, env=my_env, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
