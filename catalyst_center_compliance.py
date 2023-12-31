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

import json
import logging
import os
import time
from datetime import datetime

from dnacentersdk import DNACenterAPI
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth  # for Basic Auth

load_dotenv('environment.env')

CATALYST_CENTER_URL = os.getenv('CATALYST_CENTER_URL')
CATALYST_CENTER_USER = os.getenv('CATALYST_CENTER_USER')
CATALYST_CENTER_PASS = os.getenv('CATALYST_CENTER_PASS')

os.environ['TZ'] = 'America/Los_Angeles'  # define the timezone for PST
time.tzset()  # adjust the timezone, more info https://help.pythonanywhere.com/pages/SettingTheTimezone/

CATALYST_CENTER_AUTH = HTTPBasicAuth(CATALYST_CENTER_USER, CATALYST_CENTER_PASS)


def main():
    """
    This app will create a Catalyst Center non-compliant devices report, based on out-of-the-box compliance features.
    It will call the compliance and device details APIs to identify all devices non-compliant
    for various compliance validations. It will create a report for non-compliant devices with role "CORE".
    The app may be part of a CI/CD pipeline to run on-demand or scheduled.
    This app is using the Python SDK to make REST API calls to Cisco DNA Center.
    """

    # logging, debug level, to file {application_run.log}
    logging.basicConfig(level=logging.INFO)

    current_time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    logging.info(' Application "catalyst_center_compliance.py" Start, ' + current_time)

    # verify if folder for state files exist

    # create a DNACenterAPI "Connection Object" to use the Python SDK
    catalyst_center_api = DNACenterAPI(username=CATALYST_CENTER_USER, password=CATALYST_CENTER_PASS,
                                       base_url=CATALYST_CENTER_URL, version='2.3.5.3',
                                       verify=False)

    get_compliance_response = catalyst_center_api.compliance.get_compliance_detail()
    network_compliance_info = get_compliance_response['response']
    logging.info(' Collected Catalyst Center network compliance state')

    # sort the list of compliance status, by device Id
    network_compliance = sorted(network_compliance_info, key=lambda x: x['deviceUuid'])

    # identify all compliance checks in environment
    compliance_type = []
    for item in network_compliance:
        item_compliance = item['complianceType']
        if item_compliance not in compliance_type:
            compliance_type.append(item_compliance)

    logging.info(' Type of compliance checks: ' + json.dumps(compliance_type, indent=4))

    # create report for non-compliant devices for each compliance type
    compliance_report = {}
    for item in compliance_type:
        compliance_report.update({item: []})

    # loop through each item in compliance and append to report, to the specific category
    for item in network_compliance:
        if item['status'] == 'NON_COMPLIANT':
            item_compliance = item['complianceType']
            device_id = item['deviceUuid']
            device_info = catalyst_center_api.devices.get_device_by_id(id=device_id)
            device_hostname = device_info['response']['hostname']
            compliance_report[item_compliance].append(device_hostname)

    logging.info(' Non-compliant devices report completed: ')

    logging.info(' ' + json.dumps(compliance_report, indent=4))

    # save report to JSON formatted file
    with open('compliance_report.json', 'w') as f:
        f.write(json.dumps(compliance_report, indent=4))
    logging.info(' Saved the non-compliant devices report to file "compliance_report.json"')

    # create report for non-compliant core devices for each compliance type
    compliance_report_core = {}
    for item in compliance_type:
        compliance_report_core.update({item: []})

    # loop through each item in compliance and append to report, to the specific category
    for item in network_compliance:
        if item['status'] == 'NON_COMPLIANT':
            item_compliance = item['complianceType']
            device_id = item['deviceUuid']
            device_info = catalyst_center_api.devices.get_device_by_id(id=device_id)
            device_hostname = device_info['response']['hostname']
            device_role = device_info['response']['role']
            if device_role == 'CORE':
                compliance_report_core[item_compliance].append(device_hostname)

    logging.info(' Non-compliant Core devices report completed: ')

    logging.info(' ' + json.dumps(compliance_report_core, indent=4))

    # save report to JSON formatted file
    with open('compliance_report_core.json', 'w') as f:
        f.write(json.dumps(compliance_report, indent=4))
    logging.info(' Saved the Core non-compliant devices report to file "compliance_report.json"')

    date_time = str(datetime.now().replace(microsecond=0))
    logging.info(' End of Application "catalyst_center_compliance.py" Run: ' + date_time)

    return


if __name__ == '__main__':
    main()
