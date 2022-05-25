"""General utility and tools"""

import json
import logging
import os
import re
import sys
import sysconfig
import webbrowser
from pathlib import Path
from string import Template
from typing import Dict, List, Tuple, Union
from urllib.parse import urljoin, urlparse

import requests
import toml
import xmltodict
import yaml
from click import echo, style
from urllib3.util import parse_url

from yojenkins import __version__
from yojenkins.yo_jenkins.jenkins_item_classes import JenkinsItemClasses

logger = logging.getLogger()

CONFIG_DIR_NAME = ".yojenkins"


class TextStyle:
    """Text style definitions"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NORMAL = '\033[0m'


def print2(message: str, bold: bool = False, color: str = 'reset') -> None:
    """Print a message to the console using click

    Details:
        - Colors: `black` (might be a gray), `red`, `green`, `yellow` (might be an orange), `blue`,
          `magenta`, `cyan`, `white` (might be light gray), `reset` (reset the color code only)

    Args:
        message: Message to print to console
        bold   : Whether to bold the message
        color  : Color to use for the message ()
    """
    echo(style(message, fg=color, bold=bold))


def fail_out(message: str) -> None:
    """Output a failure message to the console, then exit

    Args:
        message: Message to output to console
    """
    echo(style(message, fg='bright_red', bold=True))
    sys.exit(1)


def failures_out(messages: list) -> None:
    """Output multiple failure messages to the console, then exit

    Args:
        message: Messages to output to console
    """
    for message in messages:
        echo(style(message, fg='bright_red', bold=True))
    sys.exit(1)


def load_contents_from_local_file(file_type: str, local_file_path: str) -> Dict:
    """Loading a local file contents

    ### TODO: Add default option to load file as plain text

    Parameters:
        file_type (str)       : Type of file to be loaded ie. 'yaml', 'toml', 'json'
        local_file_path (str) : Path to a local TOML file to be loaded
    Returns:
        file_contents (dict) : The contents of file
    """

    file_type = file_type.lower()

    # Check if file exists
    if not os.path.isfile(local_file_path):
        fail_out(f'Failed to find file: {local_file_path}')

    # Check if file is completely empty
    if os.stat(local_file_path).st_size == 0:
        return {}

    logger.debug(f"Loading specified local .{file_type} file: '{local_file_path}' ...")
    try:
        with open(local_file_path, 'r') as open_file:
            if file_type == 'yaml':
                file_contents = yaml.safe_load(open_file)
            elif file_type == 'toml':
                file_contents = toml.load(open_file)
            elif file_type == 'json':
                file_contents = json.loads(open_file.read())
            else:
                logger.debug(f"Unknown file type passed: '{file_type}'")
                raise ValueError(f"Unknown file type passed: '{file_type}'")
        logger.debug(f"Successfully loaded local .{file_type} file")
    except Exception as error:
        fail_out(f"Failed to load specified local .{file_type} file: '{local_file_path}'. Exception: {error}")
    return file_contents


def load_contents_from_remote_file_url(file_type: str, remote_file_url: str, allow_redirects: bool = True) -> Dict:
    """Loading a remote yaml file contents over HTTP

    ### FIXME: Make it able to load toml, json, and yaml file types

    Args:
        file_type (str)       : Type of file to be loaded ie. 'yaml', 'toml', 'json'
        remote_file_url (url)  : Remote URL location of file to be loaded
        allow_redirects (bool) : If True allow redirects to another URL (default True)
    Returns:
        file_contents (Dict) : The contents of the file
    """
    file_type = file_type.lower()

    # Getting name of file from URL
    remote_filename = Path(remote_file_url).name
    logger.debug(f'Requested remote filename parsed: {remote_filename}')

    # Check requested file extension
    remote_file_ext = Path(remote_file_url).suffix
    file_ext_accepted = ['.yml', '.yaml', '.conf']
    if not remote_file_ext in file_ext_accepted:
        logger.debug(
            f'Remote file requested "{remote_filename}"" is not one of the accepted file types: {file_ext_accepted}')
        return {}

    # Get request headers
    logger.debug(f'Getting remote file HTTP request headers for "{remote_file_url}" ...')
    try:
        return_content = requests.head(remote_file_url)
    except Exception as error:
        logger.debug(f'Failed to request headers. Exception: {error}')
        return {}
    header = return_content.headers

    # Check if file is below size limit
    content_length = int(header['Content-length']) / 1000000
    logger.debug(f'Requested file content length: {content_length:.5f} MB)')
    if content_length > 1.0:
        logger.debug(
            f'The requested remote file "{remote_filename}" is {content_length:.2f} MB and larger than 1.0 MB limit, will not download'
        )
        return {}

    # Check if content is text or yaml based
    content_types_accepted = ['text/plain', 'text/x-yaml', 'application/x-yaml', 'text/yaml', 'text/vnd.yaml']
    content_type = header.get('content-type')
    logger.debug(f'Request content type: {content_type}')
    if not content_type:
        return {}
    elif not any(ext in content_type for ext in content_types_accepted):
        logger.debug(
            f'The content type "{content_type}" of the requested file "{remote_filename}" is not one of the following: {content_types_accepted}'
        )
        return {}

    # Downloading the file content
    logger.debug(f"Requesting remote file: '{remote_file_url}' ...")
    remote_request = requests.get(remote_file_url, allow_redirects=allow_redirects)

    # Check if no error from downloading
    if remote_request.status_code == requests.codes.ok:
        # Loading the yaml file content
        logger.debug("Loading contents of remote file ...")
        try:
            file_contents = yaml.safe_load(remote_request.content)
        except Exception as error:
            logger.debug(f'Failed loading requested file. Exception: {error}')
            return {}
    else:
        logger.debug(
            f"Failed to get remote file '{remote_file_url}'. HTTP request error code {remote_request.status_code}")
        return {}

    return file_contents


def append_lines_to_file(filepath: str, lines_to_append: List[str], location: str = 'beginning') -> bool:
    """Add lines to the end to a text based file

    Details: The passed list is parsed and each list item is a separate line added
             to the beginning of the file

    Args:
        filepath        : Path to the file
        lines_to_append : List of strings, each item a line to append
        location        : Location of where to append lines, 'beginning' or 'end' (default 'beginning')

    Returns:
        True if successfully appended, else False
    """
    location = location.lower()

    # Check if file exists
    if not os.path.isfile(filepath):
        logger.debug(f'Failed to find file: {filepath}')
        return False

    logger.debug(f'Appending lines of text to the {location} of file: {filepath} ...')
    try:
        if location == 'beginning':
            open_file = open(filepath, 'r+')
            lines_old = open_file.readlines()  # read old content
            lines = lines_to_append + lines_old
            open_file.seek(0)
            for line in lines:
                open_file.write(line)
            open_file.close()
        elif location == 'end':
            open_file = open(filepath, 'a')
            for line in lines_to_append:
                open_file.write(line)
            open_file.close()
        else:
            logger.debug(f'Unsupported append file location: {location}')
            return False
    except Exception as error:
        logger.error(f'Failed to append lines of text to the end of file ({filepath}). Exception: {error}')
        return False
    return True


def is_list_items_in_dict(list_items: list, dict_to_check: dict) -> int:
    """Return index of ANY matched item in the passed list

    Args:
        list_items    : List of items to find in dict_to_check
        dict_to_check : Dict to match the top level keys to

    Returns:
        Index of any/first matched item in the list to the top level keys of the dict
    """
    for key in dict_to_check:  # Looping top level dict keys
        if key in list_items:  # Check if the key is in one of the list items
            return list_items.index(key)
    return None


def iter_data_empty_item_stripper(iter_data):
    """Removes any empty data from a nested or un-nested iter item

    Details: https://stackoverflow.com/a/27974027/11294572

    Args:
        iter_data : data in the from of iterable (ie. list, dict, set, etc)

    Returns:
        Iterable item without any blank/empty items
    """
    empties = ((), {}, set(), None)

    if isinstance(iter_data, dict):
        return {
            key: value
            for key, value in ((key, iter_data_empty_item_stripper(value)) for key, value in iter_data.items())
            if value not in empties
        }
    if isinstance(iter_data, list):
        return [value for value in map(iter_data_empty_item_stripper, iter_data) if value not in empties]
    return iter_data


def is_credential_id_format(text: str) -> bool:
    """Checking if the entire text is in Jenkins credential ID format

    Args:
        text: The text to check

    Returns:
        True if the text is in credential ID format, else False
    """
    regex_pattern = r'^[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}$'
    cred_match = re.match(regex_pattern, text)
    if cred_match:
        logger.debug(f'Successfully identified credential ID format')
    else:
        logger.debug(f'Failed to identify credential ID format')
    return cred_match


def is_full_url(url: str) -> bool:
    """TODO Docstring

    Args:
        TODO

    Returns:
        TODO
    """

    # TODO: Replace this same function in cli_utility.py usages with this one within classes

    parsed_url = parse_url(url)
    if all([parsed_url.scheme, parsed_url.netloc, parsed_url.path]):
        is_valid_url = True
    else:
        is_valid_url = False
    logger.debug(f'Is valid URL format: {is_valid_url} - {url}')
    logger.debug(f'    - scheme:  {parsed_url.scheme} - {"OK" if parsed_url.scheme else "MISSING"}')
    logger.debug(f'    - netloc:  {parsed_url.netloc} - {"OK" if parsed_url.netloc else "MISSING"}')
    logger.debug(f'    - path:    {parsed_url.path} - {"OK" if parsed_url.path else "MISSING"}')

    return is_valid_url


def url_to_name(url: str) -> str:
    """Convert the jenkins item URL to its name

    Args:
        url : URL of the item (ie. folder, job, build)

    Returns:
        The full name of the item
    """
    # Split url into base componenets
    url_components = urlparse(url)

    # Split and filter out terms
    # name = url_components.path.strip('/').replace('/job/', '/').strip().strip('/').strip('job/').replace('view/', '').replace('change-requests/', '')
    url_split = url_components.path.strip().strip('/').split('/')
    remove_list = ['job', 'view', 'change-requests']

    filtered_list = []
    for list_item in url_split:  # TODO: Use list comprehension
        if list_item not in remove_list:
            filtered_list.append(list_item)

    # Assemble back
    name = '/'.join(filtered_list)

    logger.debug(f'Converted URL "{url}" to fullname "{name}"')
    return name


def format_name(name: str) -> str:
    """Format / clean up the passed name

    Details: The formatting includes it:
        - /Non-PAR/job/Non-Prod-Jobs/job/Something/job/job --> /Non-PAR/Non-Prod-Jobs/Something/job
        - remove `job/`, `view/`, `change-requests/`
        - remove leading or trailing `/`

    Args:
        name : The name of the item

    Returns:
        Formatted item name
    """
    # Filter out terms
    name_formatted = name.strip().replace('/job/', '/').strip('/')
    name_formatted = name_formatted.replace('job/', '/').strip('/').replace('view/',
                                                                            '').replace('change-requests/', '')

    logger.debug(f'Formatted "{name}" to "{name_formatted}"')
    return name_formatted


def fullname_to_name(fullname: str) -> str:
    """Convert the jenkins item full name to its name only

    Details: Hey/This/Is/A/Full/Job --> Job

    Args:
        url : Full name of the item (ie. Hey/This/Is/A/Full/Job)

    Returns:
        The name of the item
    """
    name = fullname.strip().strip('/').split('/')[-1]
    logger.debug(f'Converted fullname "{fullname}" to name "{name}"')
    return name


def name_to_url(server_base_url: str, name: str) -> str:
    """Convert the item name to URL

    ** TODO **

    NOTE: Passed '.' will go to base url

    Args:
        name : The name of the item

    Returns:
        Item URL
    """
    # FIXME: Fix this workaround
    cut_off = 1 if name == '.' else 0

    a_path = name.strip('/').split('/')
    if len(a_path) > cut_off:
        short_name = 'job/' + '/job/'.join(a_path)
    else:
        short_name = ''
    # short_name = (('job/' + '/job/'.join(a_path[:-1]) + '/') if len(a_path) > 1 else '')
    url = str(urljoin(server_base_url, short_name))
    logger.debug(f'Converted name "{name}" to URL "{url}"')

    return url


def build_url_to_other_url(build_url: str, target_url: str = 'job') -> str:
    """From build_url get job or folder url

    Args:
        build_url  : The URL of the build
        target_url : URL to derive. `job` or `folder` (default: `job`)

    Returns:
        The URL of the job or folder
    """
    # Dissect the build url
    url_parsed = urlparse(build_url)
    path_list = url_parsed.path.split('/')

    # Get the indexes to remove
    if target_url == 'job':
        last_index = -2 if not path_list[-1] else -1
    elif target_url == 'folder':
        last_index = -4 if not path_list[-1] else -3
    else:
        logger.debug(f'Failed to recognize passed target URL. Passed value: {target_url}')
        return ''

    # Join the new path
    path_new = '/'.join(path_list[0:last_index])

    # Assemble the job url
    base_url = url_parsed.scheme + '://' + url_parsed.netloc

    result_url = urljoin(base_url, path_new) + '/'
    logger.debug(f'From build URL "{build_url}" extracted {target_url} URL "{result_url}"')

    return result_url


def build_url_to_build_number(build_url: str) -> int:
    """Get the build number from its build URL

    Args:
        build_url : The URL of the build

    Returns:
        The build number
    """
    logger.debug(f'Extracting build number from URL: {build_url} ...')
    # Dissect the build url
    url_parsed = urlparse(build_url)

    # Split the path, remove the empty items
    url_path_split_list = list(filter(None, url_parsed.path.split('/')))

    # Get the last item, convert to int
    build_number = int(url_path_split_list[-1])

    logger.debug(f'From build URL "{build_url}" extracted build number "{build_number}"')
    return build_number


def item_url_to_server_url(url: str, include_scheme: bool = True) -> str:
    """From build_url get job or folder url

    Args:
        url            : The URL of the build
        include_scheme : If True, include protocol scheme (ie. `https://`) (default: `True`)

    Returns:
        The URL of the server
    """
    url_parsed = urlparse(url)
    if include_scheme:
        server_url = url_parsed.scheme + '://' + url_parsed.netloc
    else:
        server_url = url_parsed.netloc
    return server_url


def has_build_number_started(job_info: dict, build_number: int) -> bool:
    """Given the job info, check if build number has been started/run

    Args:
        job_info     : The job information
        build_number : The build number to be looked up

    Returns:
        True if build number has starated, else false
    """
    if 'builds' not in job_info:
        return False
    for build in job_info['builds']:
        if not 'number' in build:
            continue
        if build['number'] == build_number:
            logger.debug(f'Successfully found tha build {build_number} was previously started')
            return True
    logger.debug(f'Failed to find build {build_number} was previously started')
    return False


def item_subitem_list(item_info: Dict,
                      get_key_info: str,
                      item_type: str,
                      item_class_list: list = [],
                      item_class_key: str = '_class') -> Tuple[list, list]:
    """Given a item (job, build, etc) info, get the sub-items matching criteria

    Details: <DETAILED DESCRIPTION>

    Args:
        item_info       : Info dict of the item
        get_key_info    : The key value to get (ie. `url`, `name`)
        item_type       : Class type of sub-item to be matched (ie. `com.cloudbees.hudson.plugins.folder.Folder`) - See `JenkinsItemClasses.py`
        item_class_list : List of classes to be matched (ie. `jobs`, `views`) - See `JenkinsItemClasses.py`
        item_class_key  : The key in the item info to match (ie. `_class`)

    Returns:
        List of the matched item dict and a list of the item names
    """
    # Find subitem info in dict item
    item_list = []
    item_name_list = []
    if item_type in item_info:

        # Loop subsection (ie. jobs, views, etc)
        for subitem_info in item_info[item_type]:

            # Check if subitem has the looked after class
            if subitem_info[item_class_key] in item_class_list:
                item_list.append(subitem_info)
                item_name_list.append(subitem_info[get_key_info])
    else:
        return [], []

    return item_list, item_name_list


def to_seconds(time_quantity: int, time_unit_text: str) -> int:
    """
    Get the number of seconds from the time quantity and time unit type.
    Examples:
        - 45 min -> 2700 seconds
        - 2 days -> 432000 seconds

    Parameters:
        time_quantity (int)  : Number of time units
        time_unit_text (str) : Type of time units (ie. seconds, minutes, hours, etc)
    Returns:
        seconds (int) : Number of seconds
    """
    if not time_quantity:
        return 0

    if time_unit_text in ["s", "sec", "second", "seconds"]:
        return time_quantity

    if time_unit_text in ["m", "min", "minute", "minutes"]:
        return time_quantity * 60

    if time_unit_text in ["h", "hr", "hour", "hours"]:
        return time_quantity * 60 * 60

    if time_unit_text in ["d", "day", "days"]:
        return time_quantity * 60 * 60 * 60

    if time_unit_text in ["blue moon"]:
        blue_moon = 41  # months
        return int(time_quantity * blue_moon * 2.628e+6)

    return 0


def html_clean(html: str) -> str:
    """Clean up HTML format to text without HTML tags

    Args:
        html : HTML content

    Returns:
        Cleaned text
    """
    # Remove all HTML tags
    cleaned_text = re.sub(re.compile('<.*?>'), '', html)

    # Convert symbols back
    cleaned_text = cleaned_text.replace("&lt;", "<")
    cleaned_text = cleaned_text.replace("&gt;", ">")
    cleaned_text = cleaned_text.replace("&quot;", '"')
    cleaned_text = cleaned_text.replace("&apos;", "'")
    cleaned_text = cleaned_text.replace('&nbsp;', '')
    cleaned_text = cleaned_text.replace("&amp;", "&")  # This has to be last

    return cleaned_text


def browser_open(url: str, new: int = 2, autoraise: bool = True) -> bool:
    """Clean up HTML format to text without HTML tags

    Args:
        url       : Weblink URL
        new       : 0=Same browser window, 1=New browser window, 2=New Tab
        autoraise : True=Window is raised

    Returns:
        True if successfull, else False
    """
    try:
        webbrowser.open(url.strip('/'), new, autoraise)
    except Exception as error:
        logger.debug(f'Failed to open web browser for URL: {url.strip("/")}  Exception: {error}')
        return False
    return True


def has_special_char(text: str, special_chars: str = '@!#$%^&*<>?/\|~:') -> bool:
    """Check if passed text string contains any special characters

    Args:
        text          : Text to check
        special_chars : String with all special characters to check

    Returns:
        True if includes special characters, else False
    """
    regex = re.compile('[' + special_chars + ']')
    includes_special_chars = regex.search(text) != None
    if includes_special_chars:
        logger.debug(f'Item "{text}" includes special characters. Special characters: {special_chars}')
    else:
        logger.debug(f'Item "{text}" does not include special characters. Special characters: {special_chars}')
    return includes_special_chars


def remove_special_char(text: str, special_chars: str = '@!#$%^&*<>?/\|~:') -> str:
    """Remove any special characters from text string

    Args:
        text          : Text to remove special characters from
        special_chars : String with all special characters to remove

    Returns:
        Text with special characters removed
    """
    regex = re.compile('[' + special_chars + ']')
    text_new = re.sub(regex, '', text)
    logger.debug(f'Removed special characters "{special_chars}" from string')
    return text_new


def queue_find(all_queue_info: dict, job_name: str = '', job_url: str = '', first: bool = True) -> list:
    """Finding job in server build queue

    Args:
        TODO

    Returns:
        TODO
    """
    if not job_name and not job_url:
        logger.debug('=No job name or job URL provided')
        return []
    job_name = job_name if job_name else url_to_name(job_url)

    queue_item_matches = []

    for i, queue_item in enumerate(all_queue_info['items']):
        # Check the item type
        if queue_item['task']['_class'] not in JenkinsItemClasses.JOB.value['class_type']:
            logger.debug(
                f"[ITEM {i+1}/{len(all_queue_info['items'])}] Queued item not a job. Item class: {queue_item['task']['_class']}"
            )
            continue

        queue_job_url = queue_item['task']['url']
        logger.debug(f"[ITEM {i+1}/{len(all_queue_info['items'])}] Queue job item: {queue_job_url}")

        queue_job_name = url_to_name(url=queue_job_url)

        # Check for name match
        if queue_job_name == job_name:
            logger.debug(f'Successfully found job in server build queue: "{job_name}"')
            queue_item_matches.append(queue_item)
            if first:
                break

    if not queue_item_matches:
        logger.debug('Failed to find job in build queue')

    return queue_item_matches


def get_resource_path(relative_path: str) -> str:
    """Getting the filepath for existing included resource

    Args:
        relative_path : Relative path within the project directory

    Details:
        - `get_resource_path(os.path.join('resources', 'server_docker_settings', 'last_deploy_info.json'))`
        - `get_resource_path(os.path.join('resources', 'scripts', 'some_script.sh'))`

    Returns:
        Included resource path
    """
    # Get the path in python site packages
    resource_dir = get_project_dir()
    resource_path = os.path.abspath(os.path.join(resource_dir, relative_path))

    # If the file has not been found and it is on windows, try APPDATA directory
    if not os.path.exists(resource_path):
        logger.debug(f'Failed to find resource "{relative_path}" in: {resource_dir}')
        return ''
    logger.debug(f'Successfully found existing resource: {resource_path}')
    return resource_path


def get_project_dir(sample_path: str = 'resources') -> str:
    """Getting the path to the directory containing project resources

    Details:
        - Effectively this function is looking through all possible package locations
        and checking if it contains a directory with the project name

    Args:
        sample_path : A directory that is directly inside the project directory (ie. yojenkins/resources)

    Returns:
        Project directory absolute path
    """
    if am_i_bundled():
        # Program is running within a pyinstaller bundle
        project_dir = ''
        possible_dirs = {
            'pyinstaller': sys._MEIPASS,
        }
    else:
        project_dir = 'yojenkins'
        possible_dirs = {
            'relative': os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
            'sys_dirs': sysconfig.get_paths()["purelib"],
            'cwd': os.getcwd(),
        }
        # NOTE: "site" module does not work with pyinstaller bundle (AttributeError)
        # 'usr_dirs': site.getusersitepackages(),
        # 'site_dirs': site.getsitepackages(),

    dirs = []
    for possible_dir in possible_dirs.values():
        if isinstance(possible_dir, list):
            dirs.extend(possible_dir)
        else:
            dirs.append(possible_dir)

    logger.debug('Searching project resource directory ...')
    resource_dir_path = ''
    for possible_dir in dirs:
        if os.path.exists(os.path.join(possible_dir, project_dir, sample_path)):
            resource_dir_path = os.path.join(possible_dir, project_dir)
            logger.debug(f'    - {possible_dir} - FOUND')
            break
        logger.debug(f'    - {possible_dir} - NOT FOUND')

    if not resource_dir_path:
        logger.fatal('Failed to find included data directory')
        return ''
    return resource_dir_path


def item_exists_in_folder(item_name: str, folder_url: str, item_type: str, rest: object) -> bool:
    """Checking if the item exists within the specified folder on server

    Args:
        item_name : Name of the item to check
        folder_url : URL of the folder to check
        item_type : Type of the item to check
        rest: Rest object

    Returns:
        True if the item exists, False if not
    """
    item_type_info = getattr(JenkinsItemClasses, item_type.upper())
    prefix = item_type_info.value['prefix']

    item_url = urljoin(folder_url, f'{prefix}/{item_name}')

    logger.debug(f'Checking if {item_type} "{item_name}" already exists within folder "{folder_url}" ...')
    item_exists = rest.request(f'{item_url.strip("/")}/api/json', 'head', is_endpoint=False)[2]
    if item_exists:
        logger.debug(f'Found existing {item_type} "{item_name}" within "{folder_url}"')
        return True
    else:
        logger.debug(f'Did not found {item_type} "{item_name}" within "{folder_url}"')

    return item_exists


def am_i_inside_docker() -> bool:
    """Find out if the program is running inside a docker container

    Returns:
        True if running in docker container, else False
    """
    path = '/proc/self/cgroup'
    return (os.path.exists('/.dockerenv') or os.path.isfile(path) and any('docker' in line for line in open(path)))


def am_i_bundled() -> bool:
    """Find out if the program is running as part of a pyinstaller bundle

    Returns:
        True if running bundled, else False
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def parse_and_check_input_string_list(string_list: str, join_back_char: str = '', split_char: str = ',') -> list:
    """Parsing a string list into a list of strings

    Details:
        - `parse_string_list('a,b,c')` => ['a', 'b', 'c']
        - `parse_string_list('a,b,c', join_back_char=';')` => ['a;b;c']

    Args:
        string_list : String list to be parsed
        split_char : Character to split the string list on
        join_back_char : Character to join the list items

    Returns:
        String with items seperated by commas
    """
    parsed_items = []
    for label in string_list.split(split_char):
        label = label.strip()
        if has_special_char(label):
            return []
        parsed_items.append(label)

    if join_back_char:
        parsed_items = join_back_char.join(parsed_items)

    logger.debug(f'Parsed and checked string list: "{string_list}" => "{parsed_items}"')

    return parsed_items


