# pyconsg26 GitHub Pages Maintenance

This is a one-minute checklist to keep https://pyconsg26.mrpiti.dev healthy after updates.

## One-Minute Checklist

1. Confirm branch and files
- Push site updates to `main`.
- Ensure `index.html`, `styles.css`, and `slides.js` are in repository root.
- Ensure `CNAME` exists and contains exactly `pyconsg26.mrpiti.dev`.

2. Confirm GitHub Pages settings
- Repository Settings -> Pages.
- Source: Deploy from a branch.
- Branch: `main` and folder: `/(root)`.
- Custom domain is set to `pyconsg26.mrpiti.dev`.

3. Confirm DNS in Cloudflare
- Record type: `CNAME`.
- Name: `pyconsg26`.
- Target: `ninefyi.github.io`.
- Proxy status: `DNS only` (recommended for stable certificate behavior).

4. Confirm HTTPS and live site
- In Pages settings, `Enforce HTTPS` is enabled.
- Open https://pyconsg26.mrpiti.dev and verify slides load.
- Test one full slide navigation cycle (next/previous + sidebar toggle).

5. Quick metadata sanity check
- In `index.html`, verify canonical and `og:url` use `https://pyconsg26.mrpiti.dev/`.

## If Something Breaks

1. Wait 1-5 minutes for DNS/cache propagation after changes.
2. Re-check `CNAME` file content and Cloudflare CNAME target.
3. In GitHub Pages settings, remove and re-add custom domain, then save.
4. Confirm no accidental base path assumptions in asset links (they should remain relative, e.g., `styles.css`).
