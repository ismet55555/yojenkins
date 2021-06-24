import click


@click.group()
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug



@cli.command()
@click.option('--int1',  default=1, help='Number of greetings', nargs=1, type=int, required=False, multiple=False, count=False, is_flag=False)
@click.option('--bool1', default=True, help='Flag to turn on blah', nargs=1, type=bool, required=False, multiple=False, count=False, is_flag=True)
@click.option('--str1',  default=None, help='Some url for blah', nargs=1, type=str, required=True, multiple=False, count=False, is_flag=False)
@click.pass_context
def command1(ctx, int1, bool1, str1):
    click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    # click.echo(count)
    # click.echo(count)
    click.echo(str1)



@cli.command()
@click.option('--int1',  default=1, help='Number of greetings', nargs=1, type=int, required=False, multiple=False, count=False, is_flag=False)
@click.option('--bool1', default=True, help='Flag to turn on blah', nargs=1, type=bool, required=False, multiple=False, count=False, is_flag=True)
@click.option('--str1',  default=None, help='Some url for blah', nargs=1, type=str, required=True, multiple=False, count=False, is_flag=False)
@click.pass_context
def command2(ctx, int1, bool1, str1):
    click.echo('Debug is %s' % (ctx.obj['DEBUG'] and 'on' or 'off'))
    # click.echo(count)
    # click.echo(count)
    click.echo(str1)




if __name__ == '__main__':
    cli(obj={})



