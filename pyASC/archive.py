from pathlib import Path
import re
import sqlite3
import datetime
import numpy as np
import astropy.coordinates as coordinates
import astropy.io.fits as fits
import astropy.units as u
from astropy.time import Time

class Archive:

    nodePattern = r"MASN-([0-9]{2})"
    yearmonthPattern = r"([0-9]{4})([01][0-9])"
    dayPattern1 = r"([0-9]{4})([01][0-9])([0-3][0-9])"
    obsPattern1 = r"IMG([0-9]{5}).FIT"
    dayPattern2 = (r"([0-9]{4})-([01][0-9])-([0-3][0-9]) to "
                   r"([0-9]{4})-([01][0-9])-([0-3][0-9])")
    obsPattern2 = (r"MASN([0-9]{2})-([0-9]{4})-([0-9]{2})-([0-9]{2})"
                   r"T([0-9]{2})-([0-9]{2})-([0-9]{2})-([0-9]{3})Z.fits")
    
    nodeData = {1: {'lat': 39.0021*u.deg, 'lon': -76.956*u.deg}}


    def __init__(self, dataPath, dbFilename):
        self.dbFilename = Path(dbFilename)
        self.rootdir = Path(dataPath)
        self.nodes = []
        self._setup()

    def __repr__(self):
        return "Archive(rootdir={0:s}, db={1:s})".format(repr(self.rootdir),
                                                         repr(self.dbFilename))

    def getFITSByDate(self, yyyymmdd, c=None):

        if c is None:
            conn = sqlite3.connect(self.dbFilename)
            c = conn.cursor()

        c.execute('SELECT fitsfile from masndata where obsdate=?',
                  (yyyymmdd, ))
        file_list = np.array([result[0] for result in c])

        return np.array(file_list)



    def _setup(self):

        conn = sqlite3.connect(self.dbFilename)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS masndata
                     (node INT, obsdate TEXT, obstime TEXT, exptime REAL,
                      ra_zenith REAL, fitsfile TEXT)''')

        conn.commit()

        for nodedir in self.rootdir.iterdir():
            if nodedir.is_dir():
                match = re.fullmatch(self.nodePattern, nodedir.name)
                if match:
                    node = int(match.group(1))
                    self.nodes.append(node)
                    self._setupNode(c, node, nodedir)
        
        conn.commit()
        
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
                match = re.fullmatch(self.dayPattern2, obsdir.name)
                if match:
                    day = int(match.group(6))
                    self._setupDay(c, node, year, month, day, obsdir,
                                   self.obsPattern2,
                                   self._generate_db_entry_v2)
                """
                else:
                    match = re.fullmatch(self.dayPattern1, obsdir.name)
                    if match:
                        day = int(match.group(3))
                        self._setupDay(c, node, year, month, day, obsdir,
                                       self.obsPattern1,
                                       self._generate_db_entry_v1)
                """

    def _setupDay(self, c, node, year, month, day, obsdir, obsPattern,
                  dbEntryFunc):

        samples = []

        yyyymmdd = "{0:04d}{1:02d}{2:02d}".format(year, month, day)

        known_files = self.getFITSByDate(yyyymmdd, c)

        for filepath in obsdir.iterdir():
            if not filepath.is_file():
                continue

            filename = filepath.name

            match = re.fullmatch(obsPattern, filename)

            if match:
    
                if (len(known_files) > 0 and 
                        (str(filepath.resolve()) == known_files).any()):
                    continue

                print(node, yyyymmdd, match.groups())

                entry = dbEntryFunc(node, yyyymmdd, filepath)
                samples.append(entry)

        c.executemany('INSERT INTO masndata VALUES (?,?,?,?,?,?)',
                      samples)

    def _generate_db_entry_v2(self, node, yyyymmdd, filepath):

        with fits.open(filepath) as hdul:
            if len(hdul) == 0:
                print("{0:s} has no primary HDU.".format(filepath))
            header = hdul[0].header


        date_obs = header['DATE-OBS']  # this is already in UTC time
        exptime = header['EXPTIME']
        RA_center = header['CRVAL1']

        time_utc_string = date_obs + "+00:00"

        entry = (node, yyyymmdd, time_utc_string, exptime, RA_center,
                 str(filepath.resolve()))

        return entry

    def _generate_db_entry_v1(self, node, yyyymmdd, filepath):

        with fits.open(filepath) as hdul:
            if len(hdul) == 0:
                print("{0:s} has no primary HDU.".format(filepath))
            header = hdul[0].header

        date_loc = header['DATE-OBS']
        time_loc = header['TIME-OBS']
        exptime = header['EXPTIME']

        time_str = date_loc + 'T' + time_loc + "-05:00"
        time = Time(time_str, format='isot', scale='utc',
                    location=self.nodeData[node]['loc'])

        zenith = coordinates.AltAz(alt=0.0*u.deg, az=0.0*u.deg,
                                   obstime=time,
                                   location=self.nodeData[node]['loc'])
        zenith_icrs = zenith.transform_to(coordinates.ICRS)

        entry = (node, yyyymmdd, time.to_value('isot'), exptime,
                 zenith_icrs.ra, str(filepath.resolve()))

        return entry
