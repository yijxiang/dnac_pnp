#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Site handler functions"""

# Import builtin python libraries
import json
import logging
import sys

# import external python libraries
import click
from yaml import load, dump
import yaml

# Import custom (local) python packages
from .api_call_handler import call_api_endpoint, get_response
from .api_endpoint_handler import generate_api_url
from .dnac_token_generator import generate_token
from .header_handler import get_headers
from .utils import divider, goodbye

# Source code meta data
__author__ = "Dalwar Hossain"
__email__ = "dalwar.hossain@dimensiondata.com"


# Generate site payload
def _generate_site_payload(site=None):
    """
    This private function generates site payload

    :param site: (dict) Single site config as python dict
    :returns: (dict) payload for api call
    """

    site_name = list(site.keys())[0]
    site_type = site[site_name]["type"]
    logging.debug(f"Site Name: {site_name}, Site Type: {site_type}")

    payload = {"type": site_type}
    if site_type == "floor":
        payload["site"] = {
            "area": {
                "name": site[site_name]["area_name"],
                "parentName": site[site_name]["area_parent"],
            },
            "building": {
                "name": site[site_name]["name"],
                "latitude": site[site_name]["latitude"],
                "longitude": site[site_name]["longitude"],
                "address": site[site_name]["address"],
            },
            "floor": {
                "name": site[site_name]["name"],
                "parentName": site[site_name]["parent"],
            },
        }
    elif site_type == "building":
        payload["site"] = {
            "area": {
                "name": site[site_name]["area_name"],
                "parentName": site[site_name]["area_parent"],
            },
            "building": {
                "name": site[site_name]["name"],
                "latitude": site[site_name]["latitude"],
                "longitude": site[site_name]["longitude"],
                "address": site[site_name]["address"],
            },
        }
    elif site_type == "area":
        payload["site"] = {
            "area": {
                "name": site[site_name]["name"],
                "parentName": site[site_name]["parent"],
            }
        }
    json_payload = json.dumps(payload, indent=4)
    return json_payload


# Read sites configuration
def _read_site_configs(file_to_read=None):
    """This private function reads sites configurations file"""

    try:
        with open(file_to_read, "r") as stream:
            configs = load(stream, Loader=yaml.FullLoader)
            return configs
    except Exception as err:
        click.secho(f"[x] Sites configuration read error!", fg="red")
        click.secho(f"[x] ERROR: {err}", fg="red")
        sys.exit(1)


# Site management
def add_site(dnac_auth_configs=None, locations_file_path=None):
    """
    This function adds site(s) to DNA center

    :param dnac_auth_configs: (dict) DNA Center authentication configurations
    :param locations_file_path: (str) Full file path to the sites configuration
    :returns: (stdOut) Output on screen
    """

    # Read site configurations
    logging.debug(f"Location File: {locations_file_path}")
    site_configs = _read_site_configs(file_to_read=locations_file_path)
    logging.debug(f"Site Configurations: {json.dumps(site_configs, indent=4)}")
    if "sites" in site_configs.keys():
        sites = site_configs["sites"]
    else:
        click.secho(f"[x] Site configuration file is malformed", fg="red")
        sys.exit(1)

    # Authentication token
    token = generate_token(configs=dnac_auth_configs)
    headers = get_headers(auth_token=token)
    method, api_url, parameters = generate_api_url(api_type="add-site")
    for item in sites:
        payload = _generate_site_payload(site=item)
        api_response = call_api_endpoint(
            method=method, api_url=api_url, data=payload, api_headers=headers
        )
        response_status, response_body = get_response(response=api_response)

        if response_status:
            print(response_body)
        else:
            print("------------------")
            print(response_body)