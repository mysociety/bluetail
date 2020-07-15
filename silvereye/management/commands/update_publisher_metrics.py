"""
Command to create an generate publisher metrics
"""
import logging
import os

from django.core.management import BaseCommand
from django.db import connections

import silvereye

logger = logging.getLogger('django')

SILVEREYE_DIR = silvereye.__path__[0]
METRICS_SQL_DIR = os.path.join(SILVEREYE_DIR, "metrics", "sql")


class Command(BaseCommand):
    help = "Generates publisher metrics for tenders"

    def handle(self, *args, **kwargs):
        sql_files = os.listdir(METRICS_SQL_DIR)
        with connections['default'].cursor() as cursor:
            for sql_file in sql_files:
                if sql_file.endswith(".sql"):
                    try:
                        file_path = os.path.join(METRICS_SQL_DIR, sql_file)
                        sql = open(file_path).read()
                        logger.info(f"Executing metric sql from file {file_path}")
                        cursor.execute(sql)
                    except:
                        logger.error(f"Error with sql_file {sql_file}")
