import sched
import time
import yaml
from . import archive
from . import analysis


def checkConfig(config):

    if config is None or config is {}:
        print("config: empty!")
        return False

    good = True

    if 'localRoot' not in config:
        good = False
        print("config: no localRoot")

    if 'analyses' in config:
        for a in config['analyses']:
            if len(a) != 1:
                good = False
                print("config: analysis requires single top-level entry"
                      " - {0:s}".format(str(a.keys())))
                continue

            (name, pars), = a.items()

            if pars is None or len(pars) <= 0:
                good = False
                print("config: analysis {0:s} is empty".format(name))
                continue

            if 'cadence' not in pars:
                good = False
                print("config: analysis {0:s} has no cadence".format(name))

            if 'outputDir' not in pars:
                good = False
                print("config: analysis {0:s} has no outputDir".format(name))

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

    print(config)

    arch = archive.Archive(config['localRoot'])

    print(arch)
    print(arch.getNodeNames())

    s = sched.scheduler(time.time, time.sleep)

    for entry in config['analyses']:
        (name, pars), = entry.items()
        a = buildAnalysis(s, name, pars, arch)
        if a.cadence is not None:
            s.enter(a.cadence, 1, a.run, (arch, ))
        else:
            s.enter(1.0, 1, a.run, (arch, ), None)

    print(s.queue)

    s.run()


def buildAnalysis(scheduler, name, pars, arch):

    cadenceStr = pars['cadence']
    outputDir = pars['outputDir']

    cadence = float(cadenceStr)

    maxIter = None
    if 'maxIter' in pars:
        maxIter = pars['maxIter']

    a = analysis.Analysis(scheduler, name, cadence, outputDir, maxIter)

    return a
