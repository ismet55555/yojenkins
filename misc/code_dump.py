# Check if at least one option was selected
from YoJenkins.YoJenkins import YoJenkins


if not any(input_options):
    click.echo(click.style("Uh-Oh! Something's wrong here ...", fg='bright_red', bold=True))
    ctx.fail(click.style(f"User Input Error: No '{ctx.info_name}'' command options were specified. Please specify any option. See --help.", fg='bright_red', bold=True))

- @click.option('--json', type=bool, default=False, required=False, is_flag=True, help='Output in json format')  # move higher?
- @click.option('--yaml', type=bool, default=False, required=False, is_flag=True, help='Output in yaml format')  # move higher?


########################################################################
########################################################################


# Get the input arguments
build_url:str = kwargs.pop('build_url', '')
job_name:str = kwargs.pop('job_name', '')
job_url:str = kwargs.pop('job_url', '')
build_number:int = kwargs.pop('build_number', 0)
latest:bool = kwargs.pop('latest', False)

print(kwargs)


########################################################################
########################################################################


# Get the build URL if it is not passed directly
if not build_url:
    build_info = self.J.build_info(
        build_url=build_url,
        job_name=job_name, 
        job_url=job_url,
        build_number=build_number,
        latest=latest
        )
    # TODO: check for blank return
    build_url = build_info['url']



########################################################################
########################################################################



#TODO: Move this message below to the main function where click is

# Checking if authentication succeeded by getting user name
try:
    self.user_info = self.J.get_whoami()
except jenkins.JenkinsException as e:
    # TODO: Move this message to cli_auth.py, only return bool
    error_no_html = e.args[0].split("\n")[0]
    logger.fatal(f'Jenkins server authentication failed.')
    logger.fatal(f'Exception: {error_no_html}')
    logger.fatal(f'Possible causes:')
    logger.fatal(f'  - Wrong Jenkins server URL')
    logger.fatal(f'  - Incorrect credentials')
    logger.fatal(f'  - Expired API Token')
    logger.fatal(f'  - You do not have access')
    logger.fatal('')
    logger.fatal('To update Jenkins credentials run:')
    logger.fatal('    yo-jenkins TODO')
    return False
except requests.exceptions.HTTPError as e:
    logger.fatal(f'Jenkins server authentication failed. Exception: {e}')
    return False
logger.debug(f'Successfully authenticated')
self.authenticated = True




########################################################################
########################################################################



# YoJenkins.py -> build_info

if 'actions' in build_info:
    pprint(build_info['actions'])
    for action in build_info['actions']:
        pprint(action)
        print(JenkinsItemClasses.action.value['class_type'])
        if action['_class'] in JenkinsItemClasses.action.value['class_type']:
            build_info['actionUserId'] = action['causes'][0]['userId']
            build_info['actionUserName'] = action['causes'][0]['userName']
            build_info['actionShortDescription'] = action['causes'][0]['shortDescription']



########################################################################
########################################################################


# YoJenkins.py -> queue stuff

# If no build info found, check server build queue
if not build_info:
    logger.debug('The specified build was not found')
    logger.debug('Looking for build in the server build queue ...')
    logger.debug('Finding job name ...')
    if build_url:
        job_url = utility.build_url_to_other_url(build_url)
        job_name = utility.url_to_name(job_url)
    elif job_name:
        pass
    elif job_url:
        job_name = utility.url_to_name(job_url)
    else:
        logger.debug('Failed to find build status text. Specify build url, job name, or job url')
        return {}
    logger.debug(f'Job name: {job_name}')
    build_info, queue_number = self.job_in_queue_check(job_name=job_name)
    if not build_info:
        logger.debug('Build not found in queue')
        return {}
    else:
        logger.debug(f'Build found in queue. Queue number {queue_number}')
        build_info['isQueuedItem'] = True
else:
    build_info['isQueuedItem'] = False