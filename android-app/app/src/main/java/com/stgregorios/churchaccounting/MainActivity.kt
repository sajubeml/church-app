package com.stgregorios.churchaccounting

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.media.MediaScannerConnection
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import java.io.File

class MainActivity : ComponentActivity() {

    private lateinit var webView: WebView
    private var filePathCallback: ValueCallback<Array<Uri>>? = null

    private val fileChooserLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (filePathCallback != null) {
            val results = WebChromeClient.FileChooserParams.parseResult(result.resultCode, result.data)
            filePathCallback?.onReceiveValue(results)
            filePathCallback = null
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this)
        setContentView(webView)

        val settings: WebSettings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.allowFileAccessFromFileURLs = true
        settings.setSupportZoom(true)
        settings.builtInZoomControls = true
        settings.displayZoomControls = false
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW

        webView.isVerticalScrollBarEnabled = true
        webView.isHorizontalScrollBarEnabled = true

        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                return false
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                this@MainActivity.filePathCallback?.onReceiveValue(null)
                this@MainActivity.filePathCallback = filePathCallback

                val intent = fileChooserParams?.createIntent() ?: Intent(Intent.ACTION_GET_CONTENT).apply {
                    addCategory(Intent.CATEGORY_OPENABLE)
                    type = "*/*"
                }

