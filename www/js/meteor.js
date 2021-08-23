let FILES = [];
let CURR_IDX = 0;
let FILTER_TAG = 'meteor';

$(async function() {
    try {
        let config = await $.get('/config.json');
        
        let tags = config['image-tags'];
        FILTER_TAG = tags[0];
        tags.forEach(tag => {
            $('#tag-select').append(`<option value=${tag}>${tag}</option>`);
        });

        $('#tag-select').change(function() {
            FILTER_TAG = $('#tag-select').val();
            init();
        });
    } catch (err) {
        console.log(`Getting config failed: ${err.statusText} (${err.status})`);
        console.log('Using default.');
        $('#tag-select').hide();
    }

    $(document).on('JS9:ready', function() {
        init();
    });
});

async function init() {
    FILES = [];
    CURR_IDX = 0;
    let tagged = JSON.parse(await $.get({
        url: `/tagger/regions.php?action=tag&tag=${FILTER_TAG}`,
        cache: false
    }));
    console.log(tagged);
    if (tagged.length > 0) {
        $('#tag-none').hide();
        $('#tag-browser').show();

        FILES = tagged.map(data => {
            let { path, params } = data;
            let date = filenameToDate(path, true).local().hour(0).minute(0).second(0).millisecond(0).add(1, 'days');
            console.log(date, date.format('YYYY-MM-DD'));
            let dateStr = date.format('YYYY-MM-DD');
            let cameraNum = path.match(/masn(\d{2})/i)[1];
            return {
                path: `/masn${cameraNum}-archive/${dateStr.substring(0, 4)}/${dateStr.substring(0, 7)}/${dateStr}/${path}`,
                params: params
            };
        });
        renderCurrentFile();
    } else {
        $('#tag-none').show();
        $('#tag-browser').hide();
    }
}

function renderCurrentFile() {
    let baseFile = FILES[CURR_IDX].path.split('/').pop();
    $('#js9-filename').text(`${baseFile} (${CURR_IDX + 1}/${FILES.length})`);
    JS9.Load(FILES[CURR_IDX].path, { 
        scale: "linear",
        zoom: "tofit",
        onload: function() {
            $('#js9-loading').hide();
            $('#js9-viewer').show();
            JS9.SetZoom('tofit');
            if (JS9.GetFlip() === 'none') JS9.SetFlip('x')
            updateSkymap(baseFile);
            renderRegions(FILES[CURR_IDX].params);
        }
    });
}

function renderDeltaFITS(delta) {
    CURR_IDX += delta;
    if (CURR_IDX < 0) CURR_IDX = FILES.length - 1;
    else if (CURR_IDX >= FILES.length) CURR_IDX = 0;
    renderCurrentFile();
}

function renderRegions(params) {
    let regions = JSON.parse(params);
    JS9.AddRegions(regions.filter(region => region.data && region.data.tag.toLowerCase() === FILTER_TAG.toLowerCase()));
}
