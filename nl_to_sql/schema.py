"""
Database schema definition for the assets table.
"""

# Assets table schema
ASSETS_TABLE = {
    "name": "assets",
    "columns": {
        # Basic identifiers
        "id": {"type": "VARCHAR(255)", "primary_key": True},
        "site": {"type": "VARCHAR(255)", "nullable": True},
        "resource": {"type": "VARCHAR(255)", "nullable": True},
        "timestamp": {"type": "TIMESTAMP", "nullable": True},
        "last_updated": {"type": "TIMESTAMP", "nullable": True},
        "name": {"type": "VARCHAR(255)", "nullable": True},
        "display_name": {"type": "VARCHAR(255)", "nullable": True},

        # Status flags
        "approved": {"type": "BOOLEAN", "nullable": True},
        "valid": {"type": "BOOLEAN", "nullable": True},
        "ghost": {"type": "BOOLEAN", "nullable": True},
        "parsed": {"type": "BOOLEAN", "nullable": True},
        "special_hint": {"type": "VARCHAR(255)", "nullable": True},
        "state": {"type": "VARCHAR(100)", "nullable": True},

        # Risk and criticality
        "risk": {"type": "VARCHAR(50)", "nullable": True},
        "criticality": {"type": "VARCHAR(50)", "nullable": True},

        # Time-based
        "last_entity_seen": {"type": "TIMESTAMP", "nullable": True},
        "last_seen": {"type": "TIMESTAMP", "nullable": True},
        "first_seen": {"type": "TIMESTAMP", "nullable": True},

        # Network identifiers
        "network": {"type": "VARCHAR(255)", "nullable": True},
        "subnet": {"type": "VARCHAR(255)", "nullable": True},
        "subnet_tag": {"type": "VARCHAR(255)", "nullable": True},
        "subnet_type": {"type": "VARCHAR(100)", "nullable": True},
        "virtual_zone": {"type": "VARCHAR(255)", "nullable": True},
        "ipv4": {"type": "VARCHAR(45)", "nullable": True},
        "ipv6": {"type": "VARCHAR(45)", "nullable": True},
        "mac": {"type": "VARCHAR(17)", "nullable": True},
        "vlan": {"type": "VARCHAR(50)", "nullable": True},
        "fdl": {"type": "VARCHAR(255)", "nullable": True},
        "address": {"type": "VARCHAR(255)", "nullable": True},
        "gateway": {"type": "VARCHAR(45)", "nullable": True},
        "default_gateway": {"type": "VARCHAR(45)", "nullable": True},
        "old_ip": {"type": "TEXT", "nullable": True},  # Can contain multiple IPs

        # Asset information
        "asset_type": {"type": "VARCHAR(100)", "nullable": True},
        "class_type": {"type": "VARCHAR(100)", "nullable": True},
        "hostname": {"type": "VARCHAR(255)", "nullable": True},
        "os": {"type": "VARCHAR(255)", "nullable": True},
        "os_build": {"type": "VARCHAR(100)", "nullable": True},
        "os_architecture": {"type": "VARCHAR(50)", "nullable": True},
        "os_service_pack": {"type": "VARCHAR(100)", "nullable": True},
        "model": {"type": "VARCHAR(255)", "nullable": True},
        "vendor": {"type": "VARCHAR(255)", "nullable": True},
        "plc_slots": {"type": "INTEGER", "nullable": True},
        "firmware": {"type": "VARCHAR(255)", "nullable": True},
        "project_parsed": {"type": "TEXT", "nullable": True},
        "serial_number": {"type": "VARCHAR(255)", "nullable": True},
        "domain_workgroup": {"type": "VARCHAR(255)", "nullable": True},

        # Edge and system info
        "edge": {"type": "VARCHAR(255)", "nullable": True},
        "edge_last_run": {"type": "TIMESTAMP", "nullable": True},
        "installed_antivirus": {"type": "VARCHAR(255)", "nullable": True},
        "has_interfaces": {"type": "BOOLEAN", "nullable": True},
        "installed_programs": {"type": "INTEGER", "nullable": True},
        "usb_devices": {"type": "INTEGER", "nullable": True},
        "asset_insight": {"type": "TEXT", "nullable": True},
        "insight_names": {"type": "TEXT", "nullable": True},

        # Queries and tasks
        "active_queries": {"type": "TEXT", "nullable": True},  # Can contain multiple query names
        "active_tasks": {"type": "TEXT", "nullable": True},  # Can contain multiple task names

        # Purdue and zones
        "purdue_level": {"type": "VARCHAR(50)", "nullable": True},

        # Custom attributes
        "custom_information": {"type": "TEXT", "nullable": True},  # JSON or serialized data
        "custom_attributes": {"type": "TEXT", "nullable": True},  # JSON or serialized data

        # Patch and code info
        "patch_count": {"type": "INTEGER", "nullable": True},
        "code_sections": {"type": "TEXT", "nullable": True},

        # Alerts and children
        "alerts": {"type": "INTEGER", "nullable": True},
        "children": {"type": "TEXT", "nullable": True},

        # Protocol
        "protocol": {"type": "VARCHAR(100)", "nullable": True},

        # Custom filters
        "CVE": {"type": "TEXT", "nullable": True},  # Can contain multiple CVEs
    }
}

