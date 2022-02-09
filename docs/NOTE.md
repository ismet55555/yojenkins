# NOTE

## Live Server Preview

- Ensure you are in the `docs` directory
- `mkdocs serve`
- Open your browser to http://localhost:8000/

## Deploying documentation

The documentation is served from the `gh-pages` branch of this repository. This branch does
not contain any `yojenkins` code and is only updated using `mkdocs gh-deploy`

- Ensure you are in the `docs` directory
- `mkdocs gh-deploy --site-dir site --verbose --config-file mkdocs.yml`