def write_xml_to_file(xml_content: str,
                      filepath: str,
                      opt_json: bool = False,
                      opt_yaml: bool = False,
                      opt_toml: bool = False) -> bool:
    """Writing XML content file in specified format

    Args:
        xml_content : XML content to be written
        filepath : Filepath to write the content to
        opt_json : Write the content as JSON
        opt_yaml : Write the content as YAML
        opt_toml : Write the content as TOML

    Returns:
        True if successful
    """
    if any([opt_json, opt_yaml, opt_toml]):
        logger.debug('Converting content to JSON ...')
        data_ordered_dict = xmltodict.parse(xml_content)
        content_to_write = json.loads(json.dumps(data_ordered_dict))
    else:
        content_to_write = xml_content  # Keep XML format

    if opt_json:
        content_to_write = json.dumps(data_ordered_dict, indent=4)
    elif opt_yaml:
        logger.debug('Converting content to YAML ...')
        content_to_write = yaml.dump(content_to_write)
    elif opt_toml:
        logger.debug('Converting content to TOML ...')
        content_to_write = toml.dumps(content_to_write)

    logger.debug(f'Writing fetched configuration to "{filepath}" ...')
    try:
        with open(filepath, 'w+') as file:
            file.write(content_to_write)
        logger.debug('Successfully wrote configurations to file')
    except Exception as error:
        logger.debug('Failed to write configurations to file. Exception: {error}')
        return False

    return True


