from pathlib import Path
import re
import sqlite3
import datetime
import astropy.coordinates as coordinates
import astropy.io.fits as fits
import astropy.units as u
from astropy.time import Time

class Archive:

    nodePattern = r"MASN-([0-9]{2})"
    yearmonthPattern = r"([0-9]{4})([01][0-9])"
    dayPattern1 = (r"([0-9]{4})-([01][0-9])-([0-3][0-9]) to "
                   r"([0-9]{4})-([01][0-9])-([0-3][0-9])")
    obsPattern1 = (r"MASN([0-9]{2})-([0-9]{4})-([0-9]{2})-([0-9]{2})"
                   r"T([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{3})Z.fits")
    dayPattern2 = r"([0-9]{4})([01][0-9])([0-3][0-9])"
    obsPattern2 = r"IMG([0-9]{5}).FIT"
    
    nodeData = {1: {'lat': 39.0021*u.deg, 'lon': -76.956*u.deg}}


    def __init__(self, dataPath, dbFilename):
        self.dbFilename = Path(dbFilename)
        self.rootdir = Path(dataPath)
        self.nodes = []
        self._setup()

    def __repr__(self):
        return "Archive(rootdir={0:s}, db={1:s})".format(repr(self.rootdir),
                                                         repr(self.dbFilename))

    def _setup(self):

        conn = sqlite3.connect(self.dbFilename)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS masndata
                     (node INT, obstime TEXT, exptime REAL,
                      ra_zenith REAL, fitsfile TEXT)''')

        conn.commit()

        for nodedir in self.rootdir.iterdir():
            if nodedir.is_dir():
                match = re.fullmatch(self.nodePattern, nodedir.name)
                if match:
                    node = int(match.group(1))
                    self.nodes.append(node)
                    self._setupNode(c, node, nodedir)
        
        conn.close()

    
    def _setupNode(self, c, node, nodedir):

        ndata = self.nodeData[node]
        ndata['loc'] = coordinates.EarthLocation(lat=ndata['lat'],
                                                 lon=ndata['lon'])

        datadir = nodedir / "archive"
        for ymdir in datadir.iterdir():
            if ymdir.is_dir():
                match = re.fullmatch(self.yearmonthPattern, ymdir.name)
                if match:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    if month >= 1 and month <= 12:
                        self._setupMonth(c, node, year, month, ymdir)

    def _setupMonth(self, c, node, year, month, ymdir):

        for obsdir in ymdir.iterdir():
            if obsdir.is_dir():
                match = re.fullmatch(self.dayPattern1, obsdir.name)
                if match:
                    self._setupObs_v1(c, node, year, month, obsdir,
                                      self.obsPattern1)
                else:
                    match = re.fullmatch(self.dayPattern2, obsdir.name)
                    if match:
                        self._setupObs_v2(c, node, year, month, obsdir,
                                          self.obsPattern2)

    def _setupObs_v1(self, c, node, year, month, obsdir, obsPattern):

        samples = []

        for filepath in obsdir.iterdir():
            if not filepath.is_file():
                continue

            filename = filepath.name

            match = re.fullmatch(obsPattern, filename)

            if match:
                print(node, year, month, match.groups())
                with fits.open(filepath) as hdul:
                    if len(hdul) == 0:
                        print("{0:s} has no primary HDU.".format(filepath))
                    header = hdul[0].header

                date_obs = header['DATE-OBS']  # this is already in UTC time
                exptime = header['EXPTIME']
                RA_center = header['CRVAL1']

                time_utc_string = date_obs + "+00:00"

                entry = (node, time_utc_string, exptime, RA_center,
                         str(filepath.resolve()))
                samples.append(entry)

        c.executemany('INSERT INTO masndata VALUES (?,?,?,?,?)',
                      samples)

    def _setupObs_v2(self, c, node, year, month, obsdir, obsPattern):

        samples = []
        
        loc = self.nodeData[node]['loc']

        for filepath in obsdir.iterdir():
            if not filepath.is_file():
                continue

            filename = filepath.name

            match = re.fullmatch(obsPattern, filename)

            if match:
                print(node, year, month, match.groups())
                with fits.open(filepath) as hdul:
                    if len(hdul) == 0:
                        print("{0:s} has no primary HDU.".format(filepath))
                    header = hdul[0].header

                date_loc = header['DATE-OBS']
                time_loc = header['TIME-OBS']
                exptime = header['EXPTIME']

                time_str = date_loc + 'T' + time_loc
                time = Time(time_str, location=loc)

                zenith = coordinates.AltAz(alt=0.0*u.deg, az=0.0*u.deg,
                                           obstime=time, location=loc)
                zenith_icrs = zenith.transform_to(coordinates.ICRS)

                samples.append((node, time.to_value('isot'), exptime,
                                zenith_icrs.ra, str(filepath.resolve())))

        c.executemany('INSERT INTO masndata VALUES (?,?,?,?,?)',
                      samples)
