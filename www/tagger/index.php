<html>

<head>
    <title>Object Tagger</title>
    
    <link rel="stylesheet" href="../css-n-inc/tagger.css" />
	<link type="text/css" rel="stylesheet" href="/js/lib/js9-3.5/js9support.css">
	<link type="text/css" rel="stylesheet" href="/js/lib/js9-3.5/js9.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans&display=swap" rel="stylesheet">
    <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/pikaday/css/pikaday.css">
    <link rel="stylesheet" type="text/css" href="https://code.jquery.com/ui/1.12.1/themes/redmond/jquery-ui.css" />
    <link rel="stylesheet" href="/js/lib/celestial0.6/celestial.css">

    <script type="text/javascript" src="/js/lib/celestial0.6/lib/d3.min.js"></script>
    <script type="text/javascript" src="/js/lib/celestial0.6/lib/d3.geo.projection.min.js"></script>
    <script type="text/javascript" src="/js/lib/celestial0.6/celestial.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/pikaday/pikaday.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.1/moment.min.js"></script>
    <script type="text/javascript" src="/js/lib/js9-3.5/js9prefs.js"></script>
    <script type="text/javascript" src="/js/lib/js9-3.5/js9support.min.js"></script>
    <script type="text/javascript" src="/js/lib/js9-3.5/js9.min.js"></script>
    <script type="text/javascript" src="/js/lib/js9-3.5/js9plugins.js"></script>
    <script src="https://kit.fontawesome.com/446f3e493f.js" crossorigin="anonymous"></script>
    <script src="/js/tagger.js"></script>
</head>

<body>
    <div id="info-modal" style="display: none;">
        <div class="modal-background"></div>
        <div class="modal-body">
            Hi.
        </div>
    </div>
    <div id="header">Object Tagger</div>
    <div id="controls">
        <input type="text" id="datepicker" placeholder="Select date..." autocomplete="off">
        <img id="skytab" height="50" style="display: none" />
    </div>
    <div id="status-bar">
        <div id="status-window">
            <span id="fileprev" class="file-control">&#60;</span>
            <span id="filename">No file selected</span>
            <span id="filenext" class="file-control">&#62;</span>
        </div>
        <div id="filetime" style='display: none'></div>
    </div>
    <div id="actions" style="display: none">
        <div id="slider-container" style="width: 90vw; display: inline-block;">
            <div id="slider">
                <div id="fits-handle" class="ui-slider-handle"></div>
            </div>
        </div>
        <div style="margin: 10px 0px;">
            <i id="action-tag" class="fas fa-tag" title='Tag region'></i>
            <i id="action-save" class="fas fa-save" title='Save changes'></i>
            <i id="action-reset" class="fas fa-palette" title='Reset colormap'></i>
            <i id="action-info" class="fas fa-question-circle" title='Help'></i>
        </div>
    </div>
    <div id="viewer-container" style="display: none">
        <div id="js9-viewer">
            <div class="JS9Menubar"></div>
            <div class="JS9Toolbar"></div>
            <div class="JS9">
            </div>
            <div class="JS9Statusbar"></div>
        </div>
        <div id="skymap" style="display: none" />
    </div>
    <div id="footer">
        Skymaps are rendered using the D3-Celestial Javascript library: <a href='https://github.com/ofrohn/d3-celestial'>https://github.com/ofrohn/d3-celestial</a>
    </div>
</body>

</html>