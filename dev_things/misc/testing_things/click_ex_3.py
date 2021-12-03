#!/usr/bin/env python3

import click


@click.group()
def main():
    pass


####################################


@main.group()
def job():
    pass


@job.command()
@click.option('--debug',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Enable debug level log messages')
@click.argument('build', nargs=1, type=str, required=True)
def build(debug, build):
    print(debug)
    print(build)


@job.command()
@click.option('--debug',
              type=bool,
              default=False,
              required=False,
              is_flag=True,
              help='Enable debug level log messages')
@click.argument('search', nargs=1, type=str, required=True)
@click.option('-f', '--folder', type=str, default=None, required=False, is_flag=False, help='Folder to search')
@click.option('-d', '--depth', type=int, default=4, required=False, is_flag=False, help='Folder depth level to search')
def search(debug, search, folder, depth):
    print(debug)
    print(search, folder, depth)


####################################


@main.group()
def build():
    pass


@build.command()
@click.option('-o',
              '--ok',
              type=bool,
              default=False,
              required=True,
              is_flag=True,
              help='Enable debug level log messages')
def info(ok):
    print(ok)


####################################

if __name__ == '__main__':
    main()
