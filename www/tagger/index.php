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

    <script type="text/javascript">
        <?php
            function quotes($str) {
                return $str == null ? 'null' : "`" . $str . "`";
            }

            function tabavg($dir) {
                $tabfile = fopen($dir . '/sky.tab', 'r');
                if ($tabfile) {
                    $tab = '';
                    while (!feof($tabfile)) {
                        $tab .= fread($tabfile, 8192);
                    }
                    fclose($tabfile);
                    $lines = preg_split("/\r\n|\n|\r/", trim($tab));
                    $visibilities = array_map(function($line) {
                        return explode(' ', $line)[1];
                    }, $lines);
                    if (count($visibilities) == 0) return 0;
                    return 65535 - (array_sum($visibilities) / count($visibilities));
                } else {
                    return null;
                }
            }

            chdir('../masn01-archive');
            
            $dirs = `find . -maxdepth 3 -type d | grep -P '(\d{4}-\d{2}-\d{2})'`;
            $tabs = array_map('tabavg', preg_split("/\r\n|\n|\r/", trim($dirs)));
            echo 'const TABS = [' . implode(',', $tabs) . '];';

            $dayDirs = `find . -maxdepth 3 -type d | grep -oP '(\d{4}-\d{2}-\d{2})'`;
            $days = array_map('quotes', preg_split("/\r\n|\n|\r/", trim($dayDirs)));
            echo 'const DAYS = [' . implode(',', $days) . '];';
        ?>
    </script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
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
    </div>
    <div id="actions" style="display: none">
        <i id="action-tag" class="fas fa-tag"></i>
        <i id="action-save" class="fas fa-save"></i>
        <i id="action-info" class="fas fa-question-circle"></i>
    </div>
    <div id="js9-viewer" style="display: none">
        <div class="JS9Menubar"></div>
        <div class="JS9Toolbar"></div>
        <div class="JS9">
            <div id="tag-overlay">
                <span id="tag-text">Tagging On</span>
            </div>
        </div>
        <div class="JS9Statusbar"></div>
    </div>
</body>

</html>