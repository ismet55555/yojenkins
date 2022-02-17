"""Credential Menu CLI Entrypoints"""

import json
import logging
import sys

import click
import xmltodict

from yojenkins.cli import cli_utility as cu
from yojenkins.cli.cli_utility import log_to_history

# Getting the logger reference
logger = logging.getLogger()


@log_to_history
def list(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_list: bool, profile: str, folder: str,
         domain: str, keys: str) -> None:
    """List credentials

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        profile: The profile/account to use
        folder: The folder to use for the credential
        domain: The domain to use for the credential
        keys: Credential keys to list

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data, data_list = yj_obj.credential.list(folder=folder, domain=domain, keys=keys)
    data = data_list if opt_list else data
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def info(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, profile: str, credential: str, folder: str,
         domain: str) -> None:
    """Credential information

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        profile: The profile/account to use
        folder: The folder to use for the credential
        domain: The domain to use for the credential

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.info(credential=credential, folder=folder, domain=domain)
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def config(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str,
           credential: str, folder: str, domain: str, filepath: str) -> None:
    """Get credential configuration

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        profile: The profile/account to use
        folder: The folder to use for the credential
        domain: The domain to use for the credential
        filepath: The filepath of the credential configuration

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.config(credential=credential,
                                    folder=folder,
                                    domain=domain,
                                    opt_json=opt_json,
                                    opt_yaml=opt_yaml,
                                    opt_toml=opt_toml,
                                    filepath=filepath)
    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def get_template(opt_pretty: bool, opt_yaml: bool, opt_xml: bool, opt_toml: bool, opt_json: bool, profile: str,
                 cred_type: str, filepath: str) -> None:
    """Credential type template to create a credential

    Args:
        opt_pretty: Option to pretty print the output
        opt_yaml: Option to output in YAML format
        opt_xml: Option to output in XML format
        opt_toml: Option to output in TOML format
        profile: The profile/account to use
        cred_type: The credential type to get the template for
        filepath: The filepath to save the credential configuration

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.get_template(cred_type=cred_type,
                                          opt_json=opt_json,
                                          opt_yaml=opt_yaml,
                                          opt_toml=opt_toml,
                                          filepath=filepath)
    opt_xml = not any([opt_json, opt_yaml, opt_toml])
    data = data if opt_xml else json.loads(json.dumps(xmltodict.parse(data)))
    cu.standard_out(data, opt_pretty, opt_yaml, opt_xml, opt_toml)


@log_to_history
def create(profile: str, config_file: str, folder: str, domain: str) -> None:
    """Create new credentials

    Args:
        profile: The profile/account to use
        config_file: The filepath of the credential configuration
        folder: The folder to use for the credential
        domain: The domain to use for the credential

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.create(config_file=config_file, folder=folder, domain=domain)
    click.secho('success', fg='bright_green', bold=True)


@log_to_history
def delete(profile: str, credential: str, folder: str, domain: str) -> None:
    """Remove credentials

    Args:
        profile: The profile/account to use
        credential: The credential ID or URL to delete
        folder: The folder of the credential
        domain: The domain of the credential

    Returns:
        None
    """
    yj_obj = cu.config_yo_jenkins(profile)
    data = yj_obj.credential.delete(credential=credential, folder=folder, domain=domain)
    click.secho('success', fg='bright_green', bold=True)
