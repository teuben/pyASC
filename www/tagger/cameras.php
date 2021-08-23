<?php
    $config = json_decode(`cat ../config.json`, true);

    $cameras = preg_split("/\r\n|\n|\r/", trim(shell_exec(sprintf("ls ../ | grep -P '%s'", $config['directory-regex']))));
    $cameras = array_map(function ($str) {
        return '/' . $str;
    }, $cameras);

    echo json_encode($cameras);
?>