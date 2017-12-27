# coding: utf8


import subprocess


def execute(cmd):
    out = None
    if cmd:
        try:
            out, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
        except ValueError:
            pass

    return out


def test_ng():
    assert execute(['ng'])


def test_ng_ip():
    assert execute(['ng', 'ip'])


def test_ng_password():
    assert execute(['ng', 'password'])


def test_ng_help():
    assert execute(['ng', '--help'])
