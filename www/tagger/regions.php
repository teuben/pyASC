<?php 
    $creds = json_decode(`cat ../../creds.json`, true);

    define('DB_SERVER', $creds['sql']['hostname']);
    define('DB_USERNAME', $creds['sql']['username']);
    define('DB_PASSWORD', $creds['sql']['password']);
    define('DB_DATABASE', $creds['sql']['database']);

    $mysqli = new mysqli(DB_SERVER, DB_USERNAME, DB_PASSWORD, DB_DATABASE);

    if ($mysqli->connect_errno) {
        echo("connection error: " + $mysqli->connect_error);
    }
?>
