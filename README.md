# Aeri Learning landing page

A responsive, static Aeri Learning landing page for the free five-page preschool activity pack. It keeps the existing sage, charcoal, warm-cream, beige, and muted-coral design, with the site source separated into HTML, CSS, and JavaScript. No front-end framework or build step is required.

## Project structure

```text
.
├── index.html                         # Main landing page and Apps Script form
├── thanks/
│   ├── index.html                     # Standalone confirmation page and direct PDF download
│   ├── README.md                      # Confirmation-page-specific setup and maintenance notes
│   ├── css/
│   │   └── thanks.css                 # Confirmation-page-only responsive styles
│   └── js/
│       └── thanks.js                  # Confirmation-page download feedback
├── css/
│   └── style.css                      # Landing-page styles only
├── js/
│   └── script.js                      # Landing form, animations, dialogs, and CTA
├── apps-script/
│   └── Code.gs                        # Google Apps Script web-app endpoint
├── assets/
│   ├── images/
│   │   ├── aeri-learning-family.jpg   # Hero photo
│   │   └── aeri-learning-logo.png     # Full Aeri Learning logo
│   ├── icons/
│   │   └── aeri-learning-mark.png     # Emblem and favicon
│   └── documents/
│       └── aeri-learning-activity-pack.pdf
├── scripts/
│   └── generate_activity_pack.py     # Source for regenerating the printable PDF
└── uploads/
    └── image-1.png                    # Original uploaded logo source
```

The `thanks/` folder contains its own page, README, CSS, and JavaScript. The confirmation page does not load or import the landing page's `css/style.css` or `js/script.js`; its links to shared assets are relative. All website paths work beneath a GitHub Pages project path.

## Run the website locally

From the project root, start Python's static-file server:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. To preview from another device on your local network, use `python3 -m http.server 8000 --bind 0.0.0.0` and visit the host computer's LAN address.

## Connect the Google Apps Script form

The landing page posts `name`, `email`, a request token, and a honeypot field to the `/exec` web-app URL in the form's `action`. The script validates the fields and adds a timestamp, parent name, and email to the configured spreadsheet tab. The response is returned to a hidden iframe; the page's JavaScript checks its response and redirects successful submissions to `https://softwareupload2025-del.github.io/aeri-learning-thanks/`. It does not use FormSubmit or send an automatic email, and it does not display a standalone `Success` response.

1. Create or select the spreadsheet where requests should be stored. The tab must be named `Sheet1`, or update `SHEET_NAME` in `apps-script/Code.gs`.
2. For a bound script, open **Extensions → Apps Script** from that spreadsheet and paste in `apps-script/Code.gs`. For a standalone script, set `SPREADSHEET_ID` to the ID in the spreadsheet URL.
3. Deploy the script as a **Web app**. Set **Execute as** to the spreadsheet owner and **Who has access** to **Anyone** so visitors can submit without Google sign-in. Authorize the script when prompted. If your account or organization does not allow public access, this endpoint cannot accept anonymous submissions; use an approved public form service instead.
4. Copy the deployment's `/exec` URL into the `action` attribute on the form in `index.html`. The project currently contains the URL supplied for this integration; replace it if you deploy a different web app.
5. If you change the Apps Script after deployment, update the existing deployment to a new version. A newly created deployment may have a different URL.

The form uses a normal browser POST rather than `fetch`, so it avoids browser CORS handling. Apps Script returns a `postMessage` response to the page; the client checks the hidden iframe and request token before redirecting. The script uses `ALLOWALL` for its response because it must load inside that hidden iframe. Since the web app is publicly reachable, keep the server-side validation and honeypot enabled; add stronger anti-spam controls if needed.

**Testing and privacy:** Do not submit real parent data while testing. Use a test name and email and confirm that a row appears in the intended spreadsheet. The included script only records form requests; it does not email the activity pack automatically. The thank-you page provides a direct download, and any promise to send the pack later requires a separate manual or automated delivery process. Review the privacy notice and spreadsheet access before publishing.

## Publish with GitHub Pages

Commit the project files and publish the repository root (or the configured folder that contains `index.html`). Keep `thanks/`, `css/`, `js/`, `apps-script/`, and `assets/` in the repository; don't change local links to root-absolute paths.

## Regenerate the activity pack (optional)

The included script uses Python 3 and Pillow. From the project root:

```bash
python3 -m pip install Pillow
python3 scripts/generate_activity_pack.py
```

It writes `assets/documents/aeri-learning-activity-pack.pdf`.
