# Go Journey 1.0

A single-page, discovery-first Go learning app.

## Render deployment

1. Create a GitHub repository and place all files from this folder in its root.
2. In Render, choose **New > Blueprint** and connect the repository. Render reads `render.yaml`.
3. Confirm the static site and deploy.

Manual alternative: choose **New > Static Site**, connect the repository, leave the build command empty, and use `.` as the publish directory.

## Local test

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000`.
