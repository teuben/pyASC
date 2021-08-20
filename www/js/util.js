const FILE_REGEX = /\w+\d+-(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})(?:-(\d{3,})(\w?))?/;

const MAX_VAL = 65535;
const POOR_LIM = MAX_VAL * (1/3);
const MEDIUM_LIM = MAX_VAL * (2/3);
const GOOD_LIM = MAX_VAL * (3/3);

function filenameToDate(name, asMoment) {
    let m = name.match(FILE_REGEX).slice(1);
    let isoDate = `${m[0]}-${m[1]}-${m[2]}T${m[3]}:${m[4]}:${m[5]}${m[6] ? `,${m[6]}${m[7]}` : ''}`;
    let isUTC = name.indexOf('Z') !== -1;
    let date = (isUTC ? moment.utc(isoDate) : moment(isoDate)).utc();
    return asMoment ? date : date.toDate();
}

function dateToPath(date) {
    console.log(dateToPath);
}

function updateSkymap(currentFile) {
    let latitude = 39.0021;
    let longitude = -76.956;
    
    let date = filenameToDate(currentFile);

    $('#filetime').text(date.toString());
    console.log(date);

    let header = JS9.GetImageData(true).header;
    if (header['SITE-LAT']) latitude = header['SITE-LAT'];
    if (header['SITE-LONG']) longitude = header['SITE-LONG'];
    if (header['DATE-OBS']) moment.utc(header['DATE-OBS']);

    $('#skymap').show();

    if ($('#skymap canvas').length === 0) {
        Celestial.display({
            width: $(window).width() / 2.7,
            container: 'skymap',
            projection: 'airy',
            form: false,
            interactive: true,
            stars: {
                limit: 4
            },
            datapath: '/js/lib/celestial0.6/data',
            daylight: {
                show: true
            },
            planets: {
                show: true
            },
            controls: false
        });
    }

    Celestial.skyview({
        date: date,
        location: [latitude, longitude],
        timezone: 0
    });

    $('#skymap').height($('#skymap canvas').height());
}