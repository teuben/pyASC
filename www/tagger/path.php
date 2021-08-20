<?php
    if (!isset($_GET['search']) || !preg_match("/[\w-]+.fits?$/i", $_GET['search'])) die('Invalid search query.');
    chdir('../');
    // $result = shell_exec('find ' . $_GET['search']);
    // echo $result;
?>