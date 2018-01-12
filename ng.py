# coding: utf8

# .-----------------. .----------------.
# | .--------------. || .--------------. |
# | | ____  _____  | || |    ______    | |
# | ||_   \|_   _| | || |  .' ___  |   | |
# | |  |   \ | |   | || | / .'   \_|   | |
# | |  | |\ \| |   | || | | |    ____  | |
# | | _| |_\   |_  | || | \ `.___]  _| | |
# | ||_____|\____| | || |  `._____.'   | |
# | |              | || |              | |
# | '--------------' || '--------------' |
# '----------------'  '----------------'


"""
    Get password of the wifi you're connected, and your current ip address.
"""

import locale
import platform
import re
import subprocess
import sys

import click
import requests

_ver = sys.version_info

# Python 2.x?
is_py2 = (_ver[0] == 2)

# Python 3.x?
is_py3 = (_ver[0] == 3)

SUPPORTED_SYSTEMS = ['Darwin', 'Linux', 'Windows']
DEFAULT_IP_ADDRESS = '127.0.0.1'
VERIFY_HOST = 'https://httpbin.org/ip'
DEFAULT_LOCALE_LANGUAGE = ('en_US', 'UTF-8')

def _system():
    return platform.system()


def _language():
    try:
        locale = locale.getdefaultlocale()
    except ValueError:
        locale = DEFAULT_LOCALE_LANGUAGE
    return locale

def _exec(command):
    out, err = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if is_py3:
        language = _language()
        return (out + err).decode(language[1]).strip()

    return (out + err).strip()


def _detect_wifi_ssid():
    system = _system()
    if system not in SUPPORTED_SYSTEMS:
        return False, 'Unknown operation system {0}'.format(system)

    if system == 'Darwin':
        command = ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I']
        pattern = re.compile(r' SSID: (?P<ssid>.+)')
    elif system == 'Linux':
        command = ['nmcli', '-t', '-f', 'active,ssid', 'dev', 'wifi']
        pattern = re.compile(r"yes:'(?P<ssid>.+)'")
    else:
        command = ['netsh', 'wlan', 'show', 'interfaces']
        pattern = re.compile(r' SSID.+: (?P<ssid>.+)\r')

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
        command = ['sudo', 'cat', '/etc/NetworkManager/system-connections/{0}'.format(ssid)]
        pattern = re.compile(r'psk\=(?P<password>.+)')
    else:
        command = ['netsh', 'wlan', 'show', 'profile', 'name={0}'.format(ssid), 'key=clear']
        language = _language()
        if language[0] == 'zh_CN':
            if is_py3:
                pattern = re.compile(r'关键内容.+: (?P<password>.+)')
            else:
                pattern = re.compile(r'{0}.+: (?P<password>.+)'.format(u'关键内容'.encode(language[1])))
        else:
            pattern = re.compile(r'Key Content.+: (?P<password>.+)')
    rs = _exec(command)
    match = re.search(pattern, rs)
    if not match:
        return False, rs

    return True, match.group('password')


def _hack_ip():
    system = _system()
    if system not in SUPPORTED_SYSTEMS:
        return False, 'Unknown operation system {0}'.format(system)

    local_ip = public_ip = DEFAULT_IP_ADDRESS
    if system == 'Darwin':
        command = ['ifconfig']
        pattern = re.compile(r'inet (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    elif system == 'Linux':
        command = ['ip', 'addr']
        pattern = re.compile(r'inet (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    else:
        command = ['ipconfig']
        pattern = re.compile(r'IPv4.+: (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    rs = _exec(command)
    for match in re.finditer(pattern, rs):
        sip = match.group('ip')
        if sip != DEFAULT_IP_ADDRESS:
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
