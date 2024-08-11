[Setup]
AppName=Media Muse
AppVersion=1.0
DefaultDirName={pf}\Media Muse
DefaultGroupName=Media Muse
OutputDir=dist
OutputBaseFilename=media_muse_windows_installer

[Files]
Source: "dist\media_muse_Windows\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\Media Muse"; Filename: "{app}\media_muse_Windows.exe"