                try {
                    fileChooserLauncher.launch(intent)
                } catch (e: Exception) {
                    this@MainActivity.filePathCallback = null
                    return false
                }
                return true
            }
        }

        webView.addJavascriptInterface(AndroidBridge(), "AndroidBridge")

        onBackPressedDispatcher.addCallback(this, object : androidx.activity.OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                if (::webView.isInitialized) {
                    webView.evaluateJavascript("(function(){ if (typeof closeAnyOpenModalOrPdf === 'function') { return closeAnyOpenModalOrPdf(); } return false; })()") { result ->
                        val closed = result != null && result != "false" && result != "null" && result != "0"
                        if (!closed) {
                            if (webView.canGoBack()) {
                                webView.goBack()
                            }
                        }
                    }
                }
            }
        })

        webView.setDownloadListener { url, _, _, mimeType, _ ->
            try {
                if (url.startsWith("blob:") || url.startsWith("data:")) {
                    // Blob/Data URLs are handled natively by JS bridge shareCsvFile/shareBackupJson
                    return@setDownloadListener
                }
                val intent = Intent(Intent.ACTION_VIEW).apply {
                    setDataAndType(Uri.parse(url), if (mimeType.isNullOrEmpty()) "*/*" else mimeType)
                }
                startActivity(intent)
            } catch (e: Exception) {
                // Ignore unhandled download intents silently
            }
        }

        // Load the cloud-hosted version instead of local assets
        webView.loadUrl("file:///android_asset/index.html")
    }

    inner class AndroidBridge {
        @JavascriptInterface
        fun shareBackupJson(jsonString: String, filename: String) {
            runOnUiThread {
                try {
                    val sendIntent: Intent = Intent().apply {
                        action = Intent.ACTION_SEND
                        putExtra(Intent.EXTRA_TEXT, jsonString)
                        putExtra(Intent.EXTRA_TITLE, filename)
                        type = "text/plain"
                    }
                    val shareIntent = Intent.createChooser(sendIntent, "Share / Save Backup JSON")
                    startActivity(shareIntent)
                } catch (e: Exception) {
                    Toast.makeText(this@MainActivity, "Share Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

        @JavascriptInterface
        fun shareBase64File(base64Content: String, filename: String) {
            runOnUiThread {
                try {
                    val bytes = android.util.Base64.decode(base64Content, android.util.Base64.DEFAULT)
                    val exportDir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS) ?: cacheDir
                    if (!exportDir.exists()) exportDir.mkdirs()

                    val exportFile = File(exportDir, filename)
                    exportFile.writeBytes(bytes)

                    try {
                        val pubDownloads = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                        if (pubDownloads.exists() || pubDownloads.mkdirs()) {
                            val pubFile = File(pubDownloads, filename)
                            pubFile.writeBytes(bytes)
                            MediaScannerConnection.scanFile(
                                this@MainActivity,
                                arrayOf(pubFile.absolutePath),
                                arrayOf("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/pdf"),
                                null
                            )
                        }
                    } catch (e: Exception) { }

                    val contentUri = androidx.core.content.FileProvider.getUriForFile(
                        this@MainActivity,
                        "${applicationContext.packageName}.fileprovider",
                        exportFile
                    )

                    val sendIntent = Intent(Intent.ACTION_SEND).apply {
                        type = "*/*"
                        putExtra(Intent.EXTRA_STREAM, contentUri)
                        putExtra(Intent.EXTRA_SUBJECT, filename)
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }

                    Toast.makeText(this@MainActivity, "📄 File exported: $filename", Toast.LENGTH_SHORT).show()

                    val chooser = Intent.createChooser(sendIntent, "Open / Share File")
                    chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    startActivity(chooser)

                } catch (e: Exception) {
                    Toast.makeText(this@MainActivity, "Export Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

        @JavascriptInterface
        fun shareCsvFile(csvContent: String, filename: String) {
            runOnUiThread {
                try {
                    val cleanName = if (filename.endsWith(".csv", ignoreCase = true)) filename else "$filename.csv"

                    val exportDir = getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS) ?: cacheDir
                    if (!exportDir.exists()) exportDir.mkdirs()

                    val exportFile = File(exportDir, cleanName)
                    exportFile.writeText(csvContent, Charsets.UTF_8)

                    try {
                        val pubDownloads = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                        if (pubDownloads.exists() || pubDownloads.mkdirs()) {
                            val pubFile = File(pubDownloads, cleanName)
                            pubFile.writeText(csvContent, Charsets.UTF_8)
                            MediaScannerConnection.scanFile(
                                this@MainActivity,
                                arrayOf(pubFile.absolutePath),
                                arrayOf("text/csv", "application/vnd.ms-excel", "text/plain"),
                                null
                            )
                        }
                    } catch (e: Exception) { }

                    val contentUri = androidx.core.content.FileProvider.getUriForFile(
                        this@MainActivity,
                        "${applicationContext.packageName}.fileprovider",
                        exportFile
                    )

                    val sendIntent = Intent(Intent.ACTION_SEND).apply {
                        type = "*/*"
                        putExtra(Intent.EXTRA_STREAM, contentUri)
                        putExtra(Intent.EXTRA_SUBJECT, cleanName)
                        putExtra(Intent.EXTRA_TEXT, "St. Gregorios Church Accounting Export: $cleanName")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }

                    Toast.makeText(this@MainActivity, "📄 Excel CSV exported: $cleanName", Toast.LENGTH_SHORT).show()

                    val chooser = Intent.createChooser(sendIntent, "Open / Share Excel File")
                    chooser.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    startActivity(chooser)

                } catch (e: Exception) {
                    Toast.makeText(this@MainActivity, "Export Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }

        @JavascriptInterface
        fun printPage(jobName: String?) {
            runOnUiThread {
                try {
                    val printManager = getSystemService(Context.PRINT_SERVICE) as android.print.PrintManager
                    val title = if (!jobName.isNullOrEmpty()) jobName else "St_Gregorios_Church_Accounting"
                    val printAdapter = webView.createPrintDocumentAdapter(title)
                    printManager.print(title, printAdapter, android.print.PrintAttributes.Builder().build())
                } catch (e: Exception) {
                    Toast.makeText(this@MainActivity, "Print Error: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
        
        @JavascriptInterface
        fun readAssetFile(filename: String): String {
            return try {
                assets.open(filename).bufferedReader().use { it.readText() }
            } catch (e: Exception) {
                "[]"
            }
        }
        
        // Native Database Bridge
        @JavascriptInterface
        fun fetchDatabaseState(): String {
            return try {
                val dbHelper = ChurchDatabaseHelper(this@MainActivity)
                val db = dbHelper.readableDatabase
                val cursor = db.rawQuery("SELECT * FROM cashbook", null)
                val cashbookArray = org.json.JSONArray()
                
                if (cursor.moveToFirst()) {
                    do {
                        val rowObj = org.json.JSONObject()
                        rowObj.put("A", cursor.getString(cursor.getColumnIndexOrThrow("date")))
                        rowObj.put("B", cursor.getString(cursor.getColumnIndexOrThrow("receipt_no")))
                        rowObj.put("C", cursor.getString(cursor.getColumnIndexOrThrow("reg_no")))
                        rowObj.put("D", cursor.getString(cursor.getColumnIndexOrThrow("name_of_hof")))
                        rowObj.put("E", cursor.getString(cursor.getColumnIndexOrThrow("receipt_acct_head")))
                        rowObj.put("F", cursor.getString(cursor.getColumnIndexOrThrow("receipt_code")))
                        rowObj.put("G", cursor.getString(cursor.getColumnIndexOrThrow("receipt_details")))
                        rowObj.put("H", cursor.getDouble(cursor.getColumnIndexOrThrow("receipt_cash")))
                        rowObj.put("I", cursor.getDouble(cursor.getColumnIndexOrThrow("receipt_bank")))
                        rowObj.put("K", cursor.getString(cursor.getColumnIndexOrThrow("payment_date")))
                        rowObj.put("L", cursor.getString(cursor.getColumnIndexOrThrow("payment_voucher_no")))
                        rowObj.put("M", cursor.getString(cursor.getColumnIndexOrThrow("payment_acct_head")))
                        rowObj.put("N", cursor.getString(cursor.getColumnIndexOrThrow("payment_code")))
                        rowObj.put("O", cursor.getString(cursor.getColumnIndexOrThrow("payment_details")))
                        rowObj.put("P", cursor.getDouble(cursor.getColumnIndexOrThrow("payment_cash")))
                        rowObj.put("Q", cursor.getDouble(cursor.getColumnIndexOrThrow("payment_bank")))
                        cashbookArray.put(rowObj)
                    } while (cursor.moveToNext())
                }
                cursor.close()
                db.close()
                
                val resultObj = org.json.JSONObject()
                resultObj.put("cashbook", cashbookArray)
                resultObj.toString()
            } catch (e: Exception) {
                e.printStackTrace()
                "{}"
            }
        }
        
        @JavascriptInterface
        fun bulkSync(jsonPayload: String): Boolean {
            return try {
                val jsonArray = org.json.JSONArray(jsonPayload)
                val dbHelper = ChurchDatabaseHelper(this@MainActivity)
                val db = dbHelper.writableDatabase
                db.beginTransaction()
                try {
                    db.execSQL("DELETE FROM cashbook")
                    for (i in 0 until jsonArray.length()) {
                        val obj = jsonArray.getJSONObject(i)
                        val values = android.content.ContentValues().apply {
                            put("date", obj.optString("A", ""))
                            put("receipt_no", obj.optString("B", ""))
                            put("reg_no", obj.optString("C", ""))
                            put("name_of_hof", obj.optString("D", ""))
                            put("receipt_acct_head", obj.optString("E", ""))
                            put("receipt_code", obj.optString("F", ""))
                            put("receipt_details", obj.optString("G", ""))
                            put("receipt_cash", obj.optDouble("H", 0.0))
                            put("receipt_bank", obj.optDouble("I", 0.0))
                            put("payment_date", obj.optString("K", ""))
                            put("payment_voucher_no", obj.optString("L", ""))
                            put("payment_acct_head", obj.optString("M", ""))
                            put("payment_code", obj.optString("N", ""))
                            put("payment_details", obj.optString("O", ""))
                            put("payment_cash", obj.optDouble("P", 0.0))
                            put("payment_bank", obj.optDouble("Q", 0.0))
                        }
                        db.insert("cashbook", null, values)
                    }
                    db.setTransactionSuccessful()
                } finally {
                    db.endTransaction()
                    db.close()
                }
                true
            } catch (e: Exception) {
                e.printStackTrace()
                false
            }
        }
        
        @JavascriptInterface
        fun saveTransaction(jsonPayload: String, isReceipt: Boolean): Boolean {
            return try {
                val obj = org.json.JSONObject(jsonPayload)
                val dbHelper = ChurchDatabaseHelper(this@MainActivity)
                val db = dbHelper.writableDatabase
                
                val values = android.content.ContentValues()
                if (isReceipt) {
                    values.put("date", obj.optString("date", ""))
                    values.put("receipt_no", obj.optString("receipt_no", ""))
                    values.put("reg_no", obj.optString("reg_no", ""))
                    values.put("name_of_hof", obj.optString("name_of_hof", ""))
                    values.put("receipt_acct_head", obj.optString("receipt_acct_head", ""))
                    values.put("receipt_code", obj.optString("receipt_code", ""))
                    values.put("receipt_details", obj.optString("receipt_details", ""))
                    values.put("receipt_cash", obj.optDouble("receipt_cash", 0.0))
                    values.put("receipt_bank", obj.optDouble("receipt_bank", 0.0))
                } else {
                    values.put("payment_date", obj.optString("payment_date", ""))
                    values.put("payment_voucher_no", obj.optString("payment_voucher_no", ""))
                    values.put("payment_acct_head", obj.optString("payment_acct_head", ""))
                    values.put("payment_code", obj.optString("payment_code", ""))
                    values.put("payment_details", obj.optString("payment_details", ""))
                    values.put("payment_cash", obj.optDouble("payment_cash", 0.0))
                    values.put("payment_bank", obj.optDouble("payment_bank", 0.0))
                }
                
                db.insert("cashbook", null, values)
                db.close()
                true
            } catch (e: Exception) {
                e.printStackTrace()
                false
            }
        }
    }

    override fun onConfigurationChanged(newConfig: android.content.res.Configuration) {
        super.onConfigurationChanged(newConfig)
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (::webView.isInitialized) {
            webView.evaluateJavascript("(function(){ if (typeof closeAnyOpenModalOrPdf === 'function') { return closeAnyOpenModalOrPdf(); } return false; })()") { result ->
                val closed = result != null && result != "false" && result != "null" && result != "0"
                if (!closed) {
                    if (webView.canGoBack()) {
                        webView.goBack()
                    } else {
                        @Suppress("DEPRECATION")
                        super.onBackPressed()
                    }
                }
            }
        } else {
            @Suppress("DEPRECATION")
            super.onBackPressed()
        }
    }
}
