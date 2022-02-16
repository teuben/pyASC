var FILESYSTEM = {};
let CURR_FILES = [];
let CURR_PATH = null;

function drawIcon(tag) {
    let canvas = $(`canvas[data-tag='${tag}']`)[0].getContext('2d');
    let size = 45;
    let data = getIconData(tag);

    let dark = [35, 74, 125];
    let light = [230, 215, 108];

    for (let i = 0; i < 12; i++) {
        let dataIndex = 11 - i;
        let brightness = data['brightness'][dataIndex] / 65536;

        let shade = [];
        for (let j = 0; j < 3; j++) {
            let min = Math.min(dark[j], light[j]);
            let max = Math.max(dark[j], light[j]);
            shade.push(brightness * (max - min) + min);
        }
        
        canvas.fillStyle = `rgb(${shade.join(',')})`;
        canvas.beginPath();
        canvas.moveTo(size / 2, size / 2);
        canvas.arc(size / 2, size / 2, (size / 2 - 6) * (1 + (brightness / 4)), (2 * Math.PI) - Math.PI / 12 * i, (2 * Math.PI) - Math.PI / 12 * (i + 1), true);
        canvas.lineTo(size / 2, size / 2);
        canvas.fill();
    }

    canvas.fillStyle = `rgb(${dark.join(',')}`;

    canvas.beginPath();
    canvas.arc(size * 0.5, size * 0.75, 5, 0, 2 * Math.PI);
    canvas.fill();
}

function getIconData(tag) {
    let result = {
        brightness: [],
        phase: null,
    };
    
    for (let i = 0; i < 12; i++) {
        result['brightness'].push(Math.floor(Math.random() * 65536));
    }
    result['phase'] = Math.floor(Math.random() * 30);

    return result;
}

function getMonthNum(month) {
    return (new Date(month + ' 1').getMonth()) + 1;
}

function getMonth(num) {
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][num - 1];
}

function getLinkDestination(link) {
    return link.href.endsWith('/') ? link.href.substring(0, link.href.length - 1).split('/').pop() + '/' : link.href.split('/').pop();
}

function parseDirectoryListing(path) {
    return new Promise(resolve => {
        $.get(path).then(data => {
            // Scrape directory listing for files
            var parser = new DOMParser();
            var root = parser.parseFromString(data, 'text/html');
            
            var links = [].slice.call(root.getElementsByTagName('a'));
            var hrefs = links.filter(link => link.innerText.match(/(^(?:(?!\.\.))(.+)(\/|>)$)|(^.+\.fits?$)/gmi)).map(link => getLinkDestination(link));
            
            console.log(links.map(link => getLinkDestination(link)));

            resolve(hrefs);
        });
    });
}

function moduloSum(a, b, m) {
    let i = (a + b) % m;
    if (i < 0) i = i + m;
    return i;
}

function getActiveCardIndex() {
    let result = -1;
    $('#browser-cards .card').filter((idx, elem) => {
        if ($(elem).data('active')) result = idx;
    });
    return result;
}

function renderBreadcrumbs(path) {
    var components = path.split('/').filter(c => c != '');
    $('ol.breadcrumb').empty();
    $('ol.breadcrumb').append('<li class="breadcrumb-item"><a href="#" onclick="renderPath(\'/masn01-archive\')">Home</a></li>');
    components.forEach((component, idx) => {
        $('ol.breadcrumb').append(`<li class="breadcrumb-item"><a href="#" onclick="renderPath('/${components.slice(0, idx + 1).join('/')}')">${component}</a></li>`);
    });
    $('ol.breadcrumb li').last().addClass('active');
    $('ol.breadcrumb > li > a').last().contents().unwrap();
}

function renderDeltaFITS(delta) {
    if ($('#js9-modal').is(':visible')) {
        if ($('#folder-view').is(':visible')) {
            let cards = $('#browser-cards .card').length;
            let idx = moduloSum(getActiveCardIndex(), delta, cards);
            $($('#browser-cards .card')[idx]).click();
        } else {
            CURR_IDX += delta;
            if (CURR_IDX < 0) CURR_IDX = CURR_FILES.length - 1;
            else if (CURR_IDX >= CURR_FILES.length) CURR_IDX = 0;
            renderFITS(`${CURR_PATH}/${CURR_FILES[CURR_IDX]}`, null);
            $('#slider').slider('value', CURR_IDX + 1);
        }
    }
}

function renderFITS(path, elem) {
    console.log(elem);
    console.log('rendering ' + path);

    if (elem) {
        $('#browser-cards .card').removeData('active');
        $(elem).data('active', true);
    }

    $('#js9-viewer').hide();
    $('#js9-loading').show();
    $('#js9-modal').fadeIn();

    $('#js9-filename').text(path);
    
    JS9.Load(path, { 
        scale: "linear",
        zoom: "tofit",
        onload: function() {
            $('#js9-loading').hide();
            $('#js9-viewer').show();
            JS9.SetZoom('tofit');
            if (JS9.GetFlip() === 'none') JS9.SetFlip('x')
            updateSkymap(path.trim().split('/').pop());
        }
    });
}

