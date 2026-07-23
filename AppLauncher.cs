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
        private static int port = 8080;
        private static string appDir;
        private static NotifyIcon notifyIcon;

        [STAThread]
        static void Main(string[] args)
        {
            appDir = AppDomain.CurrentDomain.BaseDirectory;

            // Start HTTP Server Thread
            Thread serverThread = new Thread(StartWebServer);
            serverThread.IsBackground = true;
            serverThread.Start();

            // Open Default Web Browser
            Thread.Sleep(500);
            Process.Start(string.Format("http://localhost:{0}/", port));

            // Create System Tray Icon
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            ContextMenu contextMenu = new ContextMenu();
            contextMenu.MenuItems.Add("🌐 Open Accounting Portal", (s, e) => {
                Process.Start(string.Format("http://localhost:{0}/", port));
            });
            contextMenu.MenuItems.Add("📁 Open Data Directory", (s, e) => {
                string dataPath = Path.Combine(appDir, "data_export");
                if (Directory.Exists(dataPath)) Process.Start("explorer.exe", dataPath);
            });
            contextMenu.MenuItems.Add("-");
            contextMenu.MenuItems.Add("❌ Exit Application", (s, e) => {
                if (listener != null && listener.IsListening) listener.Stop();
                if (notifyIcon != null) notifyIcon.Dispose();
                Application.Exit();
            });

            notifyIcon = new NotifyIcon();
            notifyIcon.Icon = SystemIcons.Application;
            notifyIcon.Text = "St. Gregorios Church Accounting Portal";
            notifyIcon.ContextMenu = contextMenu;
            notifyIcon.Visible = true;

            notifyIcon.ShowBalloonTip(3000, 
                "St. Gregorios Church Accounting", 
                string.Format("Portal is running live at http://localhost:{0}/", port), 
                ToolTipIcon.Info);

            Application.Run();
        }

        private static void StartWebServer()
        {
            try
            {
                listener = new HttpListener();
                listener.Prefixes.Add(string.Format("http://localhost:{0}/", port));
                listener.Start();

                while (listener.IsListening)
                {
                    HttpListenerContext context = listener.GetContext();
                    ThreadPool.QueueUserWorkItem((o) => ProcessRequest(context));
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Server Error: " + ex.Message, "St. Gregorios Accounting Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static void ProcessRequest(HttpListenerContext context)
        {
            HttpListenerRequest request = context.Request;
            HttpListenerResponse response = context.Response;

            string path = request.Url.LocalPath.TrimStart('/');
            if (string.IsNullOrEmpty(path)) path = "index.html";

            string fullPath = Path.Combine(appDir, path.Replace('/', Path.DirectorySeparatorChar));

            if (File.Exists(fullPath))
            {
                byte[] buffer = File.ReadAllBytes(fullPath);
                
                string ext = Path.GetExtension(fullPath).ToLower();
                if (ext == ".html") response.ContentType = "text/html";
                else if (ext == ".css") response.ContentType = "text/css";
                else if (ext == ".js") response.ContentType = "application/javascript";
                else if (ext == ".json") response.ContentType = "application/json";

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
