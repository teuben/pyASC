var FILESYSTEM = {};

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

function renderFITS(path) {
    console.log('rendering ' + path)

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
    elements.forEach((element, idx) => {
        if (idx % 4 == 0) $('#browser-cards').append(`<div class='row justify-content-start'></div>`);

        let action = element.toLowerCase().endsWith('.fit') || element.toLowerCase().endsWith('.fits') ? `renderFITS('${path}/${element}')` : `renderPath('${path}/${element}')`;

        $('#browser-cards .row').last().append(`
            <div class='col-3'>
                <div class="card" style="width: 18rem;" onclick="${action}">
                    <div class="card-body">
                        <p class="card-text">${decodeURI(element)}</p>
                    </div>
                </div>
            </div>
        `);
    });
}

$(function() {
    // Hide modal in beginning
    $('#js9-modal').hide();

    // Event listeners for closing modal
    $('#js9-close, #js9-backdrop').click(function() {
        $('#js9-modal').fadeOut();
    });

    $(document).keydown(function(evt) {
        if (evt.which === 27) $('#js9-modal').fadeOut();
    })

    renderPath('/masn01-archive');
});