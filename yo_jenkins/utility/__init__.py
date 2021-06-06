#!/usr/bin/env python3

import logging
import re
import webbrowser
from typing import Dict, List, Tuple
from urllib.parse import urljoin, urlparse
import sysconfig
import os
import site

import requests
import yaml
from ..YoJenkins.JenkinsItemClasses import JenkinsItemClasses

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
        The full name of the item
    """
    # Split url into base componenets
    url_components = urlparse(url)

    # Split and filter out terms
    # name = url_components.path.strip('/').replace('/job/', '/').strip().strip('/').strip('job/').replace('view/', '').replace('change-requests/', '')
    url_split = url_components.path.strip().strip('/').split('/')
    remove_list = ['job', 'view', 'change-requests']

    filtered_list =  []
    for list_item in url_split:  # TODO: Use list comprehension
        if list_item not in remove_list: 
            filtered_list.append(list_item)
    
    # Assemble back
    name = '/'.join(filtered_list)

    logger.debug(f'Converted URL "{url}" to fullname "{name}"')
    return name


def format_name(name:str) -> str:
    """Format / clean up the passed name

    Details: The formatting includes it:
        - /Non-PAR/job/Non-Prod-Jobs/job/Accenture/job/job --> /Non-PAR/Non-Prod-Jobs/Accenture/job
        - remove `job/`, `view/`, `change-requests/` 
        - remove leading or trailing `/`

    Args:
        name : The name of the item

    Returns:
        Formatted item name
    """
    # Filter out terms
    name_formatted = name.strip().replace('/job/', '/').strip('/')
    name_formatted = name_formatted.replace('job/', '/').strip('/').replace('view/', '').replace('change-requests/', '')

    logger.debug(f'Formatted "{name}" to "{name_formatted}"')
    return name_formatted


def fullname_to_name(fullname:str) -> str:
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


def name_to_url(server_base_url:str, name:str) -> str:
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
        webbrowser.open(url.strip('/'), new, autoraise)
    except Exception as e:
        logger.debug(f'Failed to open web browser for URL: {url.strip("/")}  Exception: {e}')
        return False
    return True


def has_special_char(text:str, special_chars:str='@!#$%^&*<>?/\|~:') -> bool:
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


def remove_special_char(text:str, special_chars:str='@!#$%^&*<>?/\|~:') -> str:
    """Remove any special characters from text string

    Args:
        text          : Text to remove special characters from
        special_chars : String with all special characters to remove

    Returns:
        Text with special characters removed
    """
    regex = re.compile('[' + special_chars + ']')
    text_new = re.sub(regex, '', text)
    logger.debug(f'Removed special characters "{special_chars}" form string')
    return text_new


def queue_find(all_queue_info:dict, job_name:str='', job_url:str='', first:bool=True) -> list:
    """Finding job in server build queue

    Args:
        TODO

    Returns:
        TODO
    """
    if not job_name and not job_url:
        logger.debug('Failed to get job information. No job name or job url received')
        return {}
    job_name = job_name if job_name else url_to_name(job_url)

    queue_item_matches = []

    for i, queue_item in enumerate(all_queue_info['items']):
        # Check the item type
        if queue_item['task']['_class'] not in JenkinsItemClasses.job.value['class_type']:
            logger.debug(f"[ITEM {i+1}/{len(all_queue_info['items'])}] Queued item not a job. Item class: {queue_item['task']['_class']}")
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
        logger.debug(f'Failed to find job in build queue')

    return queue_item_matches


def get_resource_path(relative_path:str) -> str:
    """Getting the filepath for existing included resource

    Args:
        TODO

    Returns:
        Included resource path
    """
    # Get the path in python site packages
    resource_dir = get_resource_dir()
    resource_path = os.path.abspath(os.path.join(resource_dir, relative_path))

    # If the file has not been found and it is on windows, try APPDATA directory
    if not os.path.exists(resource_path):
        logger.debug(f'Failed to find resource "{relative_path}" in: {resource_dir}')
        return ''
    logger.debug(f'Successfully found existing resource: {resource_path}')
    return resource_path


def get_resource_dir(project_dir:str='yo_jenkins', sample_path:str='sound') -> str:
    """Getting the path to the directory containing project resources
    
    Details:
        Effectively this function is looking through all possible package locations
    and checking if it contains a directory with the project name

    FIXME: Probably only need the relative path!

    Args:
        TODO

    Returns:
        Project directory absolute path
    """
    possible_dirs = {
        'relative': os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..')),
        'sys_dirs': sysconfig.get_paths()["purelib"],
        'usr_dirs': site.getusersitepackages(),
        'site_dirs': site.getsitepackages(),
        'cwd': os.getcwd(),
    }

    dirs = []
    for v in possible_dirs.values():
        if isinstance(v, list):
            dirs.extend(v)
        else:
            dirs.append(v)

    logger.debug(f'Searching project resource directory ...')
    resource_dir_path = ''
    for dir in dirs:
        if os.path.exists(os.path.join(dir, project_dir, sample_path)):
            resource_dir_path = os.path.join(dir, project_dir)
            logger.debug(f'    - {dir} - FOUND')
            break
        logger.debug(f'    - {dir} - NOT FOUND')

    if not resource_dir_path:
        logger.debug(f'Failed to find included data directory')
        return ''

    return resource_dir_path
