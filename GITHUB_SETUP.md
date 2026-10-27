# Publishing Video Control on GitHub

Author: Aman

The repository is https://github.com/AmanDolorain/ComfyUI-Video-Control. This update package is prepared locally; it is not published until its files are committed to that repository.

## Update the existing repository

1. Extract this update ZIP and open the inner VideoControl directory.
2. In the repository, choose Add file / Upload files.
3. Upload the contents of that directory at the repository root, keeping the tests and .github subdirectories intact. Do not upload the outer folder or ZIP.
4. Use the commit message `Fix searchable title and bottom-corner author credit (v1.1.5)`.
5. Check the Actions tab after committing. An actual ComfyUI generation test is still separate.
6. Existing users can update their Git installation and restart ComfyUI.

The following sections also describe creating a separate repository if needed.

## Create an account and repository

1. If needed, create your account at https://github.com/signup and verify your email. Keep your password private.
2. Sign in and open https://github.com/new.
3. Use `ComfyUI-Video-Control` as the repository name.
4. Suggested description: `Shared video timing, empty latent and planned video metadata for ComfyUI. Author: Aman.`
5. Choose Public to let others install from the repository URL. This package already includes a README and MIT license.
6. Create the repository. Upload the contents **inside** the extracted `VideoControl` directory, rather than uploading the ZIP or nesting that directory inside the repository.
7. Commit the files. The repository root should contain `__init__.py`, `calculations.py`, `README.md`, `pyproject.toml`, `LICENSE`, and `tests`.

The README becomes the main repository page. Add the description in About and use topics such as `comfyui`, `custom-nodes`, and `video`.

## Publish with Git

Create an empty repository first. Open a terminal inside the extracted project directory. Replace USERNAME below with your actual GitHub username.

```bash
git init
git add .
git commit -m "Initial release: Video Control"
git branch -M main
git remote add origin https://github.com/USERNAME/ComfyUI-Video-Control.git
git push -u origin main
```

Configure your Git name and email if Git requests them. Authenticate through your browser or credential manager; never put credentials in the source files. Git includes `.github` and `.gitignore`; browser uploads may omit hidden files. The `.github` directory contains the automatic test workflow.

## Install from the repository URL

Copy the HTTPS URL from the repository's Code menu. Use your ComfyUI Manager's Git URL installation option if available, or run the following inside `ComfyUI/custom_nodes`:

```bash
git clone https://github.com/AmanDolorain/ComfyUI-Video-Control.git
```

Restart ComfyUI. Do not keep another active copy installed from the ZIP.

For future updates, run `git pull` inside the installed repository directory and restart ComfyUI.

GitHub hosts the source and update history. Installation still downloads a local copy, and ComfyUI and models still run on your computer.

## Registry listing

Installing from a Git URL does not require a Comfy Registry listing. Searchable listings, publisher verification and author display may require separate registration. No publisher ID has been invented for this package.

## Public files and excluded local files

Publish the Python source, tests, README, development guide, setup guide, license, package metadata, `.gitignore` and `.github/workflows/tests.yml`. The dot-prefixed files are project configuration, not private files.

Exclude credentials, `.env` files, private keys, logs, Python caches and local environments. `.gitignore` applies to Git tracking; it does not hide already published files and does not filter files manually selected for browser upload. Review browser uploads before committing. This package contains no model weights or account credentials.
