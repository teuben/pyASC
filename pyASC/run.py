import numbers
import sched
import time
import yaml
from . import archive
from . import action


def checkConfig(config):

    if config is None or config is {}:
        print("config: empty!")
        return False

    good = True

    if 'localRoot' not in config:
        good = False
        print("config: no localRoot")

    if 'databaseFile' not in config:
        good = False
        print("config: no databaseFile")

    if 'actions' in config:
        for a in config['actions']:
            if len(a) != 1:
                good = False
                print("config: action requires single top-level entry"
                      " - {0:s}".format(str(a.keys())))
                continue

            """
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
            """

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

    arch = archive.Archive(config['localRoot'], config['databaseFile'],
                           debug=True)

    print(arch)

    s = sched.scheduler(time.time, time.sleep)

    updateCadence = config['update']
    a = action.UpdateArchive(s, "Update", updateCadence, None)
    s.enter(1.0, 0, a.run, (arch, ))

    for entry in config['actions']:
        (name, pars), = entry.items()
        a = buildAction(s, name, pars, arch)
        if isinstance(a.cadence, numbers.Real):
            s.enter(a.cadence, 2, a.run, (arch, ))
        else:
            s.enter(1.1, 2, a.run, (arch, ))

    print(s.queue)

    s.run()


def buildAction(scheduler, name, pars, arch):

    cadence = pars['cadence']
    outputDir = pars['outputDir']

    maxIter = None
    if 'maxIter' in pars:
        maxIter = pars['maxIter']

    if name == 'MakeImage':
        label = None
        if 'label' in pars:
            label = pars['label']
        targetDate = pars['targetDate']
        overwrite = None
        if 'overwrite' in pars:
            overwrite = pars['overwrite']
        inputDir = None
        if 'inputDir' in pars:
            inputDir = pars['inputDir']
        blackVal = None
        if 'blackVal' in pars:
            blackVal = pars['blackVal']
        whiteVal = None
        if 'whiteVal' in pars:
            whiteVal = pars['whiteVal']

        a = action.MakeImage(scheduler, name, cadence, outputDir, maxIter,
                             targetDate, label=label, overwrite=overwrite,
                             inputDir=inputDir, blackVal=blackVal,
                             whiteVal=whiteVal)

    elif name == 'MakeHist':
        label = None
        if 'label' in pars:
            label = pars['label']
        targetDate = pars['targetDate']
        overwrite = None
        if 'overwrite' in pars:
            overwrite = pars['overwrite']
        bitDepth = None
        if 'bitDepth' in pars:
            bitDepth = pars['bitDepth']
        binWidth = None
        if 'binWidth' in pars:
            binWidth = pars['binWidth']
        inputDir = None
        if 'inputDir' in pars:
            inputDir = pars['inputDir']
        a = action.MakeHist(scheduler, name, cadence, outputDir, maxIter,
                             targetDate, label=label, overwrite=overwrite,
                             bitDepth=bitDepth, binWidth=binWidth,
                             inputDir=inputDir)

    elif name == 'CopyByRA':
        label = None
        if 'label' in pars:
            label = pars['label']
        targetRA = pars['targetRA']
        targetDate = pars['targetDate']
        RAtolerance = pars['RAtolerance']
        a = action.CopyByRA(scheduler, name, cadence, outputDir, maxIter,
                            targetRA, targetDate, RAtolerance, label=label)
    else:
        a = action.Action(scheduler, name, cadence, outputDir, maxIter)

    return a
