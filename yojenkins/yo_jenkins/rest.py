"""Rest class definition"""

import logging
from time import perf_counter
from typing import Dict, Literal, Tuple, Union

import requests
from requests.auth import HTTPBasicAuth
from requests_futures.sessions import FuturesSession

# Getting the logger reference
logger = logging.getLogger()


class Rest:
    """Handeling of REST requests"""

    def __init__(self, username: str = '', api_token: str = '', server_url: str = '', session=None) -> None:
        """TODO Docstring

        Args:
            TODO

        Details:
            Troubleshoot: nettop -p Python

        Returns:
            TODO
        """
        # Request session
        if not session:
            logger.debug('Starting new requests session (Type: FuturesSession) ...')
            self.session = FuturesSession(max_workers=16)
        else:
            # Convert to future session
            logger.debug('Converting request session to FutureSession ...')
            self.session = FuturesSession(session=session, max_workers=16)

        # Authentication passed
        self.username: str = username
        self.api_token: str = api_token
        self.server_url: str = server_url

        # Flag signaling if this object has authentication credentials to server
        self.has_credentials = False

    def set_credentials(self, username: str, api_token: str, server_url: str) -> None:
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
        return self.session

    def is_reachable(self, server_url: str = '', timeout: int = 5) -> bool:
        """Check if the server is reachable

        Details:
            `/login` endpoint used to verify

        Args:
            server_url: URL of server to check

        Returns:
            True if reachable, else False
        """
        if not server_url:
            server_url = self.server_url.strip('/') + '/login'

        logger.debug(f'Checking if server is reachable: "{server_url}" ...')

        request_success = self.request(target=server_url,
                                       is_endpoint=False,
                                       request_type='head',
                                       auth_needed=False,
                                       timeout=timeout)[1]

        if request_success:
            logger.debug('Successfully found server is reachable')
            return True
        else:
            logger.debug('Failed. Server cannot be reached or is offline')
            return False

    def request(self,
                target: str,
                request_type: Literal['get', 'post', 'head'],
                is_endpoint: bool = True,
                json_content: bool = True,
                auth: Tuple = None,
                auth_needed: bool = True,
                new_session: bool = False,
                params: dict = {},
                data: dict = {},
                json_data: dict = {},
                headers: dict = {},
                timeout: int = 10,
                allow_redirect: bool = True) -> Tuple[Union[Dict, str], Dict, bool]:
        """Utility method for a single REST requests

        Details: Currently supported GET, POST, HEAD

        **TODO**: Refactor/Rework this method. Too bloated. Take appart into multiple methods!

        Args:
            target         : Request URL target. Does not include server_url
            is_endpoint    : If True, add the object-stored server URL address, else do not
            request_type   : Type of request. Currently `get`, `post`, `head` only
            json_content   : If True, parse as json/dict, else return raw content text
            auth           : Credentials in (username, password) format
            auth_needed    : If True, use credentials, else do not
            new_session    : If True, create a new connection sessions, else re-use previous/default session
            params         : Parameters passed with the request
            data           : Data passed with the request
            json_data      : JSON data passed with the request
            headers        : Headers passed with the request
            timeout        : Number of seconds to wait for request
            allow_redirect : If True, allow request redirection to other URLs

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
                auth = HTTPBasicAuth(self.username, self.api_token)

        # Use a connection session if possible
        if not self.session or new_session:
            logger.debug('Starting new requests session')
            self.session = FuturesSession(max_workers=16)

        # Making the request
        start_time = perf_counter()
        try:
            if request_type.lower() == 'get':
                response = self.session.get(request_url,
                                            params=params,
                                            data=data,
                                            json=json_data,
                                            headers=headers,
                                            auth=auth,
                                            timeout=timeout,
                                            allow_redirects=allow_redirect)
            elif request_type.lower() == 'post':
                response = self.session.post(request_url,
                                             params=params,
                                             data=data,
                                             json=json_data,
                                             headers=headers,
                                             auth=auth,
                                             timeout=timeout,
                                             allow_redirects=allow_redirect)
            elif request_type.lower() == 'head':
                response = self.session.head(request_url,
                                             params=params,
                                             data=data,
                                             json=json_data,
                                             headers=headers,
                                             auth=auth,
                                             timeout=timeout,
                                             allow_redirects=allow_redirect)
            elif request_type.lower() == 'delete':
                response = self.session.delete(request_url,
                                               params=params,
                                               data=data,
                                               json=json_data,
                                               headers=headers,
                                               auth=auth,
                                               timeout=timeout,
                                               allow_redirects=allow_redirect)
            else:
                logger.debug(f'Request type "{request_type}" not recognized')
                return {}, {}, False
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidSchema,
                requests.exceptions.RequestException) as error:
            logger.debug(f'Failed to make request. Exception: {error}')
            return {}, {}, False

        # Wait on the response to complete and get result
        try:
            if hasattr(response, 'result'):
                response = response.result()
        except (requests.exceptions.RequestException, Exception) as error:
            logger.debug(f'Failed to make request. Exception: {error}')
            return {}, {}, False

        # For Debug Purposes
        # print(html_clean(str(response.content)))

        # Logging any request redirects
        if response.history:
            for i, redirect_hop in enumerate(response.history):
                logger.debug('Request redirects:')
                logger.debug(
                    f'    - {i+1}/{len(response.history)}: {redirect_hop.request.method} - {redirect_hop.url} - Status: {redirect_hop.status_code}'
                )

        redirect_methods = ": " + " --> ".join([r.request.method for r in response.history] +
                                               [response.request.method]) if response.history else ''
        response_content_type = response.headers["Content-Type"] if "Content-Type" in response.headers else "N/A"
        response_content_len = response.headers["Content-Length"] if "Content-Length" in response.headers else "N/A"

        # Final request report
        logger.debug('Request summary:')
        logger.debug(f'   - Request:          {response.request.method} - {request_url}')
        logger.debug(f'   - Redirects:        {"Allow" if allow_redirect else "Block"} {redirect_methods}')
        logger.debug(f'   - Elapsed time:     {perf_counter() - start_time:.3f} seconds')
        logger.debug(f'   - Response headers: {response_content_type} (Content Length Bytes: {response_content_len})')
        logger.debug(f'   - Status code:      {response.status_code} ({response.reason})')

        # Check for permission denied
        if response.status_code in [401, 403, 405]:
            logger.debug('PERMISSION DENIED - Request denied due to insufficient privileges')

        # Check conflict
        if response.status_code in [409]:
            logger.debug('CONFLICT - Request failed due to conflict. Possible duplicate entry')

        # If a head request, only return headers
        if request_type.lower() == 'head':
            return {}, response.headers, response.ok

        # Check the return status code
        if not response.ok:
            logger.debug(
                f'Failed to make {request_type.upper()} request "{request_url}". Server code: {response.status_code}')
            if response.headers:
                logger.debug(f'Response headers: {response.headers}')
            return {}, {}, False

        # Get the return content and format it
        return_content = {}
        if response.content:
            if json_content:
                # Check for json parsing errors
                try:
                    return_content = response.json()
                except Exception as error:
                    # TODO: Specify json parse error
                    logger.debug(f"Failed to parse request return as JSON. Possible HTML content. Exception: {error})")
            else:
                return_content = response.text
        else:
            logger.debug(f'No content received from {request_type.upper()} request: {request_url}')

        return return_content, response.headers, True
