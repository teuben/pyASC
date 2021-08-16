const BASE_DIR = '/masn01-archive/';

let CURR_DIR = null;
let CURR_FILES = null;
let CURR_IDX = 0;

const MAX_VAL = 65535;
const POOR_LIM = MAX_VAL * (1/3);
const MEDIUM_LIM = MAX_VAL * (2/3);
const GOOD_LIM = MAX_VAL * (3/3);

const FILE_REGEX = /\w+\d+-(\d{4})-(\d{2})-(\d{2})T(\d{2})-(\d{2})-(\d{2})(?:-(\d{3,})(\w?))?/;

$(async function() {
    $('#datepicker').prop('disabled', true);

    let result = await $.get(BASE_DIR);
    let years = getDirectories(result, /\d{4}/);

    console.log(years);

    let picker = new Pikaday({ 
        field: document.getElementById('datepicker'),
        format: 'YYYY-MM-DD',
        minDate: moment(`${years[0]}-01-01`, 'YYYY-MM-DD').toDate(),
        maxDate: moment(`${years[years.length-1]}-12-31`, 'YYYY-MM-DD').toDate(),
        defaultDate: moment(`2018-11-20`).toDate(),
        onSelect: renderDate,
        onDraw: async function(evt) {
            let { year, month } = evt.calendars[0];

            let { tabs, days } = await $.get(`stats.php?y=${year}&m=${String(month + 1).padStart(2, '0')}`);

            let renderedDays = $('.pika-lendar tbody td').filter('[data-day]');
            renderedDays.each((_, elem) => {
                let dateStr = moment({
                    day: $(elem).data('day'),
                    month: month,
                    year: year
                }).format('YYYY-MM-DD');

                if (days.indexOf(dateStr) !== -1) {
                    let dateTab = tabs[days.indexOf(dateStr)];
                    $(elem).attr('data-tab', dateTab);
                    if (0 <= dateTab && dateTab < POOR_LIM) $(elem).addClass('day-poor');
                    else if (POOR_LIM <= dateTab && dateTab < MEDIUM_LIM) $(elem).addClass('day-medium');
                    else if (MEDIUM_LIM <= dateTab && dateTab < GOOD_LIM) $(elem).addClass('day-good');
                }
            });
        }
    });
    
    $('#datepicker').prop('disabled', false);

    $('#fileprev').click(function() {
        if (CURR_FILES == null) return;
        CURR_IDX = CURR_IDX - 1 < 0 ? CURR_FILES.length - 1 : CURR_IDX - 1;
        $('#slider').slider('value', CURR_IDX + 1);
        renderCurrentFile();
    });

    $('#filenext').click(function() {
        if (CURR_FILES == null) return;
        CURR_IDX = CURR_IDX + 1 >= CURR_FILES.length - 1 ? 0 : CURR_IDX + 1;
        $('#slider').slider('value', CURR_IDX + 1);
        renderCurrentFile();
    });

    $('#action-tag').click(function() {
        $('#action-tag').toggleClass('active');
        $('#tag-overlay, .tag-toggle').toggle();
        if ($('#action-tag').hasClass('active')) {
            JS9.SetZoom('ToFit');
            JS9.SetPan({ x: CENTER_PAN.ox, y: CENTER_PAN.oy });
        }
    });

    $('#tag-overlay, .tag-toggle').mousedown(evt => {
        evt.stopPropagation();
    });
});

function createSlider() {
    let handle = $('#fits-handle');
    handle.text(1);
    $('#slider').slider({
        value: 1,
        min: 1,
        max: CURR_FILES.length,
        change: function(evt, ui) {
            handle.text(ui.value);
            CURR_IDX = ui.value - 1;
            renderCurrentFile();
        },
        slide: function(evt, ui) {
            handle.text(ui.value);
        }
    });
}

function getDirectories(html, regex) {
    let parser = new DOMParser();
    let root = parser.parseFromString(html, 'text/html');
    let links = [].slice.call(root.getElementsByTagName('a'));
    let hrefs = links.map(link => {
        let directory = link.href.endsWith('/');
        let dest = (directory ? link.href.slice(0, -1) : link.href).split('/').pop();
        return dest.match(regex) ? dest : null;
    }).filter(e => e != null);
    return hrefs;
}

function renderCurrentFile() {
    if (CURR_FILES == null) return;

    let currentFile = CURR_FILES[CURR_IDX];
    let currPath = `${CURR_DIR}/${currentFile}`;
    
    PREV_ZOOM = null;
    PREV_PAN = null;

    $('.JS9PluginContainer').each((idx, elem) => {
        if($(elem).find('.tag-toggle, #tag-overlay').length === 0) {
            $(elem).append(`<div class='tag-toggle'></div>`);
        }
    });
    JS9.globalOpts.menuBar = ['scale'];
    JS9.globalOpts.toolBar = ['box', 'circle', 'ellipse', 'zoom+', 'zoom-', 'zoomtofit'];
    
    JS9.SetToolbar('init');
    JS9.Load(currPath, { 
        zoom: 'ToFit', 
        onload: function() {
            JS9.SetZoom('ToFit');
            JS9.SetFlip('x');

            CENTER_PAN = JS9.GetPan();
            console.log(CENTER_PAN);
            $('#viewer-container').show();
            $('#actions').show();
            $('#filename').text(`${currentFile} (${CURR_IDX + 1}/${CURR_FILES.length})`);

            let latitude = 39.0021;
            let longitude = -76.956;
            
            let m = currentFile.match(FILE_REGEX).slice(1);
            let isoDate = `${m[0]}-${m[1]}-${m[2]}T${m[3]}:${m[4]}:${m[5]}${m[6] ? `,${m[6]}${m[7]}` : ''}`;
            let isUTC = currentFile.indexOf('Z') !== -1;
            let date = (isUTC ? moment.utc(isoDate) : moment(isoDate)).utc().toDate();

            let header = JS9.GetImageData(true).header;
            if (header['SITE-LAT']) latitude = header['SITE-LAT'];
            if (header['SITE-LONG']) longitude = header['SITE-LONG'];
            if (header['DATE-OBS']) moment.utc(header['DATE-OBS']);

            $('#skymap').show();

            if ($('#skymap canvas').length === 0) {
                Celestial.display({
                    width: $(window).width() / 2.4,
                    container: 'skymap',
                    projection: 'airy',
                    form: false,
                    interactive: true,
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
    });
}

async function renderDate(date) {
    $('#filename').text('Loading...');
            
    let dateStr = moment(date).format('YYYY-MM-DD');

    let yearDir = dateStr.substring(0, 4);
    let monthDir = dateStr.substring(0, 7);
    
    let parentDir = `${BASE_DIR}${yearDir}/${monthDir}/${dateStr}`
    
    let list;
    try {
        list = await $.get(parentDir);
    } catch (error) {
        list = null;
    }
    
    let entries = getDirectories(list, /\.fits?/);
    console.log(entries);
    
    CURR_IDX = 0;
    CURR_DIR = parentDir;
    CURR_FILES = entries;

    if (list) {
        $('#skytab').show().attr('src', `${parentDir}/sky.tab.thumb.png`);
        createSlider();
        renderCurrentFile();
    } else {
        $('#skytab').hide();
        $('#filename').text('No data.');
        $('#viewer-container').hide();
        $('#actions').hide();
    }
}