def template_apply(string_template: str, is_json: bool = False, **kwargs) -> Union[str, dict]:
    """Apply/Fill variables into a string template.
    Placeholder variables must be in the `${variable_name}` format.

    Details:
        - Example of a string template:
            `'{
                "credentials": {
                    "scope": "${domain}",
                    "username": "${username}"
                }'`

    Args:
        string_template: A string template with placeholders (ie. `${variable}`)
        is_json: If true, the string template is a json string
        kwargs: dictionary of variables to be applied

    Returns:
        String template with variables applied
    """
    logger.debug('Applying variables to string template ...')
    logger.debug(f'Applied variables: {", ".join(list(kwargs.keys()))}')
    # Replace None with empty string
    for key, value in kwargs.items():
        if value is None:
            kwargs[key] = ''

    template = Template(string_template)
    try:
        template_filled = template.safe_substitute(**kwargs)
    except Exception as error:
        logger.debug(f'Failed to apply variables to string template. Exception: {error}')
        return ''
    if is_json:
        try:
            template_filled = json.loads(template_filled)
        except json.JSONDecodeError:
            logger.debug('Failed to parse filled string template as JSON')
            return ''
    logger.debug('Successfully applied variables to string template')
    return template_filled


def run_groovy_script(script_filepath: str, json_return: bool, rest: object,
                      **kwargs) -> Tuple[Union[dict, str], bool, str]:
    """Run a Groovy script on the server and return the response

    Details:
        A failed Groovy script execution will return a list/array in the following format:
        `['yojenkins groovy script failed', '<GROOVY EXCEPTION>', '<CUSTOM ERROR MESSAGE>']`

    Args:
        script_directory: Directory where the script is located
        script_filepath: The path to the Groovy script to run
        json_return: Anticipate and format script return as JSON
        rest: Rest object
        kwargs (dict): Any variables to be inserted into the script text

    Returns:
        Response from the script
        Success flag
        Error message
    """
    logger.debug(f'Loading Groovy script: {script_filepath}')
    try:
        with open(script_filepath, 'r') as open_file:
            script = open_file.read()
    except (FileNotFoundError, IOError, PermissionError) as error:
        logger.debug(f'Failed to find or read specified Groovy script file ({script_filepath}). Exception: {error}')
        return {}, False, f'Failed to find or read specified Groovy script file ({script_filepath}). Exception: {error}'

    # Apply passed kwargs to the string template
    if kwargs:
        script = template_apply(string_template=script, is_json=False, **kwargs)
        if not script:
            return {}, False, "Failed to apply variables to Groovy script template"

    # Send the request to the server
    logger.debug(f'Running the following Groovy script on server: {script_filepath} ...')
    script_result, _, success = rest.request(target='scriptText',
                                             request_type='post',
                                             data={'script': script},
                                             json_content=False)
    if not success:
        logger.debug('Failed server REST request for Groovy script execution')
        return {}, False, 'Failed server REST request for Groovy script execution'

    # Check for yojenkins Groovy script error flag
    if "yojenkins groovy script failed" in script_result:
        groovy_return = eval(script_result.strip(os.linesep))
        logger.debug('Failed to execute Groovy script')
        logger.debug(f'Groovy Exception: {groovy_return[1]}')
        logger.debug(groovy_return[2])
        return {}, False, f'Error while executing Groovy script: {groovy_return[1]}: {groovy_return[2]}'

    # Check for script exception
    exception_keywords = ['Exception', 'java:']
    if any(exception_keyword in script_result for exception_keyword in exception_keywords):
        logger.debug(f'Error keyword matched in script response: {exception_keywords}')
        return {}, False, f'Error keyword matched in script response: {exception_keywords}'

    # Parse script result as JSON
    if json_return:
        try:
            script_result = json.loads(script_result)
        except json.JSONDecodeError as error:
            logger.debug('Failed to parse response to JSON format')
            return {}, False, 'Failed to parse response to JSON format'

    return script_result, True, ''


