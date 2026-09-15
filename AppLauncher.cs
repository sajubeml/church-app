using System;
using System.IO;
using System.Net;
using System.Text;
using System.Threading;
using System.Diagnostics;
using System.Windows.Forms;
using System.Drawing;

namespace StGregoriosChurchAccounting
{
    class Program
    {
        private static HttpListener listener;
        private static int port = 8088;
        private static string appDir;
        private static NotifyIcon notifyIcon;

        // DEVELOPER BRANDING & TIME-BOUND LICENSE CONFIGURATION
        private const string DEVELOPER_NAME = "4S POWER SYSTEMS Mysore";
        private const string DEVELOPER_MOB = "9980615758";
        private static readonly DateTime LICENSE_EXPIRY = new DateTime(2028, 3, 31, 23, 59, 59);

        [STAThread]
        static void Main(string[] args)
        {
            bool createdNew;
            using (Mutex mutex = new Mutex(true, "StGregoriosChurchAccountingMutex_2026", out createdNew))
            {
                if (!createdNew)
                {
                    // Server is ALREADY running! Open browser directly and exit cleanly without error popups.
                    try { Process.Start(string.Format("http://localhost:{0}/", port)); } catch {}
                    return;
                }

                appDir = AppDomain.CurrentDomain.BaseDirectory;

                // 1. TIME-BOUND LICENSE & SECURITY TAMPER VERIFICATION
                if (DateTime.Now > LICENSE_EXPIRY)
                {
                    MessageBox.Show(
                        "SOFTWARE LICENSE EXPIRED!\n\n" +
                        "The time-bound license for St. Gregorios Church Accounting Portal has ended (Validity: 31-03-2028).\n\n" +
                        "For License Key Renewal & Authorization, please contact:\n" +
                        "Developer: " + DEVELOPER_NAME + "\n" +
                        "Mobile: " + DEVELOPER_MOB,
                        "License Expired — " + DEVELOPER_NAME,
                        MessageBoxButtons.OK,
                        MessageBoxIcon.Stop
                    );
                    return;
                }

                // 2. Start HTTP Server Thread
                Thread serverThread = new Thread(StartWebServer);
                serverThread.IsBackground = true;
                serverThread.Start();

                // 3. Open Default Web Browser
                Thread.Sleep(500);
                try
                {
                    Process.Start(string.Format("http://localhost:{0}/", port));
                }
                catch
                {
                    Process.Start("IExplore.exe", string.Format("http://localhost:{0}/", port));
                }

            // 4. Create System Tray Icon
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            ContextMenu contextMenu = new ContextMenu();
            contextMenu.MenuItems.Add("🌐 Open Accounting Portal", (s, e) => {
                try { Process.Start(string.Format("http://localhost:{0}/", port)); } catch {}
            });
            contextMenu.MenuItems.Add("📁 Open Data Directory", (s, e) => {
                string dataPath = Path.Combine(appDir, "data_export");
                if (Directory.Exists(dataPath)) Process.Start("explorer.exe", dataPath);
            });
            contextMenu.MenuItems.Add("-");
            contextMenu.MenuItems.Add("ℹ️ Developed by " + DEVELOPER_NAME, (s, e) => {
                MessageBox.Show(
                    "St. Gregorios Church Financial Accounting Portal v1.0\n\n" +
                    "Software Developed by: " + DEVELOPER_NAME + "\n" +
                    "Contact Mobile: " + DEVELOPER_MOB + "\n" +
                    "Compatibility: Windows XP / Vista / 7 / 8 / 10 / 11\n" +
                    "License Valid Until: 31-03-2028",
                    "Software Information",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );
            });
            contextMenu.MenuItems.Add("❌ Exit Application", (s, e) => {
                if (listener != null && listener.IsListening) listener.Stop();
                if (notifyIcon != null) notifyIcon.Dispose();
                Application.Exit();
            });

            notifyIcon = new NotifyIcon();
            notifyIcon.Icon = SystemIcons.Application;
            notifyIcon.Text = "St. Gregorios Church Accounting (" + DEVELOPER_NAME + ")";
            notifyIcon.ContextMenu = contextMenu;
            notifyIcon.Visible = true;

            notifyIcon.ShowBalloonTip(3000, 
                "St. Gregorios Church Accounting", 
                string.Format("Running live at http://localhost:{0}/\nDeveloped by {1} ({2})", port, DEVELOPER_NAME, DEVELOPER_MOB), 
                ToolTipIcon.Info);

            Application.Run();
            }
        }

        private static void StartWebServer()
        {
            try
            {
                listener = new HttpListener();
                listener.Prefixes.Add(string.Format("http://localhost:{0}/", port));
                listener.Prefixes.Add(string.Format("http://127.0.0.1:{0}/", port));
                listener.Start();

                while (listener.IsListening)
                {
                    HttpListenerContext context = listener.GetContext();
                    ThreadPool.QueueUserWorkItem((o) => ProcessRequest(context));
                }
            }
            catch (HttpListenerException)
            {
                // Port 8080 is already bound by existing server instance. Open browser and exit silently.
                try { Process.Start(string.Format("http://localhost:{0}/", port)); } catch {}
            }
            catch (Exception)
            {
                // Fail-safe silent catch for unexpected listener stop
            }
        }

