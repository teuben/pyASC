<?php 
    define('DB_SERVER', '129.2.14.6');
    define('DB_USERNAME', 'obsdatauser');
    define('DB_PASSWORD', 'SNgoB00m');
    define('DB_DATABASE', 'umdastroobs');

    $mysqli = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_DATABASE);

    if ($mysqli->connect_errno) {
        echo("connection error: " + $mysqli->connect_error);
    }
?>
