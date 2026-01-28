# Packaging Michael's Pomodoro for Windows Store

This directory contains the tools to package the application as an `.msix` bundle for the Microsoft Store.

## Prerequisites

1.  **Python** installed.
2.  **Windows SDK** installed (specifically the `MakeAppx.exe` tool).
    *   Usually found in `C:\Program Files (x86)\Windows Kits\10\bin\<version>\x64\MakeAppx.exe`.
    *   Ensure it is in your PATH, or you will need to provide the full path to it.

## Steps

1.  **Install Dependencies**
    Run from the project root:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Build and Stage**
    Run the build script from the project root:
    ```bash
    python packaging/build_msix.py
    ```
    This script will:
    *   Run `PyInstaller` to create the EXE.
    *   Create a `dist/MichaelsPomodoro` directory.
    *   Copy the `AppxManifest.xml` there.
    *   Generate necessary Store logos from `assets/icon.png`.

3.  **Package (Create MSIX)**
    After the build script completes, it will print a command similar to this:
    ```bash
    MakeAppx pack /d "d:\my-code\michaels-pomodoro\dist\MichaelsPomodoro" /p "MichaelsPomodoro.msix"
    ```
    Run that command in your terminal.

4.  **Sign (Optional for Store, Required for Local Testing)**
    *   **For Store Submission**: You do NOT need to sign it yourself. You upload the `.msix` (or `.msixupload` if you create a bundle) to Partner Center, and Microsoft signs it.
    *   **For Local Testing**: You must sign the package with a trusted certificate.
        ```bash
        # Create a certificate (Run as Admin)
        New-SelfSignedCertificate -Type Custom -Subject "CN=Test" -KeyUsage DigitalSignature -FriendlyName "MichaelsPomodoroCert" -CertStoreLocation "Cert:\LocalMachine\My" -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

        # Sign (using Signtool from Windows SDK)
        SignTool sign /fd SHA256 /a /f <path_to_pfx> /p <password> MichaelsPomodoro.msix
        ```
    *   *Note*: The `CN` in Identity in `AppxManifest.xml` must match the Certificate Subject. Currently it is `CN=Test`.

## Submission
1.  Go to [Microsoft Partner Center](https://partner.microsoft.com/dashboard).
2.  Create a new app.
3.  Reserve a name.
4.  Update `packaging/AppxManifest.xml` with the Identity details provided by the Store (Name, Publisher, Version).
5.  Re-run Step 2 and 3.
6.  Upload the `.msix` file.