async function renderPath(path) {
    renderBreadcrumbs(path);

    $('#browser-cards').empty();
    $('#browser-cards').append('<h6>Loading...</h6>')

    let elements = await parseDirectoryListing(path);
    $('#browser-cards').empty();

    // for (var i = 0; i < Math.ceil(elements.length / 4); i++) {
        $('#browser-cards').append(`<div class='row justify-content-start'></div>`);
        // console.log('finished appending row ' + i);
        for (var j = 0; j < elements.length; j++) {
            $('#browser-cards .row').last().append(`<div class='col-2'></div>`);
            console.log('finished appending card ' + j);
        }
    // }

    elements.forEach(async function(element, idx) {
        let separator = path.endsWith('/') ? '' : '/';
        let elemPath = `${path}${separator}${element}`;
        let action = element.toLowerCase().endsWith('.fit') || element.toLowerCase().endsWith('.fits') ? `renderFITS('${elemPath}', this)` : `renderPath('${elemPath}')`;
        let elemTxt = decodeURI(element);

        let hasThumb = null;
        
        try {
            await $.get(`${elemPath}/sky.tab.thumb.png`);
            hasThumb = true;
        } catch (err) {
            hasThumb = false;
        }

        // let targetRow = $('#browser-cards .row')[Math.floor(idx / 4)];
        let targetSpan = $('#browser-cards .row').last().find('.col-2')[4 * Math.floor(idx / 4) + (idx % 4)];

        $(targetSpan).append(`
            <div class="card" onclick="${action}">
                <div class="card-body">
                    <p class="card-text">
                        ${elemTxt}
                        ${hasThumb ? `<img class='thumbnail' src='${elemPath}/sky.tab.thumb.png' />` : ''}
                    </p>
                </div>
            </div>
        `);

        // drawIcon(elemTxt);
        // <canvas class="card-icon" height="45" width="45" data-tag="${elemTxt}"></canvas>
    });
}

function handleThumbHover(evt) {
    if ($('.thumbnail:hover').length > 0) {
        let windowHeight = $(window).height();
        let windowWidth = $(window).width();

        let thumbnail = $('.thumbnail:hover');
        $('#thumbview').attr('src', thumbnail[0].src.replace('.thumb', '')).offset({
            left: windowWidth - evt.pageX < $('#thumbview').width() + 50 ? evt.pageX - ($('#thumbview').width() + 50) : evt.pageX + 50,
            top: windowHeight - evt.pageY < 450 ? evt.pageY - (400 + 50) : evt.pageY + 50,
        }).show();
    } else {
        $('#thumbview').hide();
    }
}

function drawCalendar() {
    new Pikaday({ 
        field: document.getElementById('datepicker'),
        format: 'ddd MMM DD YYYY',
        onSelect: renderDate,
        onDraw: async function(evt) {
            let { year, month } = evt.calendars[0];

            let { tabs, days } = await $.get(`/tagger/stats.php?y=${year}&m=${String(month + 1).padStart(2, '0')}&dir=${BASE_DIR}`);

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
}

function getPath(date) {
    let dateStr = moment(date).format('YYYY-MM-DD');
    let path = `${BASE_DIR}/${dateStr.substring(0, 4)}/${dateStr.substring(0, 7)}/${dateStr}`;
    return path;
}

async function renderDate(date) {
    let path = getPath(date);
    try {
        let listing = await $.get(path);
        $('#slider').show();
        CURR_PATH = path;
        let parser = new DOMParser();
        let dom = parser.parseFromString(listing, 'text/html');
        let links = [].slice.call(dom.getElementsByTagName('a')).filter(link => link.href.match(/\.fits?$/i)).map(link => link.href.split('/').pop());
        CURR_FILES = links;
        createSlider();
        renderFITS(`${path}/${CURR_FILES[$('#slider').slider('value') - 1]}`, null);
    } catch {
        $('#slider').hide();
        alert('No data exists for this date.');
    }
}

function createSlider() {
    let handle = $('#fits-handle');
    handle.text(1);
    $('#slider').slider({
        value: 1,
        min: 1,
        max: 1,
        max: CURR_FILES.length,
        change: function(evt, ui) {
            handle.text(ui.value);
            CURR_IDX = ui.value - 1;
            renderFITS(`${CURR_PATH}/${CURR_FILES[CURR_IDX]}`, null);
        },
        slide: function(evt, ui) {
            handle.text(ui.value);
        }
    });
}

$(async function() {
    let cameras = JSON.parse(await $.get('/tagger/cameras.php'));

    cameras.forEach((camera, idx) => {
        $('#masn-switch').append(`<option value='${camera}' ${idx == 0 ? 'selected' : ''}>${camera}</option>`);
    });

    $('#info-button').click(function() {
        $('#info-modal').fadeIn();
    });

    $('#info-close').click(function() {
        $('#info-modal').fadeOut();
    });

    $('#view-toggle').click(function() {
        $('#toggle-slider').toggleClass('active');
        $('#folder-view').toggle();
        $('#calendar-view').toggle();
        if ($('#toggle-slider').hasClass('active')) $('#view-toggle span').text('Folder View');
        else $('#view-toggle span').text('Calendar View');
    });

    createSlider();

    $('body').append(`<img src='' id='thumbview' style='display: none' />`);

    // Event listeners for closing modal
    $('#js9-close, #js9-backdrop').click(function() {
        $('#js9-modal').fadeOut();
    });

    $(document).keydown(function(evt) {
        if (evt.which === 27) $('#js9-modal').fadeOut();
        if (evt.which === 37) renderDeltaFITS(-1);
        if (evt.which === 39) renderDeltaFITS(1);
    });

    $(document).mousemove(handleThumbHover);

    BASE_DIR = $('#masn-switch').val();
    renderPath($('#masn-switch').val());
    $('#masn-switch').change(evt => {
        BASE_DIR = $('#masn-switch').val();
        renderPath($('#masn-switch').val());
    });

    drawCalendar();
});
