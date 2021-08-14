<?php
    if (!preg_match("/^\d{4}$/", $_GET['y'])) die('Invalid year query.');
    if (!preg_match("/^\d{2}$/", $_GET['m'])) die('Invalid month query.');

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
            return -1;
        }
    }

    chdir(sprintf('../masn01-archive/%s/%s-%s', $_GET['y'], $_GET['y'], $_GET['m']));

    header('Content-Type: application/json');
    
    $dirs = `find . -maxdepth 3 -type d | grep -P '(\d{4}-\d{2}-\d{2})'`;
    $tabs = array_map('tabavg', preg_split("/\r\n|\n|\r/", trim($dirs)));

    $dayDirs = `find . -maxdepth 3 -type d | grep -oP '(\d{4}-\d{2}-\d{2})'`;
    $days = preg_split("/\r\n|\n|\r/", trim($dayDirs));

    echo json_encode(['tabs' => $tabs, 'days' => $days]);
?>