# Column name mappings and synonyms
COLUMN_SYNONYMS = {
    # Basic identifiers
    "id": ["id", "asset_id"],
    "site": ["site", "location", "site_id"],
    "resource": ["resource", "resource_id"],
    "timestamp": ["timestamp", "time", "created"],
    "last_updated": ["last_updated", "updated", "modified"],
    "name": ["name", "asset_name"],
    "display_name": ["display_name", "display", "displayname"],

    # Status flags
    "approved": ["approved", "approve"],
    "valid": ["valid", "validated"],
    "ghost": ["ghost"],
    "parsed": ["parsed"],
    "special_hint": ["special_hint", "hint", "special"],
    "state": ["state", "status"],

    # Risk and criticality
    "risk": ["risk", "risk_level"],
    "criticality": ["criticality", "critical"],

    # Time-based
    "last_entity_seen": ["last_entity_seen", "entity_seen"],
    "last_seen": ["last_seen", "lastseen"],
    "first_seen": ["first_seen", "firstseen"],

    # Network identifiers
    "network": ["network", "net"],
    "subnet": ["subnet", "sub"],
    "subnet_tag": ["subnet_tag", "subnettag"],
    "subnet_type": ["subnet_type", "subnettype"],
    "virtual_zone": ["virtual_zone", "virtualzone", "zone"],
    "ipv4": ["ipv4", "ip", "ip_address", "ipaddress"],
    "ipv6": ["ipv6", "ip6"],
    "mac": ["mac", "mac_address", "macaddress"],
    "vlan": ["vlan"],
    "fdl": ["fdl"],
    "address": ["address", "addr"],
    "gateway": ["gateway", "gw"],
    "default_gateway": ["default_gateway", "defaultgateway"],
    "old_ip": ["old_ip", "oldip", "old_ips", "previous_ip", "previous_ips"],  # Multi-value field

    # Asset information
    "asset_type": ["asset_type", "type", "assettype"],
    "class_type": ["class_type", "class", "classtype"],
    "hostname": ["hostname", "host"],
    "os": ["os", "operating_system", "operatingsystem"],
    "os_build": ["os_build", "osbuild", "build"],
    "os_architecture": ["os_architecture", "osarchitecture", "architecture", "arch"],
    "os_service_pack": ["os_service_pack", "osservicepack", "service_pack"],
    "model": ["model"],
    "vendor": ["vendor", "manufacturer"],
    "plc_slots": ["plc_slots", "plcslots", "slots"],
    "firmware": ["firmware", "fw"],
    "project_parsed": ["project_parsed", "projectparsed", "project"],
    "serial_number": ["serial_number", "serialnumber", "serial"],
    "domain_workgroup": ["domain_workgroup", "domainworkgroup", "domain", "workgroup"],

    # Edge and system info
    "edge": ["edge"],
    "edge_last_run": ["edge_last_run", "edgelastrun"],
    "installed_antivirus": ["installed_antivirus", "installedantivirus", "antivirus", "av"],
    "has_interfaces": ["has_interfaces", "hasinterfaces", "interfaces"],
    "installed_programs": ["installed_programs", "installedprograms", "programs"],
    "usb_devices": ["usb_devices", "usbdevices", "usb"],
    "asset_insight": ["asset_insight", "assetinsight", "insight"],
    "insight_names": ["insight_names", "insightnames"],

    # Queries and tasks (multi-value fields)
    "active_queries": ["active_queries", "activequeries", "queries", "query"],
    "active_tasks": ["active_tasks", "activetasks", "tasks", "task"],

    # Purdue and zones
    "purdue_level": ["purdue_level", "purdue", "purdue_level"],

    # Custom attributes
    "custom_information": ["custom_information", "custominformation"],
    "custom_attributes": ["custom_attributes", "customattributes"],

    # Patch and code info
    "patch_count": ["patch_count", "patchcount", "patches"],
    "code_sections": ["code_sections", "codesections"],

    # Alerts and children
    "alerts": ["alerts", "alert"],
    "children": ["children", "child"],

    # Protocol
    "protocol": ["protocol", "proto"],

    # Custom filters (multi-value field)
    "CVE": ["cve", "vulnerability", "vulnerabilities", "vuln", "cves"],
}

# Get all valid column names
VALID_COLUMNS = list(ASSETS_TABLE["columns"].keys())

# Boolean columns
BOOLEAN_COLUMNS = [
    col for col, props in ASSETS_TABLE["columns"].items()
    if props["type"] == "BOOLEAN"
]

# Numeric columns
NUMERIC_COLUMNS = [
    col for col, props in ASSETS_TABLE["columns"].items()
    if props["type"] in ["BIGINT", "INTEGER", "INT"]
]

# String columns
STRING_COLUMNS = [
    col for col, props in ASSETS_TABLE["columns"].items()
    if "VARCHAR" in props["type"]
]

# Timestamp columns
TIMESTAMP_COLUMNS = [
    col for col, props in ASSETS_TABLE["columns"].items()
    if props["type"] == "TIMESTAMP"
]

# Multi-value columns (can contain multiple values)
MULTI_VALUE_COLUMNS = [
    "old_ip",           # Can contain multiple IPs
    "active_queries",   # Can contain multiple query names
    "active_tasks",     # Can contain multiple task names
    "CVE",              # Can contain multiple CVEs
]

# JSON/Serialized data columns
JSON_COLUMNS = [
    "custom_information",  # JSON or serialized data
    "custom_attributes",   # JSON or serialized data
]

# Text columns that may contain lists or structured data
TEXT_LIST_COLUMNS = [
    "old_ip",
    "active_queries",
    "active_tasks",
    "CVE",
    "children",
    "code_sections",
    "asset_insight",
    "insight_names",
    "project_parsed",
]

