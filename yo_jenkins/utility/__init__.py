#!/usr/bin/env python3

import logging
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import urlparse, urljoin
import re
import webbrowser

import requests
import yaml


logger = logging.getLogger()


def load_contents_from_local_yaml_file(local_file_path:str) -> Dict:
    """Loading a local file contents

    Parameters:
        local_file_path (str) : Path to a local file to be loaded
    Returns: 
        file_contents (dict) : The contents of the file
    """

    logger.debug(f"Loading specified local config file: '{local_file_path}' ...")
    try:
        with open(local_file_path, 'r') as file:
            file_contents = yaml.safe_load(file)
        logger.debug("Successfully loaded local config file")
    except Exception as e:
        # TODO: Make Exception more specific
        logger.debug(f"Failed to load specified local config file: '{local_file_path}'. Exception: {e}")
        return {}
    return file_contents


def load_contents_from_remote_yaml_file_url(remote_file_url:str, allow_redirects:bool=True) -> Dict:
    """Loading a remote yaml file contents over HTTP

    Args:
        remote_file_url (url)  : Remote URL location of file to be loaded
        allow_redirects (bool) : If True allow redirects to another URL (default True)
    Returns: 
        file_contents (Dict) : The contents of the file
    """
    # Getting name of file from URL
    remote_filename = Path(remote_file_url).name
    logger.debug(f'Requested remote filename parsed: {remote_filename}')

    # Check requested file extension
    remote_file_ext = Path(remote_file_url).suffix
    file_ext_accepted = ['.yml', '.yaml', '.conf']
    if not remote_file_ext in file_ext_accepted:
        logger.debug(f'Remote file requested "{remote_filename}"" is not one of the accepted file types: {file_ext_accepted}')
        return {}

    # Get request headers
    logger.debug(f'Getting remote file HTTP request headers for "{remote_file_url}" ...')
    try:
        h = requests.head(remote_file_url)
    except Exception as e:
        logger.debug(f'Failed to request headers. Exception: {e}')
        return {}
    header = h.headers

    # Check if file is below size limit
    content_length = int(header['Content-length']) / 1000000
    logger.debug(f'Requested file content length: {content_length:.5f} MB)')
    if content_length > 1.0:
        logger.debug(f'The requested remote file "{remote_filename}" is {content_length:.2f} MB and larger than 1.0 MB limit, will not download')
        return {}

    # Check if content is text or yaml based
    content_types_accepted = ['text/plain', 'text/x-yaml', 'application/x-yaml', 'text/yaml', 'text/vnd.yaml']
    content_type = header.get('content-type')
    logger.debug(f'Request content type: {content_type}')
    if not content_type:
        return {}
    elif not any(ext in content_type for ext in content_types_accepted):
        logger.debug(f'The content type "{content_type}" of the requested file "{remote_filename}" is not one of the following: {content_types_accepted}')
        return {}

    # Downloading the file content
    logger.debug(f"Requesting remote file: '{remote_file_url}' ...")
    remote_request = requests.get(remote_file_url, allow_redirects=allow_redirects)

    # Check if no error from downloading
    if remote_request.status_code == requests.codes.ok:
        # Loading the yaml file content
        logger.debug("Loading contents of remote file ...")
        try:
            # open(os.path.join(local_dir, remote_filename), 'wb').write(remote_request.content)
            file_contents = yaml.safe_load(remote_request.content)
        except Exception as e:
            logger.debug(f'Failed loading requested file. Exception: {e}')
            return {}
    else:
        logger.debug(f"Failed to get remote file '{remote_file_url}'. HTTP request error code {remote_request.status_code}")
        return {}

    return file_contents


def uri_validator(uri:str) -> bool:
    """Check the passed URI/URL format

    Details: Validating the passed URL to see if it fits the typical URL format

    Args:
        uri : URI/URL

    Returns:
        True if valid format, else False
    """
    try:
        result = urlparse(uri)
        is_valid_uri = all([result.scheme, result.netloc, result.path])
    except:
        is_valid_uri = False
    return is_valid_uri


def append_lines_to_beginning_of_file(filepath:str, lines_to_append:List[str]) -> bool:
    """Add lines to the beginning to a text based file

    Details: The passed list is parsed and each list item is a separate line added
             to the beginning of the file

    Args:
        filepath        : Path to the file
        lines_to_append : List of strings, each item a line to append

    Returns:
        True if successfully appended, else False
    """
    # TODO: Check if file exists
    logger.debug(f'Appending lines of text to the beginning of file: {filepath} ...')
    try:
        f = open(filepath,'r+')
        lines_old = f.readlines() # read old content
        lines = lines_to_append + lines_old
        f.seek(0)
        for line in lines:
            f.write(line)
        f.close()
    except Exception as e:
        # TODO: Specify exception
        logger.error(f'Failed to append lines of text to the beginning of file ({filepath}). Exception: {e}')
        return False
    return True


def is_list_items_in_dict(list_items:list, dict_to_check:dict) -> int:
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


def url_to_name(url:str) -> str:
    """Convert the jenkins item URL to its name

    Args:
        url : URL of the item (ie. folder, job, build)

    Returns:
        The name of the item
    """
    # NOTE: May have issues with urls that have the name "job" in them as item name (ie. test_job)

    url_components = urlparse(url)
    url_converted = url_components.path.strip('/').replace('/job/', '/').strip().strip('/') #.strip('job/')  #.replace('view/', '')
    logger.debug(f'Converted URL "{url}" to name "{url_converted}"')
    return url_converted


def format_name(name:str) -> str:
    """Format / clean up the passed name

    Details: The formatting includes it:
        - remove `job`
        - remove leading or trailing `/`

    Args:
        name : The name of the item

    Returns:
        Formatted item name
    """
    name_formatted = name.strip().replace('/job/', '/').strip('/').replace('job/', '/').strip('/') #.strip('job/')
    logger.debug(f'Formatted "{name}" to "{name_formatted}"')
    return name_formatted


def name_to_url(name:str) -> str:
    """Convert the item name to URL

    ** TODO **

    Args:
        name : The name of the item

    Returns:
        Item URL
    """
    pass


def build_url_to_other_url(build_url:str, target_url:str='job') -> str:
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
        last_index = -2 if not path_list[-1] else  -1
    elif target_url == 'folder':
        last_index = -4 if not path_list[-1] else  -3
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


def build_url_to_build_number(build_url:str) -> int:
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


def item_url_to_server_url(url:str, include_scheme:bool=True) -> str:
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


def has_build_number_started(job_info:dict, build_number:int) -> bool:
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


def item_subitem_list(item_info:Dict, get_key_info:str, item_type:str, item_class_list:list=[], item_class_key:str='_class') -> Tuple[list, list]:
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


def to_seconds(time_quantity:int, time_unit_text:str) -> int:
    """
    Get the number of seconds form the time quantity and time unit type.
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
        return time_quantity * blue_moon * 2.628e+6

    return 0


def html_clean(html:str) -> str:
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


def browser_open(url:str, new:int=2, autoraise:bool=True) -> str:
    """Clean up HTML format to text without HTML tags

    Args:
        url       : Weblink URL
        new       : 0=Same browser window, 1=New browser window, 2=New Tab
        autoraise : True=Window is raised

    Returns:
        True if successfull, else False
    """
    try:
        webbrowser.open(url, new, autoraise)
    except Exception as e:
        logger.debug(f'Failed to open web browser for URL: {url}  Exception: {e}')
        return False
    return True


