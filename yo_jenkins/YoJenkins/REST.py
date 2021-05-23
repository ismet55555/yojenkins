#!/usr/bin/env python3

import logging
from pprint import pprint
from time import sleep, time
from typing import Dict, List, Tuple, Type

import requests
from requests_futures.sessions import FuturesSession
from requests_cache import CachedSession
from requests.auth import HTTPBasicAuth

# Getting the logger reference
logger = logging.getLogger()


# TODO: Septate functionalities
#       - GET, POST, HEAD
#       - Time request (request statistics)


class REST:
    """Handeling of REST requests"""

    def __init__(self, username:str='', api_token:str='', server_url:str='', session=None, is_cached:bool=False) -> None:
        """TODO Docstring

        Args:
            TODO

        Details: 
            Troubleshoot: nettop -p Python

        Returns:
            TODO
        """
        # Request session
        self.is_cached = is_cached
        if not session:
            if is_cached:
                logger.debug('Starting new CACHED requests session ...')
                self.request_session = CachedSession(backend='sqlite', expire_after=2)
            else:
                logger.debug('Starting new requests session (FuturesSession) ...')
                self.request_session = FuturesSession(max_workers=16)
        else:
            # Convert to future session
            logger.debug('Converting request session to FutureSession ...')
            self.request_session = FuturesSession(session=session, max_workers=16)

        # Authentication passed
        self.username:str = username
        self.api_token:str = api_token
        self.server_url:str = server_url

        # Flag signaling if this object has authentication credentials to server
        self.has_credentials = False


    def set_credentials(self, username:str, api_token:str, server_url:str) -> None:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        self.username = username
        self.api_token = api_token
        self.server_url = server_url.strip('/') + '/'
        self.has_credentials = True


    def get_server_url(self) -> str:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        return self.server_url


    def get_active_session(self) -> object:
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        return self.request_session


    def is_reachable(self, server_url:str='', timeout:int=5) -> bool:
        """Check if the server is reachable

        Args:
            server_url: URL of server to check

        Returns:
            True if reachable, else False
        """
        if not server_url:
            server_url = self.server_url.strip('/') + '/'

        logger.debug(f'Checking if server is reachable: "{server_url}" ...')

        request_success = self.request(
            target=server_url,
            is_endpoint=False,
            request_type='head',
            auth_needed=False,
            timeout=timeout)[2]

        if request_success:
            logger.debug('Successfully found server is reachable')
        else:
            logger.debug('Failed. Server cannot be reached or is offline')
        return request_success


    def clear_cache(self):
        """TODO Docstring

        Args:
            TODO

        Returns:
            TODO
        """
        if self.is_cached:
            self.request_session.cache.clear()
            logger.debug('Successfully cleared request session cache')


    def request(self, target:str, request_type:str, is_endpoint:bool=True, json_content:bool=True, auth:Tuple=None, auth_needed:bool=True, new_session:bool=False, params:dict={}, data:dict={}, headers:dict={}, timeout:int=10) -> Tuple[Dict, Dict, bool]:
        """Utility method for a single REST requests

        Details: Currently supported GET, POST, HEAD

        **TODO**: Refactor/Rework this method. Maybe take appart?

        Args:
            target       : Request URL target. Does not include server_url
            is_endpoint  : If True, add the object stored server URL, else do not
            request_type : Type of request. Currently `get` and `post` only
            json_content : If True, parse as json/dict, else return raw content text
            auth         : Credentials in (username, password) format
            auth_needed  : If True, use credentials, else do not
            new_session  : If True, create a new connection sessions, else re-use previous/default session
            params       : Parameters passed with the request
            headers      : Headers passed with the request

        Returns:
            Tuple of return content, return header, return success
        """
        # Constructing the request URL
        if is_endpoint:
            request_url = self.server_url.strip('/') + '/' + target.strip('/')
        else:
            request_url = target

        logger.debug(f'Request URL: {request_url}')

        # Get credentials if needed
        if auth_needed:
            if not auth:
                auth=HTTPBasicAuth(self.username, self.api_token)

        # Use a connection session if possible
        if not self.request_session or new_session:
            logger.debug('Starting new requests session')
            self.request_session = FuturesSession(max_workers=16)

        # Making the request
        try:
            elapsed_time = time()
            if request_type.lower() == 'get':
                response = self.request_session.get(request_url, params=params, data=data, headers=headers, auth=auth, timeout=timeout)
            elif request_type.lower() == 'post':
                response = self.request_session.post(request_url, params=params, data=data, headers=headers, auth=auth, timeout=timeout)
            elif request_type.lower() == 'head':
                response = self.request_session.head(request_url, params=params, data=data, headers=headers, auth=auth, timeout=timeout)
            else:
                logger.debug(f'Request type "{request_type}" not recognized')
                return {}, {}, False
        except requests.exceptions.ConnectionError as e:
            logger.debug(f'Failed to make request. Connection error. Exception: {e}')
            return {}, {}, False
        except requests.exceptions.InvalidSchema as e:
            logger.debug(f'Failed to make request. Request format error. Exception: {e}')
            return {}, {}, False
        except Exception as e:
            logger.debug(f'Failed to make request. Exception: {e}')
            return {}, {}, False  

        # Get the content from requests_cache.CachedSession() return
        try:
            if hasattr(response, 'result'):
                response = response.result()
        except requests.exceptions.ProxyError as e:
            logger.debug(f'Failed to make request. Request timeout. Exception: {e}')
            return {}, {}, False
        except requests.exceptions.MissingSchema as e:
            logger.debug(f'Failed to make request. URL error. Exception: {e}')
            return {}, {}, False
 
        logger.debug('Request info:')
        logger.debug(f'   - Elapsed time: {time() - elapsed_time} seconds')
        logger.debug(f'   - Return status code: {response.status_code}')
        if self.is_cached:
            logger.debug(f'   - Used request cache: {response.from_cache}')

        # Check the return status code
        if not response.ok:
            logger.debug(f'Failed to make {request_type.upper()} request "{request_url}". Server code: {response.status_code}')
            return {}, {}, False
        success = True

        # Get the return header
        return_headers: dict = {}
        if response.headers:
            return_headers = response.headers
            logger.debug(f'Request return headers: {return_headers}')
        else:
            logger.debug(f'No headers received form {request_type.upper()} request: {request_url}')

        # If a head request, only return headers
        if request_type.lower() == 'head':
            return {}, return_headers, success

        # Get the return content and format it
        return_content = {}
        if response.content:
            if json_content:
                # Check for json parsing errors
                try:
                    return_content = response.json()
                except Exception as e:
                    # TODO: Specify json parse error
                    logger.debug(f"Failed to parse request return as JSON. Possible HTML content. Exception: {e})")
            else:
                return_content = response.text
        else:
            logger.debug(f'No content received form {request_type.upper()} request: {request_url}')

        return return_content, return_headers, success

