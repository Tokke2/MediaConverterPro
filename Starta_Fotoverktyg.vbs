' Windows double-click launcher. PowerShell runs hidden; dialogs remain visible.
Option Explicit
Dim shell, fs, folder, ps1, command
Set shell = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
folder = fs.GetParentFolderName(WScript.ScriptFullName)
ps1 = fs.BuildPath(folder, "Starta_Fotoverktyg.ps1")
If Not fs.FileExists(ps1) Then
    MsgBox "Starta_Fotoverktyg.ps1 saknas. Behåll startfilerna i samma mapp.", vbCritical, "MediaForge"
    WScript.Quit 1
End If
command = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File " & Chr(34) & ps1 & Chr(34)
If WScript.Arguments.Count > 0 Then
    command = command & " -OpenPath " & Chr(34) & Replace(WScript.Arguments(0), Chr(34), Chr(34) & Chr(34)) & Chr(34)
End If
shell.Run command, 0, False
