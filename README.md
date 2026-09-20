# MDM — Marth Download Manager Website

The official website for **MDM (Marth Download Manager)** — a modern desktop download manager for efficient, reliable downloads with browser integration, queue management, pause and resume, and real-time download monitoring.

🌐 **Live at:** [https://marthdownloadmanager.github.io](https://marthdownloadmanager.github.io)

---

## What's Included

- **Pages & Routes:**
  - `/` — Homepage with interactive installation commands, feature highlights, and desktop app preview.
  - `/features` — Detailed capability breakdown (concurrent downloads, queueing, retry & recovery, browser integration, etc.).
  - `/how-it-works` — Visual step-by-step pipeline.
  - `/downloads` — Live GitHub release integration fetching latest artifacts directly from `MS-DevX/mdm-releases`.
- **Assets:**
  - Icons, favicon, fonts, and stylesheets.
- **SPA Routing:**
  - Client-side routing with pre-built route entry points and `404.html` fallback for GitHub Pages.

---

## How to Run Locally

### Option 1: Python (No installation needed)
```bash
python3 server.py 3000
```
Then open [http://localhost:3000](http://localhost:3000) in your browser.

### Option 2: Node.js / NPM
```bash
npm start
# OR
npm run serve
```

---

## Deployment

This site is designed for static hosting. To deploy to GitHub Pages:

```bash
git init
git branch -M main
git add .
git commit -m "Deploy MDM website"
git remote add origin https://github.com/MS-DevX/marthdownloadmanager.github.io.git
git push -u origin main
```

Then enable GitHub Pages in your repository settings (Settings → Pages → Source: Deploy from a branch → `main` / root).

---

## License

MIT
