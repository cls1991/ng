# coding: utf8

"""
    Get password of the wifi you're connected, and your current ip address.
"""

import click


@click.group()
def cli():
    """Get password of the wifi you're connected, and your current ip address."""
    pass


@click.command()
def ip():
    """Show ip address."""
    click.echo('@TODO: ip')


@click.command()
def password():
    """Show wifi password."""
    click.echo('@TODO: password')


# Install click commands.
cli.add_command(ip)
cli.add_command(password)

if __name__ == '__main__':
    cli()
