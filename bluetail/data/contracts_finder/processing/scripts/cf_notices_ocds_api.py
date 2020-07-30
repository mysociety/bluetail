# coding=utf-8
"""
Gets OCDS JSON notices from the Contracts Finder API, and insert 100 with sufficient content,
with an option to update these using the existing OCIDs

API Info

https://content-api.publishing.service.gov.uk/#gov-uk-content-api
https://www.gov.uk/government/publications/open-contracting
https://www.contractsfinder.service.gov.uk/apidocumentation/home
https://www.contractsfinder.service.gov.uk/Published/Notice/releases/450280ac-b308-4df1-bdc5-9ede0c5c7e9f.json
https://www.contractsfinder.service.gov.uk/Published/Notice/releases/5fecfc86-007a-4966-94e2-c695018ec2dd.json
"""
import argparse
import shutil

from urllib3.util import Retry
import json
from datetime import datetime, timedelta, date
from collections import OrderedDict
import logging
import random
import os

import pandas as pd
from django.conf import settings
from requests.adapters import HTTPAdapter
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from ocdskit.upgrade import upgrade_10_11

import requests
import logging.config
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
})

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL")
OCDS_OUTPUT_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data", "contracts_finder", "ocds")
PROCESSING_DIR = os.path.join(settings.BLUETAIL_APP_DIR, "data", "contracts_finder", "processing")
SUPPLIER_DF_PATH = os.path.join(settings.BLUETAIL_APP_DIR, "data", "contracts_finder", "processing", 'openopps_supplier_matches.csv')


def session_with_backoff(
        total_retries=25,
):
    """
    The backoff wait time increases with this equation
    {backoff factor} * (2 ** ({number of total retries} - 1))

    :param total_retries:
    :return:
    """
    s = requests.Session()
    retries = Retry(total=total_retries,
                    read=10,
                    connect=10,
                    backoff_factor=2,
                    status_forcelist=[500, 502, 503, 504, 429],
                    respect_retry_after_header=False,
                    # method_whitelist=frozenset(['GET', 'POST']),
                    method_whitelist=False,
                    )

    adapter = HTTPAdapter(max_retries=retries)
    s.mount('http://', adapter)
    s.mount('https://', adapter)
    return s


def search(publishedFrom=None, publishedTo=None):
    logger.info("Searching CF OCDS award notices from {0} to {1}".format(publishedFrom, publishedTo))

    ocds_api_url = "https://www.contractsfinder.service.gov.uk/Published/Notices/OCDS/Search"
    max_page = 1
    page = 1
    ocds_api_params = {
        "publishedFrom": publishedFrom,
        "publishedTo": publishedTo,
        "stages": [
            "award"
        ],
        "orderBy": "publishedDate",
        "order": "DESC",
        "size": 100,
        "page": page
    }
    if not publishedFrom:
        ocds_api_params.pop("publishedFrom")
    if not publishedTo:
        ocds_api_params.pop("publishedTo")
        ocds_api_params["order"] = "DESC"

    logger.info("Making CF OCDS API request. From %s to %s.", publishedFrom, publishedTo)

    session = session_with_backoff()

    while page <= max_page:
        if page == 1:
            logger.info("Page %s", page)
        else:
            logger.info("Page %s of %s", page, max_page)
        response = session.get(ocds_api_url, params=ocds_api_params)
        response = response.json()

        if page == 1:
            count = response.get('hitsCount')
            logger.info("hitsCount %s", count)
        max_page = response.get("maxPage")

        results = response.get('results')

        for notice in results:
            ocid = notice["releases"][0]["ocid"]
            if ocid == 'ocds-b5fd17-':
                continue

            yield notice
        page += 1
        ocds_api_params["page"] = page


class CFDownload(object):
    def __init__(self, **kwargs):

        self.session = session_with_backoff()
        self.too_few_suppliers_skipped = 0
        self.too_few_matched_suppliers_skipped = 0
        self.saved = 0
        self.fromDate = None
        self.toDate = None
        self.rows = kwargs['rows']
        self.saved_files = kwargs.get('update')
        self.dataset = kwargs.get('dataset')

        if kwargs.get('days') != None:
            self.fromDate = str(date.today() - timedelta(days=kwargs['days']))
            self.toDate = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            if kwargs.get('fromdate') != None:
                self.fromDate = kwargs['fromdate']
            else:
                self.fromDate = str(date.today() - timedelta(days=7))
            if kwargs.get('todate') != None:
                self.toDate = kwargs['todate']
            else:
                self.toDate = str(date.today())

        if self.dataset == 'bodsmatch':
            self.dataset_dir = 'json_1_1_bods_match'
        elif self.dataset == 'suppliermatch':
            self.dataset_dir = 'json_1_1_supplier_ids_match'
        elif self.dataset == 'raw':
            self.dataset_dir = 'json_1_1_raw'

    def get_notices(self, datasetpth='json_1_1_bods_match'):
        """ Get notices from Contracts Finder API
            With option of searching date periods
            or searching existing OCIDs that have a sufficient number of matched suppliers.
         """
        session = session_with_backoff()
        if self.saved_files:
            dirpath = os.path.join(OCDS_OUTPUT_DIR, datasetpth)
            for filename in os.listdir(dirpath):
                filepath = os.path.join(dirpath, filename)
                with open(filepath) as notice:
                    resp = json.load(notice)
                    ocds = json.loads(session.get(resp['uri']).content)
                    yield ocds
        else:

            notices = search(publishedFrom=self.fromDate, publishedTo=self.toDate)
            for n in notices:
                yield n


