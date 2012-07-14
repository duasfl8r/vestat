#!/usr/bin/python2
import fabric
from fabric.api import local
from fabric.context_managers import lcd

import settings

EXCLUDE = [
        "venv",
        "*.pyc",
        ".ropeproject",
        "__pycache__"
]

def hide_4ever(*groups):
    for group in groups:
        fabric.state.output[group] = False

def silence_is_golden(verbose=False, *additional_groups):
    hidden_groups = ['running', 'stdout', 'status']
    hidden_groups.extend(additional_groups)
    if not verbose:
        hidden_groups.append('user')
    hide_4ever(*hidden_groups)

def build():
    silence_is_golden()
    with lcd(".."):
        local("tar -czf vestat_{versao}.tar.gz vestat".format(versao=settings.VERSAO) + \
              " --exclude-vcs" + \
              "".join(" --exclude='{p}'".format(p=p) for p in EXCLUDE))
