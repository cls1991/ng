# coding: utf8

"""
    Get password of the wifi you're connected, and your current ip address.
"""

import platform
import re
import subprocess
import sys

import click
import requests

SUPPORTED_SYSTEMS = ['Darwin', 'Linux']
LOCAL_IP_ADDRESS = '127.0.0.1'
VERIFY_HOST = 'https://httpbin.org/ip'


def _system():
    return platform.system()


def _exec(command):
    out, err = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return '{0}{1}'.format(out, err).strip()


def _detect_wifi_ssid():
    system = _system()
    if system not in SUPPORTED_SYSTEMS:
        return False, 'Unknown operation system {0}'.format(system)

    if system == 'Darwin':
        command = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']
        pattern = re.compile(r' SSID: (?P<ssid>\w+)')
    else:
        command = ['nm-tool']
        pattern = re.compile(r'\*(?P<ssid>\w+):')

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
    else:
        command = ['sudo', 'cat', '/etc/NetworkManager/system-connections/{0}'.format(ssid)]
        pattern = re.compile(r'psk\=(?P<password>\w+)')

    rs = _exec(command)
    match = re.search(pattern, rs)
    if not match:
        return False, rs

    return True, match.group('password')


def _hack_ip():
    system = _system()
    if system not in SUPPORTED_SYSTEMS:
        return False, 'Unknown operation system {0}'.format(system)

    local_ip = LOCAL_IP_ADDRESS
    public_ip = LOCAL_IP_ADDRESS
    command = ['ifconfig']
    rs = _exec(command)
    for match in re.finditer(r'inet (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', rs):
        sip = match.group('ip')
        if sip != LOCAL_IP_ADDRESS:
            local_ip = sip
            break

    try:
        r = requests.get(VERIFY_HOST)
        public_ip = r.json()['origin']
    except requests.RequestException:
        pass
    return True, '{0}\n{1}'.format(local_ip, public_ip)


@click.group()
def cli():
    """Get password of the wifi you're connected, and your current ip address."""
    pass


@click.command()
def ip():
    """Show ip address."""
    ok, err = _hack_ip()
    if not ok:
        click.secho(click.style(err, fg='red'))
        sys.exit(1)
    click.secho(click.style(err, fg='green'))


@click.command()
@click.argument('ssid', required=False)
def wp(ssid):
    """Show wifi password."""
    if not ssid:
        ok, err = _detect_wifi_ssid()
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
cli.add_command(wp)

if __name__ == '__main__':
    cli()
