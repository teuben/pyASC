# import os
import yaml
from . import archive


def checkConfig(config):

    if config is None or config is {}:
        print("config: empty!")
        return False

    good = True

    if 'localRoot' not in config:
        good = False
        print("config: no localRoot")

    return good


def runYAML(configFile):

    try:
        with open(configFile, "r") as f:
            config = yaml.safe_load(f)
    except IOError as e:
        print("Could not load file: {0:s}".format(configFile))
        print(e)
        return

    if not checkConfig(config):
        print("Bad configuration, exiting.")
        return

    arch = archive.Archive(config['localRoot'])

    print(arch)
    print(arch.getNodeNames())
