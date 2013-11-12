<?php

include('config.inc.php');
header('Content-type: application/json');
$db = new PDO("mysql:host=localhost;dbname=def100k", $user, $passwd);
$stmt = $db->prepare('SELECT * FROM images WHERE username=?');
$stmt->bindParam(1, $_GET['handle']);
$stmt->execute();
$data = $stmt->fetch(PDO::FETCH_ASSOC);
echo json_encode($data);
