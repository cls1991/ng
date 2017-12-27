# coding: utf8

"""
    Get password of the wifi you're connected, and your current ip address.
"""

import locale
import platform
import re
import subprocess
import sys

import click

SUPPORTED_SYSTEMS = ['Darwin', 'Linux', 'Windows']


def _system():
    return platform.system()


def _language():
    return locale.getdefaultlocale()


def _exec(command):
    out, err = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return '{0}{1}'.format(out, err).strip()


def _get_wifi_ssid():
    system = _system()
    if system not in SUPPORTED_SYSTEMS:
        return False, 'Unknown operation system {0}'.format(system)

    if system == 'Darwin':
        command = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']
        pattern = re.compile(r' SSID: (?P<ssid>\w+)')
    elif system == 'Linux':
        command = ['nm-tool']
        pattern = re.compile(r'\*(?P<ssid>\w+):')
    else:
        # @TODO: parse ssid on Windows
        command = ['netsh', 'wlan', 'show', 'interfaces']
        pattern = re.compile(r'')

    rs = _exec(command)
    match = re.search(pattern, rs)
    if not match:
        return False, rs

    return True, match.group('ssid')


def _hack_wifi_password(ssid):
    system = _system()
    if system not in SUPPORTED_SYSTEMS:
        return False, 'Unknown operation system {0}'.format(system)

    if system == 'Darwin':
        command = ['security', 'find-generic-password', '-D', 'AirPort network password', '-ga', ssid]
        pattern = re.compile(r'password: "(?P<password>.+)"')
    elif system == 'Linux':
        command = ['cat', '/etc/NetworkManager/system-connections/{0}'.format(ssid)]
        pattern = re.compile(r'psk\=(?P<password>\w+)')
    else:
        # @TODO: parse wifi password on Windows
        command = ['netsh', 'wlan', 'show', 'profile', 'name={0}'.format(ssid), 'key=clear']
        pattern = re.compile(r'')

    rs = _exec(command)
    match = re.search(pattern, rs)
    if not match:
        return False, rs

    return True, match.group('password')


@click.group()
def cli():
    """Get password of the wifi you're connected, and your current ip address."""
    pass


@click.command()
def ip():
    """Show ip address."""
    click.echo('@TODO: ip')


@click.command()
@click.argument('ssid', required=False)
def password(ssid):
    """Show wifi password."""
    if not ssid:
        ok, err = _get_wifi_ssid()
        if not ok:
            click.secho(click.style(err, fg='red'))
            sys.exit(1)
        ssid = err
    ok, err = _hack_wifi_password(ssid)
    if not ok:
        click.secho(click.style(err, fg='red'))
        sys.exit(1)
    click.secho(click.style('{ssid}:{password}'.format(ssid=ssid, password=err), fg='green'))


# Install click commands.
cli.add_command(ip)
cli.add_command(password)

if __name__ == '__main__':
    cli()
