# Publish Video Control to Comfy Registry

Publisher ID: `amandolorain`
Display name: `Video Control`
Package ID: `comfyui-video-control`
Prepared version: `1.1.2`

This package is prepared for publication. Registry availability is not confirmed until publishing and any applicable registry checks succeed. If the package ID is already owned by another publisher, choose a new available ID before the first successful publication.

## 1. Create the publishing secret

In Comfy Registry, select the amandolorain publisher and create a new API key. A descriptive key name such as `video-control-github` is sufficient. Copy the generated key privately.

In the GitHub repository, open Settings > Secrets and variables > Actions > New repository secret. Name it `REGISTRY_ACCESS_TOKEN` and paste the key as the secret value. Save it. Never put the key in a source file or chat message.

## 2. Upload the package update

Upload the contents inside VideoControl to the repository root, including the new `.github/workflows/publish.yml`. The existing `.github/workflows/tests.yml` and `.gitignore` are unchanged. If browser upload omits the .github directory, use Add file > Create new file, name it `.github/workflows/publish.yml`, and paste the contents from this package.

Suggested commit message: `Configure Comfy Registry publishing v1.1.2`.

## 3. Publish and verify

The publish workflow runs when pyproject.toml changes on main. Alternatively, go to Actions > Publish to Comfy Registry > Run workflow and select main. Tests run before publication. If a workflow fails, inspect the failed step; do not assume the node is published.

After success, check the Registry publisher page for the node and version. Registry validation and Manager cache refresh can delay visibility. Check the registry status rather than assuming immediate Manager availability.

For later releases, increment the version in pyproject.toml, __init__.py and README, commit the changes and check Actions. An already published version cannot be overwritten. GitHub commits without a version bump do not replace a published registry release.

GitHub hosts the source, the Registry distributes versioned packages, and Manager installs a local copy. Manager updates still require an update action and a ComfyUI restart.