def get_item_action(item_info: dict, class_type: str) -> List[dict]:
    """Get the item's actions for a specific action class type

    Args:
        item_info: The item info dictionary (ie. job info, build info, etc.)
        class_type: The class type of the item

    Returns:
        List of matched actions for the item
    """
    logger.debug(f'Getting actions for item coresponding to class type "{class_type}" ...')
    actions_info = []
    for action in item_info['actions']:
        if action:
            if action['_class'] == class_type:
                actions_info.append(action)

    return actions_info


def create_new_history_file(file_path: str) -> None:
    """Create a new blank command history file.

    Args:
        file_path: Full path to the history file

    Returns:
        None
    """
    try:
        # Creating configuration directory if it does not exist
        config_dir_abs_path = os.path.join(Path.home(), CONFIG_DIR_NAME)

        if not os.path.exists(config_dir_abs_path):
            logger.debug("Configuration directory does not exist. Creating it ...")
            os.makedirs(config_dir_abs_path)

        if not os.path.exists(file_path):
            logger.debug(f'Command history file NOT found: "{file_path}"')
            logger.debug("Creating a new command history file ...")
        with open(file_path, "w") as open_file:
            json.dump({}, open_file)

    except (FileNotFoundError, IOError, PermissionError) as error:
        fail_out(f'Failed to create history file ({file_path}). Exception: {error}')
    except Exception as error:
        logger.exception(f"Failed to create new command history file. Exception: {error}")
