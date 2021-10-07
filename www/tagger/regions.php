<?php
    class RegionDB extends SQLite3 {
        function __construct() {
            $this->open('db/regions.db');
        }
    }

    $create = !file_exists('db/regions.db');
    $db = new RegionDB();

    if ($create) $db->query('CREATE TABLE regions (
        path TEXT NOT NULL UNIQUE,
        tags TEXT NOT NULL,
        params TEXT NOT NULL
    );');

    if ($_GET['action'] == 'all') {
        $output = array();
        $result = $db->query('SELECT * FROM regions');
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            array_push($output, $row);
        }
        die(json_encode($output));
    }

    if ($_GET['action'] == 'tag') {
        if (!isset($_GET['tag'])) die('No search tag specified.');
        $output = array();
        $stmt = $db->prepare("SELECT path, params FROM regions WHERE tags LIKE '%' || :tag || '%'");
        $stmt->bindValue(':tag', $_GET['tag'], SQLITE3_TEXT);
        $result = $stmt->execute();
        while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
            array_push($output, $row);
        }
        die(json_encode($output));
    }

    if (!isset($_GET['path'])) die('No path specified.');

    switch($_GET['action']) {
        case 'list':
            $stmt = $db->prepare('SELECT * FROM regions WHERE path=:path');
            $stmt->bindValue(':path', $_GET['path'], SQLITE3_TEXT);
            $result = $stmt->execute();
            if (!$result) {
                die($db->lastErrorMsg());
            }
            echo ($output = $result->fetchArray(SQLITE3_ASSOC)) ? json_encode($output) : '{}';
            break;
        case 'update':
            if (!isset($_GET['tags'])) die('No tags specified.');
            if (!isset($_GET['params'])) die('No params specified.');
            $stmt = $db->prepare('INSERT OR REPLACE INTO regions (path, tags, params) VALUES (:path, :tags, :params)');
            $stmt->bindValue(':path', $_GET['path'], SQLITE3_TEXT);
            $stmt->bindValue(':tags', $_GET['tags'], SQLITE3_TEXT);
            $stmt->bindValue(':params', $_GET['params'], SQLITE3_TEXT);
            if (!$stmt->execute()) {
                die($db->lastErrorMsg());
            }
            break;
        default:
            die('No valid action.');
            break;
    }

    $db->close();
?>
