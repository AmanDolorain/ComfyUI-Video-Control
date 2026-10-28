import { app } from "../../scripts/app.js";

const installed = Symbol("videoControlFooter");
const states = new Set();
let observer;
let scheduled = false;

function makeCredit() {
    const label = document.createElement("span");
    label.className = "video-control-author-credit";
    label.textContent = "♪ Aman Dolorain";
    label.title = "ComfyUI-Video-Control — ♪ Aman Dolorain";
    Object.assign(label.style, {
        marginLeft: "auto",
        flex: "0 0 auto",
        alignSelf: "center",
        font: '600 10px/20px "Segoe UI", sans-serif',
        letterSpacing: "0.45px",
        color: "#ffffff",
        opacity: "1",
        whiteSpace: "nowrap",
        pointerEvents: "none",
        userSelect: "none",
        padding: "0",
    });
    return label;
}

function clearMount(state) {
    state.label?.remove();
    state.ownRow?.remove();
    state.label = state.ownRow = state.root = null;
}

function syncCredits() {
    scheduled = false;
    const activeGraph = app.canvas?.graph;
    const roots = [...document.querySelectorAll(".lg-node[data-node-id]")];
    for (const state of states) {
        const { node } = state;
        const root = node.graph === activeGraph && !node.flags?.collapsed
            ? roots.find((element) => element.dataset.nodeId === String(node.id))
            : null;
        if (!root || root.dataset.collapsed) {
            if (state.root) clearMount(state);
            continue;
        }
        if (state.root && state.root !== root) clearMount(state);
        const body = [...root.querySelectorAll("[data-testid]")].find(
            (element) => element.dataset.testid === `node-body-${node.id}`,
        );
        if (!body) continue;
        // NodeBadges.vue renders a direct .mt-auto flex row in the Vue node body.
        // Reuse the footer row and remove only this package's old badge.
        let row = [...body.children].find(
            (element) => element.classList.contains("mt-auto") && element !== state.ownRow,
        );
        // Keep branding in its own reserved footer, apart from controls.
        if (row) {
            for (const element of row.querySelectorAll("*")) {
                if (["Video-Control", "ComfyUI-Video-Control"].includes(element.textContent.trim())) {
                    element.style.display = "none";
                }
            }
        }
        if (!state.ownRow?.isConnected) {
            const footer = document.createElement("div");
            footer.className = "video-control-credit-row";
            Object.assign(footer.style, {
                display: "flex", alignItems: "center", justifyContent: "flex-end",
                boxSizing: "border-box", minHeight: "48px", flexShrink: "0",
                margin: "18px 14px 0", padding: "12px 2px 14px",
                borderTop: "1px solid rgba(255,255,255,0.12)",
            });
            body.append(footer);
            state.ownRow = footer;
        }
        row = state.ownRow;
        if (!state.label) state.label = makeCredit();
        if (state.label.parentElement !== row) row.append(state.label);
        state.root = root;
    }
}

function scheduleSync() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(syncCredits);
}

function observeNodes() {
    if (observer) return;
    observer = new MutationObserver(scheduleSync);
    observer.observe(document.body, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ["data-collapsed", "data-node-id"],
    });
}

app.registerExtension({
    name: "VideoControl.AuthorCredit",
    setup() { observeNodes(); scheduleSync(); },
    nodeCreated(node) {
        if (node.comfyClass !== "VideoControl" || node[installed]) return;
        node[installed] = true;
        const state = { node, label: null, ownRow: null, root: null };
        states.add(state);

        // Classic canvas fallback. Vue nodes use the DOM footer above instead.
        const previousComputeSize = node.computeSize;
        node.computeSize = function (...args) {
            const size = previousComputeSize.apply(this, args);
            return [Math.max(size[0], 300), size[1] + 66];
        };
        const previousDraw = node.onDrawForeground;
        node.onDrawForeground = function (ctx, ...args) {
            const result = previousDraw?.call(this, ctx, ...args);
            if (this.flags?.collapsed || state.root?.isConnected) return result;
            ctx.save();
            try {
                ctx.strokeStyle = "rgba(255,255,255,0.12)";
                ctx.beginPath();
                ctx.moveTo(14, this.size[1] - 46);
                ctx.lineTo(this.size[0] - 14, this.size[1] - 46);
                ctx.stroke();
                ctx.font = "600 10px Segoe UI, sans-serif";
                ctx.fillStyle = "#ffffff";
                ctx.textAlign = "right";
                ctx.textBaseline = "middle";
                ctx.fillText("♪ Aman Dolorain", this.size[0] - 16, this.size[1] - 24);
            } finally { ctx.restore(); }
            return result;
        };
        const previousRemoved = node.onRemoved;
        node.onRemoved = function (...args) {
            states.delete(state);
            clearMount(state);
            return previousRemoved?.apply(this, args);
        };
        const minimum = node.computeSize();
        node.setSize([Math.max(node.size[0], minimum[0]), Math.max(node.size[1], minimum[1])]);
        observeNodes();
        scheduleSync();
        node.setDirtyCanvas?.(true, true);
    },
});
