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
        marginLeft: "0",
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
                display: "flex", alignItems: "center", justifyContent: "center",
                boxSizing: "border-box", minHeight: "30px", flexShrink: "0",
                margin: "0", padding: "5px 14px",
                width: "100%", borderRadius: "0 0 10px 10px",
                
            });
            root.append(footer);
            state.ownRow = footer;
        }
        row = state.ownRow;
        // Sample the visible title bar so custom node colors and themes stay in sync.
        const header = root.querySelector('[data-testid="node-header"], .lg-node-header, .node-header')
            || [...root.children].find(el => el !== row && el !== body && !el.contains(body));
        let color = node.color || "#2e3440";
        if (header) {
            const candidates = [header, ...header.querySelectorAll("*")];
            for (const el of candidates) {
                const bg = getComputedStyle(el).backgroundColor;
                if (bg && bg !== "transparent" && bg !== "rgba(0, 0, 0, 0)") {
                    color = bg;
                    break;
                }
            }
        }
        if (row.style.backgroundColor !== color) row.style.backgroundColor = color;
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
    observer = new MutationObserver(records => {
        if (records.some(record => !record.target.closest?.(".video-control-credit-row"))) scheduleSync();
    });
    observer.observe(document.body, {
        childList: true, subtree: true, attributes: true,
        attributeFilter: ["data-collapsed", "data-node-id", "class", "style"],
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
            return [Math.max(size[0], 300), size[1] + 30];
        };
        const previousDraw = node.onDrawForeground;
        node.onDrawForeground = function (ctx, ...args) {
            const result = previousDraw?.call(this, ctx, ...args);
            if (this.flags?.collapsed || state.root?.isConnected) return result;
            ctx.save();
            try {
                ctx.fillStyle = this.color || LiteGraph.NODE_DEFAULT_COLOR || "#2e3440";
                ctx.beginPath();
                ctx.roundRect(0, this.size[1] - 30, this.size[0], 30, [0, 0, 10, 10]);
                ctx.fill();
                ctx.font = "600 10px Segoe UI, sans-serif";
                ctx.fillStyle = "#ffffff";
                ctx.textAlign = "center";
                ctx.textBaseline = "middle";
                ctx.fillText("♪ Aman Dolorain", this.size[0] / 2, this.size[1] - 15);
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
