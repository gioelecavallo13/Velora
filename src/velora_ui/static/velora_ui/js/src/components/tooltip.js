/**
 * Componente Velora "tooltip" (10.3).
 *
 * Si attacca a qualunque elemento con `data-velora-component="tooltip"` e
 * `data-tooltip-text="..."`. Mostra un balloon flottante in `<body>` su
 * hover/focus, lo nasconde su mouseleave/blur/Escape.
 *
 * Singolo balloon globale riusato fra tutti i trigger: niente memory
 * leak da N nodi creati in DOM.
 */

const ATTR_TEXT = "data-tooltip-text";
const ATTR_PLACEMENT = "data-tooltip-placement";
const ATTR_DELAY = "data-tooltip-delay";

let tooltipEl = null;
let activeTrigger = null;
let showTimer = null;

function ensureTooltipEl() {
    if (tooltipEl) {
        return tooltipEl;
    }
    tooltipEl = document.createElement("div");
    tooltipEl.className = "velora-tooltip";
    tooltipEl.setAttribute("role", "tooltip");
    tooltipEl.setAttribute("aria-hidden", "true");
    document.body.appendChild(tooltipEl);
    return tooltipEl;
}

function positionTooltip(trigger, placement) {
    const el = ensureTooltipEl();
    const rect = trigger.getBoundingClientRect();
    const tipRect = el.getBoundingClientRect();
    const margin = 8;
    let top = 0;
    let left = 0;
    switch (placement) {
        case "bottom":
            top = rect.bottom + margin;
            left = rect.left + rect.width / 2 - tipRect.width / 2;
            break;
        case "left":
            top = rect.top + rect.height / 2 - tipRect.height / 2;
            left = rect.left - tipRect.width - margin;
            break;
        case "right":
            top = rect.top + rect.height / 2 - tipRect.height / 2;
            left = rect.right + margin;
            break;
        case "top":
        default:
            top = rect.top - tipRect.height - margin;
            left = rect.left + rect.width / 2 - tipRect.width / 2;
            break;
    }
    // Clamp dentro al viewport (margine di 4px)
    const maxLeft = window.innerWidth - tipRect.width - 4;
    const maxTop = window.innerHeight - tipRect.height - 4;
    if (left < 4) left = 4;
    if (top < 4) top = 4;
    if (left > maxLeft) left = maxLeft;
    if (top > maxTop) top = maxTop;
    el.style.top = `${Math.round(top + window.scrollY)}px`;
    el.style.left = `${Math.round(left + window.scrollX)}px`;
    el.setAttribute("data-placement", placement);
}

function showTooltip(trigger) {
    const el = ensureTooltipEl();
    const text = trigger.getAttribute(ATTR_TEXT) || "";
    const placement = trigger.getAttribute(ATTR_PLACEMENT) || "top";
    el.textContent = text;
    el.classList.add("is-open");
    el.setAttribute("aria-hidden", "false");
    activeTrigger = trigger;
    // Posiziono dopo aver settato il testo (cosi` getBoundingClientRect e` attendibile)
    positionTooltip(trigger, placement);
}

function hideTooltip() {
    if (!tooltipEl) {
        return;
    }
    tooltipEl.classList.remove("is-open");
    tooltipEl.setAttribute("aria-hidden", "true");
    activeTrigger = null;
}

function scheduleShow(trigger) {
    cancelShow();
    let delay = parseInt(trigger.getAttribute(ATTR_DELAY) || "200", 10);
    if (isNaN(delay) || delay < 0) {
        delay = 0;
    }
    showTimer = window.setTimeout(() => showTooltip(trigger), delay);
}

function cancelShow() {
    if (showTimer !== null) {
        window.clearTimeout(showTimer);
        showTimer = null;
    }
}

let escListenerInstalled = false;
function installEscListener() {
    if (escListenerInstalled) return;
    escListenerInstalled = true;
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && activeTrigger) {
            cancelShow();
            hideTooltip();
        }
    });
}

const tooltip = {
    name: "tooltip",
    init(el) {
        installEscListener();
        el.addEventListener("mouseenter", () => scheduleShow(el));
        el.addEventListener("mouseleave", () => {
            cancelShow();
            hideTooltip();
        });
        el.addEventListener("focus", () => scheduleShow(el));
        el.addEventListener("blur", () => {
            cancelShow();
            hideTooltip();
        });
    },
};

export default tooltip;