def fix_cf_supplier_ids(json):
    """ Modify Contracts Finder OCDS JSON enough to be processed """
    # Fixing to match current version, to be processed by ocdskit
    json['version'] = '1.0'
    # Giving suppliers distinct IDs (source sets all supplier IDs to zero)
    for i, supplier in enumerate(json['releases'][0]['awards'][0]['suppliers']):
        json['releases'][0]['awards'][0]['suppliers'][i]['id'] = str(i)

    return json


def clean_and_convert_to_1_1(row):
    rowjson = json.dumps(row)
    rowjson = json.loads(rowjson)

    # Fix OCDS errors

    rowjson = fix_cf_supplier_ids(rowjson)

    # Convert to 1.1 OCDS
    json_1_1 = upgrade_10_11(json.loads(json.dumps(rowjson), object_pairs_hook=OrderedDict))
    # json_1_1 = json.dumps(json_1_1)
    return json_1_1


def match_supplier_info(suppliername):
    """ Adding supplier details from table where a match is found. """
    try:
        row = supplier_df.loc[suppliername]
    except KeyError:
        logger.debug('Supplier match not found for %s', suppliername)
        return None

    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]

    supplier_match = {
        'id': row['id'],
        'scheme': row['scheme'],
        'legalName': suppliername
    }
    return supplier_match


def get_company_statements(
        company_id,
        scheme='GB-COH',
        elastic_conn=Elasticsearch(ELASTICSEARCH_URL, verify_certs=True),
):
    """ Check for an existing BODS document for a supplier ID """
    s = Search(using=elastic_conn, index="bods") \
        .filter("term", identifiers__scheme__keyword=scheme) \
        .filter("term", identifiers__id__keyword=company_id)

    res = s.execute()
    statements = [s["_source"] for s in res.hits.hits]
    return statements


def update_parties(ocdsjson, dataset='bodsmatch'):
    """ Change suppliers to tenderers to reflect tender process. """

    parties = ocdsjson['releases'][0]['parties']
    supplier_names = []
    newparties = []
    tenderers = []

    for i, party in enumerate(parties):
        if 'supplier' in party['roles']:

            supplier = party['name']
            if supplier in supplier_names:
                logger.debug('Removing duplicated supplier %s', supplier)
                continue
            supplier_names.append(supplier)
            supplier_matched_id = match_supplier_info(supplier)

            if dataset in ('bodsmatch', 'suppliermatch'):
                # Skips adding supplier if a match isn't found in Companies House
                if not supplier_matched_id:
                    continue

            if dataset == 'bodsmatch':
                # Skips adding supplier if not found in BODS elastic index
                bodsmatch = get_company_statements(supplier_matched_id['id'])
                if not bodsmatch:
                    continue

            if supplier_matched_id:
                # Adding supplier info from Companies house
                party['identifier'] = supplier_matched_id

            party['roles'].append('tenderer')
            party['id'] = str(i)

            tenderers.append({
                'id': str(i),
                'name': supplier
            })
            newparties.append(party)
        else:
            newparties.append(party)

    ocdsjson['releases'][0]['parties'] = newparties
    ocdsjson['releases'][0]['tender']['numberOfTenderers'] = len(tenderers)
    ocdsjson['releases'][0]['tender']['tenderers'] = tenderers
    ocdsjson['releases'][0]['awards'][0]['suppliers'] = tenderers
    return ocdsjson


def fix_dates(d_json, aws):
    tenderenddate = d_json['releases'][0]['tender']['tenderPeriod']['endDate']
    weeksback = random.randint(1, 12)
    newpubdate = (datetime.strptime(tenderenddate, '%Y-%m-%dT%H:%M:%SZ') - timedelta(weeks=weeksback)).strftime(
        '%Y-%m-%dT%H:%M:%SZ')
    newpubdate_str = str(newpubdate)
    d_json['releases'][0]['date'] = newpubdate_str

    # Move contract period to tender section
    if aws["contractPeriod"]:
        d_json['releases'][0]['tender']["contractPeriod"] = aws["contractPeriod"]
    try:
        for item in d_json['releases'][0]['tender']['milestones']:
            if item['title'] == 'Contract start':
                d_json['releases'][0]['tender']["contractPeriod"] = {}
                d_json['releases'][0]['tender']["contractPeriod"]['startDate'] = item['dueDate']
            if item['title'] == 'Contract end':
                d_json['releases'][0]['tender']["contractPeriod"]['endDate'] = item['dueDate']
        del d_json['releases'][0]['tender']['milestones']
    except:
        logging.debug('No contract dates found', exc_info=True)

    return d_json


