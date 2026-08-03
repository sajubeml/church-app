import subprocess, os

cs_code = """
using System;
using System.Net;
using System.Threading;

class Test
{
    static void Main()
    {
        int port = 8088;
        HttpListener listener = new HttpListener();
        
        // Always add localhost & 127.0.0.1
        listener.Prefixes.Add(string.Format("http://localhost:{0}/", port));
        listener.Prefixes.Add(string.Format("http://127.0.0.1:{0}/", port));

        try
        {
            listener.Start();
            Console.WriteLine("[OK] Listener started successfully on localhost & 127.0.0.1!");
            listener.Stop();
        }
        catch (Exception ex)
        {
            Console.WriteLine("[ERROR] Failed to start listener: " + ex.Message);
        }
    }
}
"""

with open("TestBinding.cs", "w", encoding="utf-8") as f:
    f.write(cs_code)

csc = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
subprocess.run([csc, "/out:TestBinding.exe", "TestBinding.cs"], check=True)
res = subprocess.run(["TestBinding.exe"], capture_output=True, text=True)
print(res.stdout)

if os.path.exists("TestBinding.cs"): os.remove("TestBinding.cs")
if os.path.exists("TestBinding.exe"): os.remove("TestBinding.exe")
