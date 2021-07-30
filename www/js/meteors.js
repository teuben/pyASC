var CAMERAS = ['/masn01-archive', '/masn02-archive'] // edit this for more camera options (name of symlink directory)
var FILESYSTEM = {};

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
        let cards = $('#browser-cards .card').length;
        let idx = moduloSum(getActiveCardIndex(), delta, cards);
        $($('#browser-cards .card')[idx]).click();
    }
}

function renderFITS(path, elem) {
    console.log(elem);
    console.log('rendering ' + path);

    $('#browser-cards .card').removeData('active');
    $(elem).data('active', true);

    $('#js9-viewer').hide();
    $('#js9-loading').show();
    $('#js9-modal').fadeIn();

    $('#js9-filename').text(path);
    
    JS9.Load(path, { 
        bias: 0.945313,
        contrast: 3.96484375,
        scale: "log",
        scalemin: "158",
        scalemax: "62017",
        zoom: 0.5,
        onload: function() {
            $('#js9-loading').hide();
            $('#js9-viewer').show();
        }
    });
}

async function renderPath(path) {
    renderBreadcrumbs(path);

    $('#browser-cards').empty();
    $('#browser-cards').append('<h6>Loading...</h6>')

    let elements = await parseDirectoryListing(path);
    $('#browser-cards').empty();
    elements.forEach(async function(element, idx) {
        if (idx % 4 == 0) $('#browser-cards').append(`<div class='row justify-content-start'></div>`);

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

        $('#browser-cards .row').last().append(`
            <div class='col-2'>
                <div class="card" onclick="${action}">
                    <div class="card-body">
                        <p class="card-text">
                            ${elemTxt}
                            ${hasThumb ? `<img class='thumbnail' src='${elemPath}/sky.tab.thumb.png' />` : ''}
                        </p>
                    </div>
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

$(function() {
    CAMERAS.forEach((camera, idx) => {
        $('#masn-switch').append(`<option value='${camera}' ${idx == 0 ? 'selected' : ''}>${camera}</option>`);
    });

        // Hide modal in beginning
    $('#js9-modal').hide();

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

    renderPath($('#masn-switch').val());
    $('#masn-switch').change(evt => {
        renderPath($('#masn-switch').val());
    });
});