def aws_to_tender(json_ocds, dataset='bodsmatch'):
    """ Converts a Contracts Finder award to tender """

    awards = json_ocds['releases'][0]['awards']
    if len(awards) > 1:
        logging.warning('Notice contains multiple awards which are not currently processed')
    award_info = awards[0]
    json_ocds['releases'][0]['tag'][0] = 'tender'

    json_ocds = update_parties(json_ocds, dataset=dataset)
    json_ocds = fix_dates(json_ocds, award_info)
    return json_ocds


def clean_and_dump_1_1_tenders(notice_json, datasetinfo):

    ocid = notice_json['releases'][0]['ocid']
    if datasetinfo.dataset == 'bodsmatch':
        notice_json['releases'][0]['ocid'] = ocid.replace('-b5fd17-', '-b5fd17bodsmatch-')
    elif datasetinfo.dataset == 'suppliermatch':
        notice_json['releases'][0]['ocid'] = ocid.replace('-b5fd17-', '-b5fd17suppliermatch-')
    elif datasetinfo.dataset == 'raw':
        notice_json['releases'][0]['ocid'] = ocid.replace('-b5fd17-', '-b5fd17raw-')

    ocid = notice_json['releases'][0]['ocid']
    filedir = os.path.join(OCDS_OUTPUT_DIR, datasetinfo.dataset_dir, '%s.json' % ocid)
    with open(filedir, 'w') as dataloc:
        final_json = json.dumps(notice_json, indent=2)
        logger.info('Saved notice %s' % filedir)
        dataloc.write(final_json)


def run(**kwargs):

    dataset = kwargs.get('dataset')
    clear = kwargs.get('clear')
    downloader = CFDownload(**kwargs)
    global supplier_df
    supplier_df = pd.read_csv(
        SUPPLIER_DF_PATH,
        index_col='legal_name'
    )

    # Clear existing files if --clear
    dataset_path = os.path.join(OCDS_OUTPUT_DIR, downloader.dataset_dir)

    if clear and os.path.exists(dataset_path):
        shutil.rmtree(dataset_path)

    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    i = 0
    for i, notice_ocds_json in enumerate(downloader.get_notices(datasetpth=downloader.dataset_dir)):
        try:
            uri = notice_ocds_json["uri"]

            ocid = notice_ocds_json["releases"][0]["ocid"]
            number_of_suppliers = len(notice_ocds_json['releases'][0]['awards'][0]['suppliers'])
            if number_of_suppliers < 2:
                logger.debug('Notice %s contains less than 2 suppliers - skipping' % ocid)
                downloader.too_few_suppliers_skipped += 1
                continue

            notice_ocds_1_1_json = clean_and_convert_to_1_1(notice_ocds_json)

            # Convert award notices to tender notices
            tenders_json = aws_to_tender(notice_ocds_1_1_json, dataset=dataset)
            if tenders_json['releases'][0]['tender']['numberOfTenderers'] < 2:
                logger.debug('Notice %s has less than 2 matched suppliers - skipping' % ocid)
                downloader.too_few_matched_suppliers_skipped += 1
                continue

            clean_and_dump_1_1_tenders(tenders_json, downloader)

            downloader.saved += 1
            if downloader.saved >= downloader.rows:
                logger.info(f'Saved {downloader.saved} notices')
                break

        except KeyboardInterrupt:
            break
        except:
            logger.error('Failed to process notice {}'.format(uri), exc_info=True)
            continue

    logger.info('Processed {0} notices.'.format(i))
    logger.info('Saved {0} notices.'.format(downloader.saved))
    logger.info('Skipped {0} notices.'.format(downloader.too_few_suppliers_skipped + downloader.too_few_matched_suppliers_skipped))


def add_arguments(parser):
    parser.add_argument("-s", "--dataset", type=str, help="Options of 'bodsmatch', 'suppliermatch' or 'raw'", default='bodsmatch')
    parser.add_argument("-u", "--update", action='store_true', default=False, help="Update notices already outputted by uri of saved files.")
    parser.add_argument("-c", "--clear", action='store_true', default=False, help="Clear existing files before downloading.")
    parser.add_argument("-d", "--days", type=int, help="Import the last x days of notices.")
    parser.add_argument("-r", "--rows", type=int, help="Import x notices in total.", default=100)
    parser.add_argument("-f", "--fromdate", help="Import from date. YYYY-MM-DD", default='2020-01-01')
    parser.add_argument("-t", "--todate", help="Import to date. YYYY-MM-DD", default='2020-06-01')
    return parser


def kwargs_from_parsed_args(args):
    return {k: v for k, v in vars(args).items() if v is not None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = add_arguments(parser)
    parser.print_help()
    args = parser.parse_args()

    try:
        run(**kwargs_from_parsed_args(args))
    except Exception:
        logger.critical("Contracts Finder download error.", exc_info=True)
