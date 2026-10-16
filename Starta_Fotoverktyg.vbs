' Windows double-click launcher. PowerShell runs hidden; dialogs remain visible.
Option Explicit
Dim shell, fs, folder, ps1, command
Set shell = CreateObject("WScript.Shell")
Set fs = CreateObject("Scripting.FileSystemObject")
folder = fs.GetParentFolderName(WScript.ScriptFullName)
ps1 = fs.BuildPath(folder, "Starta_Fotoverktyg.ps1")
If Not fs.FileExists(ps1) Then
    MsgBox "Starta_Fotoverktyg.ps1 saknas. Behåll startfilerna i samma mapp.", vbCritical, "Fotoverktyg"
    WScript.Quit 1
End If
command = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File " & Chr(34) & ps1 & Chr(34)
shell.Run command, 0, False
