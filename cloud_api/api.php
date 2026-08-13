<?php
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");
header("Content-Type: application/json; charset=UTF-8");
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

// Database connection
$servername = "localhost";
$username = "orthodox_acct";
$password = "ChurchAccount@22053";
$dbname = "orthodox_acct";

$conn = new mysqli($servername, $username, $password, $dbname);
if ($conn->connect_error) {
    echo json_encode(['success' => false, 'message' => 'DB Connection failed: ' . $conn->connect_error]);
    exit;
}
$conn->set_charset("utf8mb4");

// Read input
$input = json_decode(file_get_contents('php://input'), true);
if (!$input) {
    $input = $_REQUEST;
}

$action = $input['action'] ?? '';
$response = ['success' => false, 'message' => 'No action provided'];

try {
    switch ($action) {

        case 'setup_tables':
            // Create cashbook table matching the JSON column format
            $conn->query("DROP TABLE IF EXISTS cashbook");
            $sql = "CREATE TABLE cashbook (
                id INT AUTO_INCREMENT PRIMARY KEY,
                col_A VARCHAR(50),
                col_B VARCHAR(100),
                col_C VARCHAR(100),
                col_D VARCHAR(255),
                col_E VARCHAR(255),
                col_F VARCHAR(100),
                col_G TEXT,
                col_H VARCHAR(50),
                col_I VARCHAR(50),
                col_K VARCHAR(50),
                col_L VARCHAR(100),
                col_M VARCHAR(255),
                col_N VARCHAR(100),
                col_O TEXT,
                col_P VARCHAR(50),
                col_Q VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )";
            if ($conn->query($sql)) {
                $conn->query("DROP TABLE IF EXISTS app_state");
                $sql2 = "CREATE TABLE app_state (
                    key_name VARCHAR(100) PRIMARY KEY,
                    json_data LONGTEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )";
                if ($conn->query($sql2)) {
                    $response = ['success' => true, 'message' => 'Tables created successfully'];
                } else {
                    throw new Exception($conn->error);
                }
            } else {
                throw new Exception($conn->error);
            }
            break;

        case 'get_cashbook':
            $result = $conn->query("SELECT * FROM cashbook ORDER BY id ASC");
            $data = [];
            if ($result) {
                while($row = $result->fetch_assoc()) {
                    // Convert DB columns back to JSON format
                    $entry = [];
                    foreach(['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'] as $col) {
                        $dbCol = 'col_' . $col;
                        if (isset($row[$dbCol]) && $row[$dbCol] !== null && $row[$dbCol] !== '') {
                            $entry[$col] = $row[$dbCol];
                        }
                    }
                    if (!empty($entry)) {
                        $data[] = $entry;
                    }
                }
                $response = ['success' => true, 'data' => $data, 'count' => count($data)];
            } else {
                throw new Exception($conn->error);
            }
            break;

        case 'get_app_state':
            // Auto-create table if it doesn't exist
            if (!$conn->query("CREATE TABLE IF NOT EXISTS app_state (
                key_name VARCHAR(100) PRIMARY KEY,
                json_data LONGTEXT
            )")) {
                throw new Exception("CREATE TABLE ERROR: " . $conn->error);
            }
            $result = $conn->query("SELECT * FROM app_state");
            $data = [];
            if ($result) {
                while($row = $result->fetch_assoc()) {
                    $data[$row['key_name']] = json_decode($row['json_data'], true);
                }
                $response = ['success' => true, 'data' => $data];
            } else {
                throw new Exception($conn->error);
            }
            break;

        case 'save_receipt':
            $date = $input['date'] ?? '';
            $receipt_no = $input['receipt_no'] ?? '';
            $reg_no = $input['reg_no'] ?? '';
            $name_of_hof = $input['name_of_hof'] ?? '';
            $receipt_acct_head = $input['receipt_acct_head'] ?? '';
            $receipt_code = $input['receipt_code'] ?? '';
            $receipt_details = $input['receipt_details'] ?? '';
            $receipt_cash = $input['receipt_cash'] ?? '';
            $receipt_bank = $input['receipt_bank'] ?? '';
            
            $sql = "INSERT INTO cashbook (col_A, col_B, col_C, col_D, col_E, col_F, col_G, col_H, col_I) VALUES (
                '" . $conn->real_escape_string($date) . "',
                '" . $conn->real_escape_string($receipt_no) . "',
                '" . $conn->real_escape_string($reg_no) . "',
                '" . $conn->real_escape_string($name_of_hof) . "',
                '" . $conn->real_escape_string($receipt_acct_head) . "',
                '" . $conn->real_escape_string($receipt_code) . "',
                '" . $conn->real_escape_string($receipt_details) . "',
                '" . $conn->real_escape_string($receipt_cash) . "',
                '" . $conn->real_escape_string($receipt_bank) . "'
            )";
            if ($conn->query($sql)) {
                $response = ['success' => true, 'message' => 'Receipt saved', 'id' => $conn->insert_id];
            } else {
                throw new Exception($conn->error);
            }
            break;

        case 'save_payment':
            $payment_date = $input['payment_date'] ?? '';
            $payment_voucher_no = $input['payment_voucher_no'] ?? '';
            $payment_acct_head = $input['payment_acct_head'] ?? '';
            $payment_code = $input['payment_code'] ?? '';
            $payment_details = $input['payment_details'] ?? '';
            $payment_cash = $input['payment_cash'] ?? '';
            $payment_bank = $input['payment_bank'] ?? '';
            
            $sql = "INSERT INTO cashbook (col_K, col_L, col_M, col_N, col_O, col_P, col_Q) VALUES (
                '" . $conn->real_escape_string($payment_date) . "',
                '" . $conn->real_escape_string($payment_voucher_no) . "',
                '" . $conn->real_escape_string($payment_acct_head) . "',
                '" . $conn->real_escape_string($payment_code) . "',
                '" . $conn->real_escape_string($payment_details) . "',
                '" . $conn->real_escape_string($payment_cash) . "',
                '" . $conn->real_escape_string($payment_bank) . "'
            )";
            if ($conn->query($sql)) {
                $response = ['success' => true, 'message' => 'Payment saved', 'id' => $conn->insert_id];
            } else {
                throw new Exception($conn->error);
            }
            break;

        case 'save_transaction':
            $row = $input['row'] ?? null;
            if (!$row) {
                throw new Exception('No row data provided');
            }
            
            $cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            $dbCols = [];
            $values = [];
            foreach ($cols as $col) {
                if (isset($row[$col]) && $row[$col] !== '') {
                    $dbCols[] = 'col_' . $col;
                    $values[] = "'" . $conn->real_escape_string($row[$col]) . "'";
                }
            }
            
            if (empty($dbCols)) {
                throw new Exception('No valid column data');
            }
            
            $sql = "INSERT INTO cashbook (" . implode(',', $dbCols) . ") VALUES (" . implode(',', $values) . ")";
            if ($conn->query($sql)) {
                $response = ['success' => true, 'message' => 'Transaction saved', 'id' => $conn->insert_id];
            } else {
                throw new Exception($conn->error);
            }
            break;

        case 'import_cashbook':
            // Bulk import from Cash_Book.json format
            $rows = $input['rows'] ?? [];
            if (empty($rows)) {
                throw new Exception('No rows to import');
            }
            
            // CLEAR table before bulk import to prevent duplication
            $conn->query("TRUNCATE TABLE cashbook");
            
            $imported = 0;
            $cols = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q'];
            
            foreach ($rows as $row) {
                $dbCols = [];
                $values = [];
                foreach ($cols as $col) {
                    if (isset($row[$col]) && $row[$col] !== null && $row[$col] !== '') {
                        $dbCols[] = 'col_' . $col;
                        $values[] = "'" . $conn->real_escape_string($row[$col]) . "'";
                    }
                }
                if (!empty($dbCols)) {
                    $sql = "INSERT INTO cashbook (" . implode(',', $dbCols) . ") VALUES (" . implode(',', $values) . ")";
                    if ($conn->query($sql)) {
                        $imported++;
                    }
                }
            }
            $response = ['success' => true, 'message' => "Imported $imported rows", 'count' => $imported];
            break;

        case 'save_app_state':
            $state_data = $input['state_data'] ?? [];
            if (empty($state_data)) {
                throw new Exception('No state data provided');
            }
            $saved = 0;
            // Auto-create table if it doesn't exist
            if (!$conn->query("CREATE TABLE IF NOT EXISTS app_state (
                key_name VARCHAR(100) PRIMARY KEY,
                json_data LONGTEXT
            )")) {
                throw new Exception("CREATE TABLE ERROR: " . $conn->error);
            }
            foreach ($state_data as $key => $val) {
                $safeKey = $conn->real_escape_string($key);
                $safeVal = $conn->real_escape_string(json_encode($val));
                $sql = "INSERT INTO app_state (key_name, json_data) VALUES ('$safeKey', '$safeVal') 
                        ON DUPLICATE KEY UPDATE json_data = '$safeVal'";
                if ($conn->query($sql)) {
                    $saved++;
                }
            }
            $response = ['success' => true, 'message' => "Saved $saved state keys"];
            break;

        case 'test':
            $response = ['success' => true, 'message' => 'API is working!', 'db' => 'connected'];
            break;

        default:
            $response = ['success' => false, 'message' => 'Unknown action: ' . $action];
            break;
    }
} catch (Exception $e) {
    $response = ['success' => false, 'message' => 'Error: ' . $e->getMessage()];
}

echo json_encode($response);
$conn->close();
?>
