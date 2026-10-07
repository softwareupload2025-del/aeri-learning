# Aeri Learning landing page

A responsive, static Aeri Learning landing page for the free five-page preschool activity pack. It keeps the existing sage, charcoal, warm-cream, beige, and muted-coral design, with the source separated into HTML, CSS, and JavaScript. No framework, build step, or external front-end dependency is required.

## Project structure

```text
.
├── index.html                         # Main landing page
├── thank-you.html                     # FormSubmit redirect and direct PDF download
├── css/
│   └── style.css                      # Shared landing-page and thank-you-page styles
├── js/
│   └── script.js                      # Form state, animations, dialogs, and mobile CTA
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

All website links use relative paths so the site also works when published beneath a GitHub Pages project path.

## Run locally

From the project root, start Python's static-file server:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. To preview on another device on your local network, bind to all interfaces with `python3 -m http.server 8000 --bind 0.0.0.0` and visit the host computer's LAN address.

## Publish with GitHub Pages

Commit the project files and publish the repository root (or the configured folder that contains `index.html`) with GitHub Pages. Keep the `css/`, `js/`, and `assets/` directories alongside the HTML files; don't change their relative links to root-absolute paths. The form's redirect is resolved from the current page URL, so it points to `thank-you.html` on the same published site.

## Form behavior and setup

The form sends a `POST` to `https://formsubmit.co/softwareupload2025@gmail.com` and includes:

- Required parent name (`name="name"`, minimum 2 characters) and parent email (`name="email"`, native email validation).
- `_captcha=false` and `_subject="New Aeri Learning Free Activity Pack Request"`.
- A same-site `_next` redirect to `thank-you.html` (set by JavaScript, with a relative HTML fallback).
- A disabled-button `Sending...` state after submission.

FormSubmit may send an activation email to the recipient before forwarding the first real submission; the mailbox owner needs to confirm it. The confirmation page contains the requested copy and a direct download of the activity pack. An automated follow-up email with the PDF is not configured. Do not use the preview server to submit real parent data; test the final form only after the recipient and privacy details have been verified.

## Regenerate the activity pack (optional)

The included script uses Python 3 and Pillow. From the project root:

```bash
python3 -m pip install Pillow
python3 scripts/generate_activity_pack.py
```

It writes `assets/documents/aeri-learning-activity-pack.pdf`.
