' Windows double-click launcher. PowerShell runs hidden; dialogs remain visible.
Option Explicit
Dim shell, fs, folder, ps1, command, errorLog
Set shell = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
folder = fs.GetParentFolderName(WScript.ScriptFullName)
errorLog = fs.BuildPath(fs.BuildPath(fs.BuildPath(folder, "MediaForge_Data"), "Logs"), "errors.log")
ps1 = fs.BuildPath(folder, "Starta_Fotoverktyg.ps1")
If Not fs.FileExists(ps1) Then
    WriteError "Starta_Fotoverktyg.ps1 saknas."
    MsgBox "Starta_Fotoverktyg.ps1 saknas. Behåll startfilerna i samma mapp.", vbCritical, "MediaForge"
    WScript.Quit 1
End If
command = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File " & Chr(34) & ps1 & Chr(34)
If WScript.Arguments.Count > 0 Then
    command = command & " -OpenPath " & Chr(34) & Replace(WScript.Arguments(0), Chr(34), Chr(34) & Chr(34)) & Chr(34)
End If
On Error Resume Next
shell.Run command, 0, False
If Err.Number <> 0 Then
    WriteError "Kunde inte starta PowerShell-startaren: " & Err.Description
    MsgBox "MediaForge-startaren kunde inte startas. Se felloggen i MediaForge_Data\Logs.", vbCritical, "MediaForge"
    WScript.Quit 1
End If
On Error GoTo 0

Sub WriteError(message)
    On Error Resume Next
    Dim dataDir, logDir, f
    dataDir = fs.BuildPath(folder, "MediaForge_Data")
    logDir = fs.BuildPath(dataDir, "Logs")
    If Not fs.FolderExists(dataDir) Then fs.CreateFolder dataDir
    If Not fs.FolderExists(logDir) Then fs.CreateFolder logDir
    Set f = fs.OpenTextFile(errorLog, 8, True)
    f.WriteLine Now & " | ERROR | " & message
    f.Close
    On Error GoTo 0
End Sub
