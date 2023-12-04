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

import difflib
import json
import logging
import os
import time
from datetime import datetime

import yaml
from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth  # for Basic Auth

import github_apis

load_dotenv('environment.env')

CATALYST_CENTER_URL = os.getenv('CATALYST_CENTER_URL')
CATALYST_CENTER_USER = os.getenv('CATALYST_CENTER_USER')
CATALYST_CENTER_PASS = os.getenv('CATALYST_CENTER_PASS')

GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_REPO = os.getenv('GITHUB_REPO')

NETWORK_CONFIGS_PATH = 'network_configs/'

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

CATALYST_CENTER_AUTH = HTTPBasicAuth(CATALYST_CENTER_USER, CATALYST_CENTER_PASS)
FILE_NAME = 'custom_network_compliance.yaml'


# noinspection PyTypeChecker
def main():
    """
    This application will get device config CLI configurations form GitHub. It will identify if devices are configured with
    the CLI commands based on specific rules.
    The files from GitHub include:
     - filters to match the devices, example device role, family
     - CLI commands that will be validated on each device
    """

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(level=logging.INFO)

    current_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logging.info(' Application "device_config_compliance.py" Start, ' + current_time)

    # get the repos for user
    repos = github_apis.get_private_repos(username=GITHUB_USERNAME, github_token=GITHUB_TOKEN)

    # verify if repo exists
    if GITHUB_REPO not in repos:
        logging.info(' Repo "' + GITHUB_REPO + '" not found!')
        return
    logging.info(' Repo "' + GITHUB_REPO + '" found!')

    # get the device config  compliance intent file
    file_content = github_apis.get_repo_file_content(username=GITHUB_USERNAME,
                                                     repo_name=GITHUB_REPO,
                                                     file_name=FILE_NAME)
    logging.info(' File "' + FILE_NAME + '" found!')

    # parse the input data
    intent_config = yaml.safe_load(file_content)
    aaa_config = intent_config['aaa_config']['commands']
    ntp_config = intent_config['ntp_config']['commands']

    # parse the device policy
    device_role = intent_config['device_filter']['device_role']
    device_family = intent_config['device_filter']['device_family']

    logging.info(' Device configs from GitHub:')
    logging.info('   aaa_config: \n' + aaa_config)
    logging.info('   ntp_config: \n' + ntp_config)

    # save the config compliance to files
    with open(NETWORK_CONFIGS_PATH + 'aaa_config.txt', 'w') as f:
        f.write(aaa_config)

    # save the config compliance to files
    with open(NETWORK_CONFIGS_PATH + 'ntp_config.txt', 'w') as f:
        f.write(ntp_config)

    logging.info(' Compliance device filter:')
    logging.info('   device_role: ' + device_role)
    logging.info('   device_family: ' + device_family)

    # create a DNACenterAPI "Connection Object" to use the Python SDK
    catalyst_center_api = DNACenterAPI(username=CATALYST_CENTER_USER, password=CATALYST_CENTER_PASS,
                                       base_url=CATALYST_CENTER_URL, version='2.3.5.3',
                                       verify=False)

    # collect device inventory
    # get the device count
    response = catalyst_center_api.devices.get_device_count()
    device_count = response['response']
    logging.info(' Number of devices managed by Catalyst Center: ' + str(device_count))

    # get the device info list
    offset = 1
    limit = 500
    device_list = []
    while offset <= device_count:
        response = catalyst_center_api.devices.get_device_list(offset=offset)
        offset += limit
        device_list.extend(response['response'])
    logging.info(' Collected the device list from Catalyst Center')

    # create device inventory, add location and fabric roles

    device_inventory = []
    for device in device_list:
        # select which inventory to add the device to
        if device.family != "Unified AP":
            device_id = device['id']
            device_management_ip_address = device['managementIpAddress']

            device_details = {'hostname': device['hostname']}
            device_details.update({'device_ip': device['managementIpAddress']})
            device_details.update({'device_id': device['id']})
            device_details.update({'version': device['softwareVersion']})
            device_details.update({'device_family': device['type']})
            device_details.update({'role': device['role']})

            # get the device site hierarchy
            response = catalyst_center_api.devices.get_device_detail(identifier='uuid', search_by=device_id)
            site = response['response']['location']
            device_details.update({'site': site})

            # get the device fabric role
            device_sda_roles = []
            try:
                response = catalyst_center_api.sda.get_device_role_in_sda_fabric(
                    device_management_ip_address=device_management_ip_address)
                device_sda_roles = response['roles']
            except:
                pass
            device_details.update({'sda_roles': device_sda_roles})

            device_inventory.append(device_details)

    logging.info(' Retrieved the device location and fabric role')

    # save device inventory to json formatted file
    with open(NETWORK_CONFIGS_PATH + 'device_inventory.json', 'w') as f:
        f.write(json.dumps(device_inventory, indent=4))
    logging.info(' Saved the device inventory to file "device_inventory.json"')

    os.chdir(NETWORK_CONFIGS_PATH)

    # collect the device configs for the devices that match the role
    logging.info(' Compliance checks for devices that match the device filter')
    for item in device_inventory:
        if item['role'] == device_role and item['device_family'] == device_family:
            response = catalyst_center_api.devices.get_device_config_by_id(item['device_id'])
            device_config = response['response']
            with open(item['hostname'] + '_config.txt', 'w') as f:
                f.write(device_config)
            logging.info(' Saved the device config ' + item['hostname'] + '_config.txt')
            logging.info(' Device: ' + item['hostname'] + ' :')

            # check common lines between the two files - device config compliance commands and running config
            aaa_config_file = open('aaa_config.txt', 'r').readlines()
            ntp_config_file = open('ntp_config.txt', 'r').readlines()
            config_file = open(item['hostname'] + '_config.txt', 'r').readlines()

            aaa_difference = difflib.Differ()
            aaa_commands_list = []
            for line in aaa_difference.compare(aaa_config_file, config_file):
                if line.startswith('-'):
                    clean_line = line.strip()
                    aaa_commands_list.append(clean_line)
            if len(aaa_commands_list) == 0:
                logging.info('    - AAA config check passed')
            else:
                logging.info('    - AAA config check failed, missing commands:')
                for command in aaa_commands_list:
                    logging.info('        ' + command)

            ntp_difference = difflib.Differ(charjunk=lambda x: x in [',', '.', '-', "'"])
            ntp_commands_list = []
            for line in ntp_difference.compare(ntp_config_file, config_file):
                if line.startswith('-'):
                    clean_line = line.strip()
                    ntp_commands_list.append(clean_line)
            if len(ntp_commands_list) == 0:
                logging.info('    - NTP config check passed')
            else:
                logging.info('    - NTP config check failed, missing commands:')
                for command in ntp_commands_list:
                    logging.info('        ' + command)

    date_time = str(datetime.now().replace(microsecond=0))
    logging.info(' End of Application "device_config_compliance.py" Run: ' + date_time)

    return


if __name__ == '__main__':
    main()
