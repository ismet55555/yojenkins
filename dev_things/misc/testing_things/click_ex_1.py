#!/usr/bin/env python3

import click


@click.group()
@click.pass_context
@click.option('--opt1', default=1, help='Number of greetings.')
def a(opt1):
    print('A')


@a.command()
@click.pass_context
def a1():
    print('A1')


@a.command()
@click.pass_context
def a2():
    print('A2')


if __name__ == '__main__':
    a()
