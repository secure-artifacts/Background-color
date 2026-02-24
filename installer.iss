[Setup]
AppName=Background Color Viewer
AppVersion=1.0.1
DefaultDirName={autopf}\BackgroundColorViewer
DefaultGroupName=Background Color Viewer
OutputBaseFilename=BackgroundColorViewer_Setup_Windows
OutputDir=dist
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest

[Files]
Source: "dist\BackgroundColorViewer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Background Color Viewer"; Filename: "{app}\BackgroundColorViewer.exe"
Name: "{autodesktop}\Background Color Viewer"; Filename: "{app}\BackgroundColorViewer.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
