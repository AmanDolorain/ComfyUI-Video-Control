import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "VideoControl.AuthorCredit",
    nodeCreated(node) {
        if (node.comfyClass !== "VideoControl") return;
        if (node.widgets?.some((widget) => widget.name === "video_control_author")) return;

        const label = document.createElement("div");
        label.textContent = "Author: Aman";
        label.title = "Video Control — Author: Aman";
        Object.assign(label.style, {
            color: "var(--descrip-text, #b8b8b8)",
            font: "10px sans-serif",
            opacity: "0.65",
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "flex-end",
            boxSizing: "border-box",
            width: "100%",
            height: "18px",
            padding: "0 8px 2px 0",
            whiteSpace: "nowrap",
            pointerEvents: "none",
        });

        // Display only: no model input, editable setting, output, or saved value.
        const widget = node.addDOMWidget("video_control_author", "video_control_credit", label, {
            serialize: false,
            hideOnZoom: true,
            getValue: () => undefined,
            setValue: () => {},
        });
        widget.computeSize = () => [0, 18];
        const size = node.computeSize();
        node.setSize([Math.max(node.size[0], size[0]), Math.max(node.size[1], size[1])]);
    },
});
