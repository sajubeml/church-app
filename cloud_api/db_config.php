<?php
// db_config.php — Database connection for Church Accounting
$servername = "localhost";
$username = "orthodox_acct";
$password = "ChurchAccount@22053";
$dbname = "orthodox_acct";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    header("Content-Type: application/json");
    echo json_encode(['success' => false, 'message' => 'DB Connection failed: ' . $conn->connect_error]);
    exit;
}
$conn->set_charset("utf8mb4");
?>
