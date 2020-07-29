"""
Rough script to store SQL queries to CSV while preparing CF data
"""
import os

from sqlalchemy import create_engine
import pandas as pd
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', "proj.settings")
django.setup()

OPENOPPS_DB_URL = os.environ.get('OPENOPPS_DB_URL')
SQL_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data", "contracts_finder", "processing", "sql")
CSV_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data", "contracts_finder", "processing", "csv")


def save_sql_to_csv(sql_or_path, csv_path):
    engine = create_engine(OPENOPPS_DB_URL)

    if os.path.exists(sql_or_path):
        sql = open(sql_or_path).read()
    else:
        sql = sql_or_path

    df = pd.read_sql(sql, engine)

    df.to_csv(csv_path, index=False)

    return df


def save_cf_data():
    get_cf_data_with_CHIDs_100 = os.path.join(SQL_DIR, "get_cf_data_with_CHIDs_100.sql")
    csv_path = os.path.join(CSV_DIR, "get_cf_data_with_CHIDs_100.csv")
    save_sql_to_csv(get_cf_data_with_CHIDs_100, csv_path)


if __name__ == '__main__':
    save_cf_data()
