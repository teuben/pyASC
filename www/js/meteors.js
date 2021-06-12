var FILESYSTEM = {};

function getMonthNum(month) {
    return (new Date(month + ' 1').getMonth()) + 1;
}

function getMonth(num) {
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][num - 1];
}

function parseDirectoryListing(data, pathFilter, fileExt) {
    // Scrape directory listing for files
    var parser = new DOMParser();
    var root = parser.parseFromString(data, 'text/html');
    
    var links = [].slice.call(root.getElementsByTagName('a'));
    var hrefs = links.map(item => item.href.replace('archives', pathFilter)); // console.log(hrefs);

    console.log(hrefs);
    
    var regex = !fileExt ? new RegExp('(.+)\/(' + pathFilter + ')\/(.+)\/$') : new RegExp('(.+)\.' + fileExt + '$');
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

function renderFITS(path) {
    console.log('rendering ' + path)

    $('#js9-viewer').hide();
    $('#js9-loading').show();
    $('#js9-modal').fadeIn();

    let filePath = path.split('/').filter(elem => elem !== '').slice(0, -1);
    console.log(filePath)
    filePath[1] = getMonthNum(filePath[1]).toString();
    if(filePath[1].length == 1) filePath[1] = "0" + filePath[1];

    let dateString = filePath.join('');
    let monthFolder = dateString.substring(0, 6);

    let fullPath = ['/masn01-archive', monthFolder, dateString, path.split('/').pop()].join('/');

    console.log('loading ' + fullPath)

    $('#js9-filename').text(fullPath);
    
    JS9.Load(fullPath, { 
        bias: 0.945313,
        contrast: 3.96484375,
        scale: "linear",
        scalemin: "158",
        scalemax: "62017",
        zoom: 0.5,
        onload: function() {
            $('#js9-loading').hide();
            $('#js9-viewer').show();
        }
    });
}

function renderPath(path) {
    var components = path.split('/').filter(c => c != '');
    renderBreadcrumbs(path);

    var currentPoint = FILESYSTEM;
    components.forEach(component => {
        console.log('browsing to ' + component);
        currentPoint = currentPoint[component];
    });

    $('#browser-cards').empty();
    if (currentPoint === undefined) return;

    var elements = currentPoint.length ? currentPoint : Object.keys(currentPoint);
    elements.forEach((element, idx) => {
        if (idx % 4 == 0) $('#browser-cards').append(`<div class='row justify-content-start'></div>`);

        let action = element.endsWith('.FIT') ? `renderFITS('${path}/${element}')` : `renderPath('${path}/${element}')`;

        $('#browser-cards .row').last().append(`
            <div class='col-3'>
                <div class="card" style="width: 18rem;" onclick="${action}">
                    <div class="card-body">
                        <p class="card-text">${element}</p>
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

    // Fetch stored months from directory listing
    $.get('/masn01-archive/', function(data) {
        var dirData = parseDirectoryListing(data, 'masn01-archive');
        var months = dirData[1];
        
        // Store each month in filesystem object
        months.forEach(month => {
            let y = month.substring(0, 4);
            let m = month.substring(4, 6);
            if (!FILESYSTEM[y]) FILESYSTEM[y] = {};
            if (!FILESYSTEM[y][getMonth(m)]) FILESYSTEM[y][getMonth(m)] = {};
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

                days.forEach(day => FILESYSTEM[y][getMonth(m)][day] = []);

                // Get FITS files under each day
                var dayPromises = monthData[0].map(day => $.get(day));
                Promise.all(dayPromises).then((dayListings) => {
                    dayListings.forEach((dayFiles, idx) => {
                        let dayData = parseDirectoryListing(dayFiles, `masn01-archive/${months[idx]}/${monthData[1][idx]}`, 'FIT');
                        if (dayData[0].length > 0) {
                            let fileNames = dayData[0].map(data => data.split('/').pop());
                            console.log(fileNames);

                            let filePath = dayData[0][0].split('/');
                            filePath.pop();
                            let parentFolder = filePath.pop();
                            console.log(parentFolder);

                            let y = parentFolder.substring(0, 4);
                            let m = parentFolder.substring(4, 6);
                            let d = parentFolder.substring(6, 8);

                            FILESYSTEM[y][getMonth(m)][d] = fileNames;
                        }
                    });
                })
            });

            renderPath('');
        });
    });
});