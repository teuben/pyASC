let BASE_DIR = '/masn01-archive/';
const TAG_OPTIONS = ['meteor', 'cloud', 'bug', 'misc'];

let CURR_DIR = null;
let CURR_FILES = null;

let INIT_CMAP = null;
let CURR_IDX = 0;
let PREV_IDX = null;

$(async function() {
    let cameras = JSON.parse(await $.get('cameras.php'));
    cameras.forEach((camera) => {
        $('#masn-switch').append(`<option value='${camera}/'>${camera}</option>`);
    });
    BASE_DIR = $('#masn-switch').val();

    JS9.ResizeDisplay(750, 750);

    TAG_OPTIONS.forEach(tag => $('#tag-select').append(`<option value='${tag}'>${tag}</option>`));

    $('#datepicker').prop('disabled', true);

    let result = await $.get(BASE_DIR);
    let years = getDirectories(result, /\d{4}/);

    console.log(years);

    new Pikaday({ 
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
            $('#tag-select')[0].selectedIndex = 0;
            $('#tag-modal').show();
        } else if (selectedRegions.length > 1) {
            alert('Please select only one region.');
        } else {
            alert('Please select a region.');
        }
    });

    $('#tag-select').change(function(evt) {
        let tag = $(this).val();
        if (tag.trim() != '') {
            JS9.ChangeRegions('selected', { text: tag, data: { tag: tag } });
            saveCurrentRegions();
        }
        $('#tag-modal').hide();
    });

    $('#action-reset').click(function() {
        if (INIT_CMAP == null) return;
        JS9.SetColormap(INIT_CMAP.colormap, INIT_CMAP.contrast, INIT_CMAP.bias);
    });

    $('#action-save').click(function() {
        saveCurrentRegions();
        alert('All changes saved.');
    });

    $('#action-info').click(function() {
        $('#info-modal').show();
    });

    $('.modal-close').click(function() {
        $('.modal').hide();
    });

    $(window).keydown(function(evt) {
        if (evt.which === 8 && JS9.GetImageData(true)) saveCurrentRegions();
        if (evt.which === 27) $('.modal').hide();
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
            let fileData = JSON.parse(await $.get({
                    url: 'regions.php',
                    cache: false
                }, {
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
            if (JS9.GetFlip() === 'none') JS9.SetFlip('x');

            CENTER_PAN = JS9.GetPan();
            INIT_CMAP = JS9.GetColormap();

            console.log(CENTER_PAN);
            $('#viewer-container').show();
            $('#actions').show();

            $('#filename').text(`${currentFile} (${CURR_IDX + 1}/${CURR_FILES.length})`);
            $('#filetime').show();

            updateSkymap(currentFile);
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
    $.get({
        url: 'regions.php',
        cache: false
    }, {
        action: 'update',
        path: CURR_FILES[CURR_IDX],
        tags: tags.join(','),
        params: JSON.stringify(regions)
    }).then(response => {
        if (response.trim() !== '') {
            alert(`Error saving regions: ${response}`);
        }
    });
}