        private static void ProcessRequest(HttpListenerContext context)
        {
            HttpListenerRequest request = context.Request;
            HttpListenerResponse response = context.Response;

            string path = request.Url.LocalPath.TrimStart('/');
            if (string.IsNullOrEmpty(path)) path = "index.html";

            // Handle API POST request to save printed receipts to print/ folder
            if (request.HttpMethod == "POST" && request.Url.LocalPath.Equals("/api/save_print", StringComparison.OrdinalIgnoreCase))
            {
                try
                {
                    using (StreamReader reader = new StreamReader(request.InputStream, request.ContentEncoding))
                    {
                        string jsonText = reader.ReadToEnd();
                        string printDir = Path.Combine(appDir, "Receipts");
                        if (!Directory.Exists(printDir)) Directory.CreateDirectory(printDir);

                        string filename = "Receipt.html";
                        string content = "";

                        int fnStart = jsonText.IndexOf("\"filename\":");
                        if (fnStart >= 0)
                        {
                            int valStart = jsonText.IndexOf("\"", fnStart + 11) + 1;
                            int valEnd = jsonText.IndexOf("\"", valStart);
                            if (valStart > 0 && valEnd > valStart)
                            {
                                filename = jsonText.Substring(valStart, valEnd - valStart);
                            }
                        }

                        int ctStart = jsonText.IndexOf("\"content\":");
                        if (ctStart >= 0)
                        {
                            int valStart = jsonText.IndexOf("\"", ctStart + 10) + 1;
                            int valEnd = jsonText.LastIndexOf("\"");
                            if (valStart > 0 && valEnd > valStart)
                            {
                                content = jsonText.Substring(valStart, valEnd - valStart);
                                content = System.Text.RegularExpressions.Regex.Unescape(content);
                            }
                        }

                        string savePath = Path.Combine(printDir, filename);
                        File.WriteAllText(savePath, content, Encoding.UTF8);

                        string pdfName = filename.Replace(".html", ".pdf");
                        if (!pdfName.EndsWith(".pdf")) pdfName += ".pdf";
                        string pdfPath = Path.Combine(printDir, pdfName);

                        try
                        {
                            string edgePath = @"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe";
                            if (!File.Exists(edgePath)) edgePath = @"C:\Program Files\Microsoft\Edge\Application\msedge.exe";
                            if (File.Exists(edgePath))
                            {
                                var psi = new System.Diagnostics.ProcessStartInfo
                                {
                                    FileName = edgePath,
                                    Arguments = string.Format("--headless --print-to-pdf=\"{0}\" --no-pdf-header-footer \"{1}\"", pdfPath, savePath),
                                    CreateNoWindow = true,
                                    UseShellExecute = false
                                };
                                var proc = System.Diagnostics.Process.Start(psi);
                                proc.WaitForExit(3000);
                            }
                        }
                        catch {}

                        string jsonRes = string.Format("{{\"status\":\"ok\",\"pdf_url\":\"Receipts/{0}\"}}", pdfName);
                        byte[] resBuf = Encoding.UTF8.GetBytes(jsonRes);
                        response.ContentType = "application/json";
                        response.ContentLength64 = resBuf.Length;
                        response.OutputStream.Write(resBuf, 0, resBuf.Length);
                    }
                }
                catch (Exception ex)
                {
                    byte[] errBuf = Encoding.UTF8.GetBytes("{\"status\":\"error\",\"message\":\"" + ex.Message + "\"}");
                    response.ContentType = "application/json";
                    response.OutputStream.Write(errBuf, 0, errBuf.Length);
                }
                response.OutputStream.Close();
                return;
            }

            string fullPath = Path.Combine(appDir, path.Replace('/', Path.DirectorySeparatorChar));

            if (File.Exists(fullPath))
            {
                byte[] buffer = File.ReadAllBytes(fullPath);
                
                string ext = Path.GetExtension(fullPath).ToLower();
                if (ext == ".html") response.ContentType = "text/html";
                else if (ext == ".css") response.ContentType = "text/css";
                else if (ext == ".js") response.ContentType = "application/javascript";
                else if (ext == ".json") response.ContentType = "application/json";

                response.Headers.Add("Cache-Control", "no-cache, no-store, must-revalidate");
                response.Headers.Add("Pragma", "no-cache");
                response.Headers.Add("Expires", "0");

                response.ContentLength64 = buffer.Length;
                response.OutputStream.Write(buffer, 0, buffer.Length);
            }
            else
            {
                response.StatusCode = 404;
            }
            response.OutputStream.Close();
        }
    }
}
