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

$(function() {
    // Fetch stored months from directory listing
    $.get('/masn01-archive/', function(data) {
        var dirData = parseDirectoryListing(data, 'masn01-archive');
        var months = dirData[1];
        // Fetch stored days for each available month
        var monthPromises = months.map(dir => $.get('/masn01-archive/' + dir));
        Promise.all(monthPromises).then(monthListings => {
            monthListings.forEach((monthDir, idx) => {
                // Iterate over each day folder in each month
                var currentMonth = months[idx];
                $('#link').append(currentMonth + '<br />');
                var monthData = parseDirectoryListing(monthDir, 'masn01-archive\/' + currentMonth);
                monthData[1].forEach(day => $('#link').append('&nbsp;' + day + '<br />'));
            });
        });
    });
});