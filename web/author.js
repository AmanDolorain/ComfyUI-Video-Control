import { app } from "../../scripts/app.js";

const decorated = Symbol("videoControlAuthorFooter");

app.registerExtension({
    name: "VideoControl.AuthorCredit",
    nodeCreated(node) {
        if (node.comfyClass !== "VideoControl" || node[decorated]) return;
        node[decorated] = true;

        // Reserve a footer below the controls, rather than inserting a widget row.
        const computeSize = node.computeSize;
        node.computeSize = function (...args) {
            const size = computeSize.apply(this, args);
            return [Math.max(size[0], 300), size[1] + 24];
        };

        // Anchor to the actual node boundary, including after manual resizing.
        // Keep the lower-left package badge free and draw no clickable overlay.
        const drawForeground = node.onDrawForeground;
        node.onDrawForeground = function (ctx, ...args) {
            const result = drawForeground?.call(this, ctx, ...args);
            if (this.flags?.collapsed) return result;
            ctx.save();
            try {
                ctx.font = "10px sans-serif";
                ctx.fillStyle = "#9aa0a6";
                ctx.globalAlpha *= 0.7;
                ctx.textAlign = "right";
                ctx.textBaseline = "middle";
                ctx.fillText("Author: Aman", this.size[0] - 12, this.size[1] - 18);
            } finally {
                ctx.restore();
            }
            return result;
        };
        const minimum = node.computeSize();
        node.setSize([
            Math.max(node.size[0], minimum[0]),
            Math.max(node.size[1], minimum[1]),
        ]);
        node.setDirtyCanvas?.(true, true);
    },
});
