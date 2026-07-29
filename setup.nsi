; 创为转Tray机操作SOP Windows Installer
; NSIS (Nullsoft Scriptable Install System) script
; Compile with: makensis setup.nsi

!include "MUI2.nsh"
!include "FileFunc.nsh"

; --- General ---
!define PRODUCT_NAME "创为转Tray机操作SOP"
!define PRODUCT_VERSION "2.0"
!define PRODUCT_PUBLISHER "创为科技"
!define INSTALL_DIR "$PROGRAMFILES\${PRODUCT_NAME}"

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "output\创为Tray机SOP_Setup.exe"
InstallDir "${INSTALL_DIR}"
RequestExecutionLevel admin
SetCompressor /SOLID lzma
ShowInstDetails show

; --- Interface ---
!define MUI_ABORTWARNING
!define MUI_ICON "dist\CWLOGO.ico"
!define MUI_UNICON "dist\CWLOGO.ico"

; --- Pages ---
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "English"

; --- Install Section ---
Section "Install"
  SetOutPath "$INSTDIR"

  ; Copy all files
  File /r "dist\*.*"

  ; Create desktop shortcut
  CreateShortCut "$DESKTOP\创为转Tray机操作SOP.lnk" "$INSTDIR\index.html" "" "$INSTDIR\CWLOGO.ico" 0

  ; Create Start Menu shortcuts
  CreateDirectory "$SMPROGRAMS\${PRODUCT_NAME}"
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\创为转Tray机操作SOP.lnk" "$INSTDIR\index.html" "" "$INSTDIR\CWLOGO.ico" 0
  CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}\卸载.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\CWLOGO.ico" 0

  ; Write uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; Write registry entries for Add/Remove Programs
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "Publisher" "${PRODUCT_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayIcon" "$INSTDIR\CWLOGO.ico"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "NoRepair" 1

  ; Get install size
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "EstimatedSize" "$0"

SectionEnd

; --- Uninstall Section ---
Section "Uninstall"
  ; Remove shortcuts
  Delete "$DESKTOP\创为转Tray机操作SOP.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\创为转Tray机操作SOP.lnk"
  Delete "$SMPROGRAMS\${PRODUCT_NAME}\卸载.lnk"
  RMDir "$SMPROGRAMS\${PRODUCT_NAME}"

  ; Remove registry
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"

  ; Remove all installed files
  RMDir /r "$INSTDIR"
SectionEnd
