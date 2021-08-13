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
    JS9.Load(currPath, { zoom: 'ToFit' });
    CENTER_PAN = JS9.GetPan();
    
    $('#js9-viewer').show();
    $('#actions').show();
    $('#filename').text(`${currentFile} (${CURR_IDX + 1}/${CURR_FILES.length})`);
}

let CURR_DIR = null;
let CURR_FILES = null;
let CURR_IDX = 0;

let CENTER_PAN = null;
let PREV_ZOOM = null;
let PREV_PAN = null;

$(async function() {
    const BASE_DIR = 'http://localhost:8010/proxy/masn01-archive/';

    $('#datepicker').prop('disabled', true);

    let result = await $.get(BASE_DIR);
    let years = getDirectories(result, /\d{4}/);
    let months = await Promise.all(years.map(async function(year) {
        let list = await $.get(`${BASE_DIR}${year}`);
        return getDirectories(list, /\d{4}-\d{2}/);
    }));
    months = [].concat(...months);
    console.log(months);
    let days = await Promise.all(months.map(async function(month) {
        let list = await $.get(`${BASE_DIR}${month.substring(0, 4)}/${month}`);
        return getDirectories(list, /\d{4}-\d{2}-\d{2}/);
    }));
    days = [].concat(...days);

    console.log(days);

    let picker = new Pikaday({ 
        field: document.getElementById('datepicker'),
        format: 'YYYY-MM-DD',
        minDate: new Date(days[0]),
        maxDate: new Date(days[days.length - 1]),
        disableDayFn: function(date) {
            return days.indexOf(moment(date.toString()).format('YYYY-MM-DD')) === -1;
        },
        onSelect: async function(date) {
            $('#filename').text('Loading...');
            
            let dateStr = moment(date).format('YYYY-MM-DD');

            let yearDir = dateStr.substring(0, 4);
            let monthDir = dateStr.substring(0, 7);
            
            let parentDir = `${BASE_DIR}${yearDir}/${monthDir}/${dateStr}`
            let list = await $.get(parentDir);
            
            let entries = getDirectories(list, /\.fits?/);
            console.log(entries);
            
            CURR_IDX = 0;
            CURR_DIR = parentDir;
            CURR_FILES = entries;

            $('#skytab').show().attr('src', `${parentDir}/sky.tab.thumb.png`);

            renderCurrentFile();
        }
    });
    
    $('#datepicker').prop('disabled', false);

    $('#fileprev').click(function() {
        if (CURR_FILES == null) return;
        CURR_IDX = CURR_IDX - 1 < 0 ? CURR_FILES.length - 1 : CURR_IDX - 1;
        renderCurrentFile();
    });

    $('#filenext').click(function() {
        if (CURR_FILES == null) return;
        CURR_IDX = CURR_IDX + 1 >= CURR_FILES.length - 1 ? 0 : CURR_IDX + 1;
        renderCurrentFile();
    });

    $('#action-tag').click(function() {
        $('#action-tag').toggleClass('active');
        $('#tag-overlay, .tag-toggle').toggle();
        if ($('#action-tag').hasClass('active')) {
            PREV_ZOOM = JS9.GetZoom();
            PREV_PAN = JS9.GetPan();
            
        } else {

        }
    });

    $('#tag-overlay, .tag-toggle').mousedown(evt => {
        evt.stopPropagation();
    });
});
