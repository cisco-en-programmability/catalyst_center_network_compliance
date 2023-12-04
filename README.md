# Cisco DNA Center Network Compliance

This repo hosts files for few network compliance workflows:
 - catalyst_center_compliance.py - generate non-compliant devices report
 - network_settings_compliance.py - verify network settings configuration from Catalyst Center to match an intent from GitHub
 - device_config_compliance.py - identify which devices do not have specific CLI commands in the running configuration

**Cisco Products & Services:**

 - Cisco DNA Center, devices managed by Cisco DNA Center
 - Cisco DNA Center Python SDK

**Tools & Frameworks:**

- Python environment to run the application
- Optional: CI/CD platform if desired to automate the process

**Usage**

Output "catalyst_center_compliance.py"
```shell
INFO:root: Application "catalyst_center_compliance.py" Start, 2023-12-03 18:54:33
INFO:root: Collected Catalyst Center network compliance state
INFO:root: Type of compliance checks: [
    "EOX",
    "NETWORK_SETTINGS",
    "PSIRT",
    "IMAGE",
    "RUNNING_CONFIG",
    "APPLICATION_VISIBILITY",
    "NETWORK_PROFILE",
    "FABRIC"
]
INFO:root: Non-compliant devices report completed: 
INFO:root: {
    "EOX": [
        "LO-EDGE"
    ],
    "NETWORK_SETTINGS": [
        "PDX-M",
        "LO-CN",
        "LO-EDGE",
        "PDX-CORE1",
        "LO-BN"
    ],
    "PSIRT": [
        "PDX-RO",
        "PDX-STACK",
        "PDX-M",
        "NYC-RO",
        "SP",
        "PDX-RN",
        "LO-EDGE",
        "PDX-CORE1",
        "LO-BN",
        "C9800-CL"
    ],
    "IMAGE": [
        "LO-BN"
    ],
    "RUNNING_CONFIG": [
        "PDX-RO",
        "NYC-RO",
        "SP",
        "PDX-RN",
        "LO-CN"
    ],
    "APPLICATION_VISIBILITY": [],
    "NETWORK_PROFILE": [
        "NYC-ACCESS",
        "PDX-STACK",
        "PDX-M",
        "PDX-RN",
        "LO-CN",
        "LO-EDGE",
        "PDX-CORE1",
        "LO-BN"
    ],
    "FABRIC": []
}
INFO:root: Saved the non-compliant devices report to file "compliance_report.json"
INFO:root: Non-compliant Core devices report completed: 
INFO:root: {
    "EOX": [],
    "NETWORK_SETTINGS": [
        "PDX-CORE1"
    ],
    "PSIRT": [
        "PDX-CORE1"
    ],
    "IMAGE": [],
    "RUNNING_CONFIG": [],
    "APPLICATION_VISIBILITY": [],
    "NETWORK_PROFILE": [
        "PDX-CORE1"
    ],
    "FABRIC": []
}
INFO:root: Saved the Core non-compliant devices report to file "compliance_report.json"
INFO:root: End of Application "catalyst_center_compliance.py" Run: 2023-12-03 18:54:49
```

Output "network_settings_compliance.py"
```shell
INFO:root: Application "network_settings_compliance.py" Start, 2023-12-03 18:55:52
INFO:root: Repo "compliance_state" found!
INFO:root: File "intent_network_settings.yaml" found!
INFO:root: Intent network settings from GitHub:
INFO:root:   Site hierarchy: Global/OR/PDX
INFO:root:   Banner: This device is managed by Catalyst Center 10.93.141.45, version 2.3.7.3
INFO:root:   NTP server: 171.68.38.66
INFO:root:   DNS server: 171.70.168.183
INFO:root: The site id for the site: "Global/OR/PDX" is: 15628823-b52e-4564-a39c-36a9d45dc180
INFO:root: Collected the site settings
INFO:root: Network Settings compliance report:
INFO:root:   {
    "site_hierarchy": "Global/OR/PDX",
    "compliance_status": {
        "dns": "compliant",
        "ntp": "compliant",
        "banner": "not_compliant",
        "banner_intent": "This device is managed by Catalyst Center 10.93.141.45, version 2.3.7.3",
        "banner_configured": "This device is managed by Catalyst Center 10.93.141.45"
    }
}
INFO:root: Saved the network settings report to file "network_settings_report.json"
INFO:root: End of Application "network_settings_compliance.py" Run: 2023-12-03 18:55:58
```

Output "device_config_compliance.py'
```shell
INFO:root: Application "device_config_compliance.py" Start, 2023-12-03 18:57:04
INFO:root: Repo "compliance_state" found!
INFO:root: File "custom_network_compliance.yaml" found!
INFO:root: Device configs from GitHub:
INFO:root:   aaa_config: 
aaa new-model
aaa authentication login default local
aaa authorization exec default local 
aaa authorization network local

INFO:root:   ntp_config: 
ntp source Loopback1
ntp server 171.68.38.66
ntp server 171.68.48.78

INFO:root: Compliance device filter:
INFO:root:   device_role: ACCESS
INFO:root:   device_family: Cisco Catalyst 9300 Switch
INFO:root: Number of devices managed by Catalyst Center: 14
INFO:root: Collected the device list from Catalyst Center
INFO:root: Retrieved the device location and fabric role
INFO:root: Saved the device inventory to file "device_inventory.json"
INFO:root: Compliance checks for devices that match the device filter
INFO:root: Saved the device config LO-CN_config.txt
INFO:root: Device: LO-CN :
INFO:root:    - AAA config check failed, missing commands:
INFO:root:        - aaa authorization network local
INFO:root:    - NTP config check failed, missing commands:
INFO:root:        - ntp source Loopback1
INFO:root:        - ntp server 171.68.48.78
INFO:root: Saved the device config PDX-STACK_config.txt
INFO:root: Device: PDX-STACK :
INFO:root:    - AAA config check failed, missing commands:
INFO:root:        - aaa authorization network local
INFO:root:    - NTP config check failed, missing commands:
INFO:root:        - ntp server 171.68.48.78
INFO:root: End of Application "device_config_compliance.py" Run: 2023-12-03 18:57:26
```

**License**

This project is licensed to you under the terms of the [Cisco Sample Code License](./LICENSE).


