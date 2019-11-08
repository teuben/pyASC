import os
import re


class Archive:

    def __init__(self, dataDir):
        self.rootdir = os.path.abspath(dataDir)
        self._setup()

    def __repr__(self):
        return "Archive(rootdir={0:s})".format(repr(self.rootdir))

    def getNodeNames(self):
        names = [k for k in self.nodes.keys()]
        return names

    def getFITS(self, node, yyyymmdd):
        # yyyymm = yyyymmdd[:6]
        # day = self.nodes[node][yyyymm][yyyymmdd]

        path = self._getDayPath(node, yyyymmdd)

        files = os.listdir(path)

        fits = []
        for filename in files:
            if os.path.splitext(filename)[1] == ".FIT":
                fits.append(filename)
        fits.sort()

        for fit in fits:
            yield os.path.join(path, fit)

    def _setup(self):
        dirs = os.listdir(self.rootdir)
        self.nodes = {}
        self.years = []

        nodePattern = r"MASN-[0-9][0-9]"

        for d in dirs:
            if re.fullmatch(nodePattern, d) is not None:
                self.nodes[d] = {}

        monthPattern = r"[0-9]{6}"
        dayPattern = r"[0-9]{8}"

        for node in self.nodes:
            path = os.path.join(self.rootdir, node)
            dirs = os.listdir(path)
            for mo in dirs:
                if re.fullmatch(monthPattern, mo) is not None:
                    year = int(mo[:4])
                    month = int(mo[4:])
                    if month >= 1 and month <= 12:
                        self.nodes[node][mo] = {}
                        if year not in self.years:
                            self.years.append(year)
                        daypath = os.path.join(path, mo)
                        daydirs = os.listdir(daypath)
                        for daydir in daydirs:
                            if re.fullmatch(dayPattern, daydir) is not None:
                                if mo == daydir[:6]:
                                    day = int(daydir[-2:])
                                    if ((month in [1, 3, 5, 7, 8, 10, 12]
                                         and day <= 31)
                                            or (month in [4, 6, 9, 11]
                                                and day <= 30)
                                            or day <= 29) and day >= 1:
                                        self.nodes[node][mo][daydir] = {}

        for n in self.nodes:
            node = self.nodes[n]
            for ym in node:
                month = node[ym]
                for ymd in month:
                    day = month[ymd]
                    path = os.path.join(self.rootdir, n, ym, ymd)
                    count = 0
                    files = os.listdir(path)
                    for filename in files:
                        if os.path.splitext(filename)[1] == ".FIT":
                            count += 1
                    day['num'] = count

    def _getDayPath(self, node, yyyymmdd):

        yyyymm = yyyymmdd[:6]
        path = os.path.join(self.rootdir, node, yyyymm, yyyymmdd)
        return path
