Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strAppDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = strAppDir

' Check if port 8088 is listening using WinHttpRequest
On Error Resume Next
Set http = CreateObject("MSXML2.ServerXMLHTTP")
http.open "GET", "http://localhost:8088/index.html", False
http.send

If Err.Number <> 0 Then
    ' Server is not running yet — start background server
    Err.Clear
    WshShell.Run "cmd.exe /c start /b py start_server.py", 0, False
    WScript.Sleep 2500
End If
On Error GoTo 0

' Open Microsoft Edge in Standalone App Mode (Signed system browser)
strEdge32 = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
strEdge64 = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"

If fso.FileExists(strEdge64) Then
    WshShell.Run """" & strEdge64 & """ --app=""http://localhost:8088/""", 1, False
ElseIf fso.FileExists(strEdge32) Then
    WshShell.Run """" & strEdge32 & """ --app=""http://localhost:8088/""", 1, False
Else
    WshShell.Run "http://localhost:8088/", 1, False
End If
