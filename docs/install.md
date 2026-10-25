# Installing on Android (and Android developer verification)

## Install from a release (on the phone)

1. On the phone, open the latest release page:
   <https://github.com/mjcipriano/zany-test-prep/releases/latest>
2. Under **Assets**, tap `zany-test-prep-vX.Y.Z.apk` (not "Source code").
3. **Wait until the download says it is complete.** The APK is large; opening it
   while it is still downloading, or after a dropped connection, gives
   *"There was a problem parsing the package."* Use Wi‑Fi if you can.
4. Open the file from the browser's download notification or the **Files** app →
   **Downloads**.
5. If Android asks, allow **Install unknown apps** for that app (Chrome or Files),
   go back, and tap **Install** (or **Update**).

Updates install in place over the previous version and keep your progress:
every release is signed with the same key.

### Install from a computer instead (most reliable)

Use this if the phone download keeps failing. ADB installs never need developer
verification.

1. On the phone: **Settings → About phone →** tap **Build number** 7 times, then
   **Settings → System → Developer options →** turn on **USB debugging**.
2. On the computer: install the Android
   [platform-tools](https://developer.android.com/tools/releases/platform-tools),
   download the APK, plug in the phone and accept the prompt on it.
3. Run:

   ```bash
   adb install -r zany-test-prep-vX.Y.Z.apk
   ```

### Check the download (optional)

Each release also has `zany-test-prep-vX.Y.Z.apk.sha256`. Its hash must match the
downloaded file. On a computer, run `sha256sum zany-test-prep-vX.Y.Z.apk`. On the
phone, file managers such as Material Files can show a file's SHA‑256.

## Troubleshooting

| Message | Cause | Fix |
| --- | --- | --- |
| There was a problem parsing the package | The download is incomplete or interrupted. Or the phone runs Android 6 or older (the app needs Android 7.0+). Or you opened a GitHub Actions artifact `.zip` instead of the release `.apk`. | Delete the file and download it again from **Releases**, waiting for it to finish. Check the size or SHA‑256. Or install with ADB. |
| App not installed / package conflicts | A copy signed with a different key is installed, such as an old debug build. | Export a backup first (Settings → Backup & restore). Then uninstall the old copy, install the release, and import the backup. |
| Install blocked: app from an unverified developer | Android developer verification is enforced in your region (see below). | Use Android's *advanced flow* for unverified apps, or ADB. Long term, register the app (below). |
| Can't open file | The browser saved it under another name or type. | Open it from **Files → Downloads**, not from the browser's history. |

## Android developer verification (what it means for this app)

Google now requires apps installed on certified Android devices to be
**registered by a verified developer**. That covers apps from outside Google Play
too.

| When | Where | Effect |
| --- | --- | --- |
| Since 30 Sep 2026 | Brazil, Indonesia, Singapore, Thailand | Unregistered apps are blocked on certified devices. |
| 2027 (global rollout) | Everywhere else, including the US | The same rule applies everywhere. |

Unregistered apps can still be installed with **ADB** or the **advanced flow**,
a one-time setup with a waiting period. Verification does not cause the
"problem parsing the package" error. A blocked unverified app shows its own
message.

Sources:
[Google: Android developer verification](https://developer.android.com/developer-verification),
[limited distribution guide](https://developer.android.com/developer-verification/guides/limited-distribution),
[Android Developer Console guide](https://developer.android.com/developer-verification/guides/android-developer-console),
[FAQ](https://developer.android.com/developer-verification/guides/faq).

### Recommended path: a free limited distribution account

This is a personal/family app, so the **limited distribution account** fits. It is
free, needs no government ID, and lets you share the app with **up to 20 devices**.
Each device is authorized through a QR-code or link handshake with the owner's
consent.

What the app owner has to do (only the account holder can do this):

1. Create an account in the **Android Developer Console** with a Google Account
   that has **2‑Step Verification** turned on, and choose **limited distribution**.
   It uses your Google payments profile for your legal name and address.
2. **Register the package name** on the Packages page:
   - Package name: `ai.zanybot.zany_test_prep`
   - Signing key SHA‑256 fingerprint:
     `1D:9D:03:EB:A0:CA:CD:A8:31:A2:DE:E5:7E:21:57:0A:0B:77:81:B5:61:2F:31:F5:C9:4E:B6:D4:F2:9F:D2:05`
     (certificate `CN=Zany Test Prep, O=ZanyBot`, valid until 2053)
3. **Prove ownership.** The console gives you a small snippet file to put in the
   APK's assets folder. In GitHub, go to **Actions → Ownership proof APK → Run
   workflow**, and paste the snippet's file name and contents. The workflow signs
   the APK with the release key from the repo secrets. Download the
   `ownership-proof-apk` artifact and upload the APK to the console.
4. When the package shows **Registered**, authorize each phone (up to 20) using
   the console's QR code or link.

If the app ever needs more than 20 devices, upgrade to **full distribution**.
Individuals provide a government photo ID and proof of address. Organizations
also need a D‑U‑N‑S number and a verified website. A limited account can be
upgraded later.

> **Never change the signing key.** The registration is tied to the fingerprint
> above. Releases are signed with it from the `KEYSTORE_BASE64` repo secret. Keep
> the offline backup of `android/app/zany-release.jks` safe.
