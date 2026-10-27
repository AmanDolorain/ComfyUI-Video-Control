# Verification for 1.1.6

## Source review

Reviewed the official ComfyUI frontend sources for the Vue node container and bottom badge row:

- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/renderer/extensions/vueNodes/components/LGraphNode.vue
- https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/renderer/extensions/vueNodes/components/NodeBadges.vue
- https://github.com/Comfy-Org/ComfyUI-Manager/blob/main/glob/manager_core.py
- https://github.com/Comfy-Org/ComfyUI-Manager/blob/main/glob/manager_server.py
- https://github.com/Comfy-Org/ComfyUI-Manager/blob/main/glob/cnr_utils.py

The Vue implementation places the package/source badges in a direct bottom `.mt-auto` row inside the node body. This update attaches the author to that same row. It does not rely solely on the classic canvas foreground callback.

Manager obtains the title of a Registry-only pack from the Registry node name. The channel-list mode and Registry cache are distinct in the reviewed Manager source. A correct Registry name can coexist with an old Manager title until its Registry metadata is refreshed.

## Checks performed

- All ten Python unit tests pass, including mocked tensor allocation.
- A DOM test checks the native Vue row attachment, alignment styles, duplicate prevention, hidden-badge fallback, collapse/expand, remount and cleanup.
- A headless Chromium test uses a fixture reproducing the relevant Vue node-body and badge-row structure. It verifies matching vertical centers for the package badge and full author name, right alignment after resize, non-interactive text, hidden/restored badges, collapse/expand, cleanup and the classic canvas fallback coordinates.

These are not a full ComfyUI installation, model-generation test or a guarantee for every historical/future frontend release. The installed frontend remains the final integration check.

## Update checklist

Keep the Registry name `ComfyUI-Video-Control`; do not rename it again if already correct. Upload the contents of this package, including `web/author.js`, and commit with `Fix author footer compatibility and full author credit v1.1.6`.

The `.github` directory and `.gitignore` are unchanged from 1.1.5. Author metadata and LICENSE now use Aman Dolorain. After successful publishing, update the installed pack, restart ComfyUI, hard-refresh the browser, and inspect a fresh node.

If Manager still shows the old title, keep DB Channel remote and Channel default, use Check Update/Fetch Updates when available, and let `FETCH ComfyRegistry Data [DONE]` finish before reopening the list. Do not delete old versions or publish another patch just to refresh a cached title.
