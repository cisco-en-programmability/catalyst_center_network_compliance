#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Gabriel Zapodeanu TME, ENB"
__email__ = "gzapodea@cisco.com"
__version__ = "0.1.0"
__copyright__ = "Copyright (c) 2023 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

import logging
import os
import time
import json
import yaml
import base64
import github_apis

from github import Github
from datetime import datetime

from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth  # for Basic Auth
from pprint import pprint


load_dotenv('environment.env')

CATALYST_CENTER_URL = os.getenv('CATALYST_CENTER_URL')
CATALYST_CENTER_USER = os.getenv('CATALYST_CENTER_USER')
CATALYST_CENTER_PASS = os.getenv('CATALYST_CENTER_PASS')

GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')

NETWORK_STATE_PATH = 'network_settings/'

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

CATALYST_CENTER_AUTH = HTTPBasicAuth(CATALYST_CENTER_USER, CATALYST_CENTER_PASS)
FILE_NAME = 'intent_network_settings.yaml'

def main():
    """
    This app will pull network settings file from GitHub and identify if all sites are configured with the defined network settings.
    """

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(level=logging.INFO)

    current_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logging.info(' Application "network_settings_compliance.py" Start, ' + current_time)

    # get the repos for user
    repos = github_apis.get_private_repos()

    # verify if repo exists
    if GITHUB_REPO not in repos:
        logging.info(' Repo "' + GITHUB_REPO + '" not found!')
        return
    logging.info(' Repo "' + GITHUB_REPO + '" found!')

    # get the network settings intent file
    intent_network_settings = github_apis.get_repo_file_content(username=GITHUB_USERNAME, repo_name=GITHUB_REPO, file_name=FILE_NAME)
    logging.info(' File "' + FILE_NAME + '" found!')

    # decode the YAMl file
    intent_config = yaml.safe_load(intent_network_settings)

    # parse the input data
    site_name_hierarchy = intent_config['site_info']['site_name_hierarchy']
    banner_message = intent_config['banner']['message']
    ntp_server = intent_config['ntp_server']['server_ip']
    dns_server = intent_config['dns_server']['server_ip']

    logging.info(' Intent network settings from GitHub:')
    logging.info('   Site hierarchy: ' + site_name_hierarchy)
    logging.info('   Banner: ' + banner_message)
    logging.info('   NTP server: ' + ntp_server)
    logging.info('   DNS server: ' + dns_server)

    # create a DNACenterAPI "Connection Object" to use the Python SDK
    catalyst_center_api = DNACenterAPI(username=CATALYST_CENTER_USER, password=CATALYST_CENTER_PASS, base_url=CATALYST_CENTER_URL, version='2.3.5.3',
                                       verify=False)

    # get the site Id for the site with the name
    response = catalyst_center_api.sites.get_site(name=site_name_hierarchy)
    site_id = response['response'][0]['id']
    logging.info(' The site id for the site: "' + site_name_hierarchy + '" is: ' + site_id)

    # collect the network settings for site
    response = catalyst_center_api.network_settings.get_network_v2(site_id)
    site_network_settings = response['response']
    logging.info(' Collected the site settings')

    # prepare a network settings report
    network_settings_report = {}

    # verify the settings for NTP
    network_settings_ntp_status = {'ntp': 'not_compliant'}
    for item in site_network_settings:
        if item['instanceType'] == 'ip' and item['key'] == 'ntp.server' and item['value'][0] == ntp_server:
            network_settings_ntp_status.update({'ntp': 'compliant'})
            break

    # verify the settings for DNS
    network_settings_dns_status = {'dns': 'not_compliant'}
    for item in site_network_settings:
        if item['instanceType'] == 'dns' and item['key'] == 'dns.server' and item['value'][0]['primaryIpAddress'] == dns_server:
            network_settings_dns_status.update({'dns': 'compliant'})
            break

    # verify the settings for Banner message
    network_settings_banner_status = {'banner': 'not_compliant'}
    for item in site_network_settings:
        if item['instanceType'] == 'banner' and item['value'][0]['bannerMessage'] == banner_message:
            network_settings_banner_status.update({'banner': 'compliant'})
            break

    # merge the compliance reports for each network settings
    network_settings_report = {**network_settings_dns_status, **network_settings_ntp_status, **network_settings_banner_status}

    logging.info(' Network Settings compliance report:')
    logging.info('   ' + json.dumps(network_settings_report))

    date_time = str(datetime.now().replace(microsecond=0))
    logging.info(' End of Application "network_settings_compliance.py" Run: ' + date_time)

    return


if __name__ == '__main__':
    main()