<?php
    $cameras = preg_split("/\r\n|\n|\r/", trim(`ls ../ | grep -P 'masn.+archive'`));
    $cameras = array_map(function ($str) {
        return '/' . $str;
    }, $cameras);

    echo json_encode($cameras);
?>