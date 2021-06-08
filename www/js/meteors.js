var CURRENT_PATH = '';
var FILESYSTEM = {};

function parseDirectoryListing(data, pathFilter) {
    // Scrape directory listing for files
    var parser = new DOMParser();
    var root = parser.parseFromString(data, 'text/html');
    
    var links = [].slice.call(root.getElementsByTagName('a'));
    var hrefs = links.map(item => item.href); console.log(hrefs);
    
    var regex = new RegExp('(.+)\/(' + pathFilter + ')\/(.+)\/$');
    var dirs = hrefs.filter(href => href.match(regex));
    var matches = dirs.map(dir => dir.match(regex)[3]);
    
    return [dirs, matches];
}

function renderBreadcrumbs(path) {
    var components = path.split('/').filter(c => c != '');
    $('ol.breadcrumb').empty();
    $('ol.breadcrumb').append('<li class="breadcrumb-item"><a href="#" onclick="renderPath(\'\')">Home</a></li>');
    components.forEach((component, idx) => {
        $('ol.breadcrumb').append(`<li class="breadcrumb-item"><a href="#" onclick="renderPath('${components.slice(0, idx + 1).join('/')}')">${component}</a></li>`);
    });
    $('ol.breadcrumb li').last().addClass('active');
    $('ol.breadcrumb > li > a').last().contents().unwrap();
}

function renderPath(path) {
    var components = path.split('/').filter(c => c != '');
    renderBreadcrumbs(path);

    var currentPoint = FILESYSTEM;
    components.forEach(component => {
        console.log('browsing to ' + component);
        currentPoint = currentPoint[component];
    });

    var elements = currentPoint.length ? currentPoint : Object.keys(currentPoint);
    
    $('#browser-cards').empty();
    elements.forEach((element, idx) => {
        if (idx % 5 == 0) $('#browser-cards').append(`<div class='row justify-content-start'></div>`);

        $('#browser-cards .row').last().append(`
            <div class='col'>
                <div class="card" style="width: 18rem;" onclick="renderPath('${path}/${element}')">
                    <div class="card-body">
                        <p class="card-text">${element}</p>
                    </div>
                </div>
            </div>
        `);
    });
}

$(function() {
    // Fetch stored months from directory listing
    $.get('/masn01-archive/', function(data) {
        var dirData = parseDirectoryListing(data, 'masn01-archive');
        var months = dirData[1];
        
        // Store each month in filesystem object
        months.forEach(month => {
            let y = month.substring(0, 4);
            let m = month.substring(4, 6);
            if (!FILESYSTEM[y]) FILESYSTEM[y] = {};
            if (!FILESYSTEM[y][m]) FILESYSTEM[y][m] = [];
        });

        // Fetch stored days for each available month
        var monthPromises = months.map(dir => $.get('/masn01-archive/' + dir));
        Promise.all(monthPromises).then(monthListings => {
            monthListings.forEach((monthDir, idx) => {
                // Iterate over each stored day in each month
                let currentMonth = months[idx];
                let monthData = parseDirectoryListing(monthDir, 'masn01-archive\/' + currentMonth);
                
                let y = currentMonth.substring(0, 4);
                let m = currentMonth.substring(4, 6);
                let days = monthData[1].map(day => day.substring(6, 8));

                FILESYSTEM[y][m] = days;
            });

            renderPath('');
        });
    });
});