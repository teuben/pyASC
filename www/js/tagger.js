const BASE_DIR = '/masn01-archive/';

let CURR_DIR = null;
let CURR_FILES = null;

let INIT_CMAP = null;
let CURR_IDX = 0;
let PREV_IDX = null;

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
        let selectedRegions = JS9.GetRegions('selected');
        if (selectedRegions.length === 1) {
            let tag = prompt('What should the tag be for this region?');
            JS9.ChangeRegions('selected', { text: tag, data: { tag: tag } });
            saveCurrentRegions();
        } else if (selectedRegions.length > 1) {
            alert('Please select only one region.');
        } else {
            alert('Please select a region.');
        }
    });

    $('#action-reset').click(function() {
        if (INIT_CMAP == null) return;
        JS9.SetColormap(INIT_CMAP.colormap, INIT_CMAP.contrast, INIT_CMAP.bias);
    });

    $('#action-save').click(function() {
        saveCurrentRegions();
    });

    $(window).keydown(function(evt) {
        if (evt.which === 8 && JS9.GetImageData(true)) saveCurrentRegions();
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
    if (PREV_IDX == CURR_IDX) return;
    if (CURR_FILES == null) return;

    PREV_IDX = CURR_IDX;
    let currentFile = CURR_FILES[CURR_IDX];
    let currPath = `${CURR_DIR}/${currentFile}`;

    JS9.CloseImage();
    
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
        onload: async function() {
            let fileData = JSON.parse(await $.get('regions.php', {
                action: 'list',
                path: currentFile
            }));
            
            if (Object.keys(fileData).length > 0) {
                fileData.params = JSON.parse(fileData.params);
                fileData.params.map(region => {
                    if (region.data.tag) region.text = region.data.tag;
                    return region;
                });
                JS9.AddRegions(fileData.params);
            }

            JS9.SetZoom('ToFit');
            JS9.SetFlip('x');

            CENTER_PAN = JS9.GetPan();
            INIT_CMAP = JS9.GetColormap();

            console.log(CENTER_PAN);
            $('#viewer-container').show();
            $('#actions').show();

            $('#filename').text(`${currentFile} (${CURR_IDX + 1}/${CURR_FILES.length})`);
            $('#filetime').show();

            let latitude = 39.0021;
            let longitude = -76.956;
            
            let m = currentFile.match(FILE_REGEX).slice(1);
            let isoDate = `${m[0]}-${m[1]}-${m[2]}T${m[3]}:${m[4]}:${m[5]}${m[6] ? `,${m[6]}${m[7]}` : ''}`;
            let isUTC = currentFile.indexOf('Z') !== -1;
            let date = (isUTC ? moment.utc(isoDate) : moment(isoDate)).utc().toDate();

            $('#filetime').text(date.toString());

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
    
    PREV_IDX = null;
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
        $('#filetime').hide();
        $('#viewer-container').hide();
        $('#actions').hide();
    }
}

function saveCurrentRegions() {
    let regions = JS9.GetRegions('all');
    let tags = JS9.GetRegions('all').map(region => region.data ? region.data.tag : null).filter(tag => tag != null);
    $.get('regions.php', {
        action: 'update',
        path: CURR_FILES[CURR_IDX],
        tags: tags.join(','),
        params: JSON.stringify(regions)
    }).then(response => console.log(response));
}
