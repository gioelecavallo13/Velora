/**
 * Componente Velora "dropdown" (10.5).
 *
 * Trigger generico con pannello: si attacca a qualunque elemento con
 * `data-velora-component="dropdown"` purche` contenga un `<button>` /
 * elemento focusabile come trigger e un sotto-elemento con classe
 * `velora-dropdown__panel` come pannello.
 *
 * E` cugino di `header-menu` ma resta separato: la geometria, il
 * posizionamento e i casi d'uso (link/btn inline vs voce di header) sono
 * abbastanza diversi da preferire due componenti specializzati piuttosto
 * che un super-componente con feature flag. Quando avremo bisogno di
 * `tooltip` + `dropdown` + `dialog` con stessa primitiva di "popup
 * controller" la estrarremo (probabilmente in v0.3+).
 */

const OPEN_CLASS = "is-open";
const TRIGGER_SELECTORS = [
    "button.velora-link-dropdown",
    "button.velora-btn",
];
const PANEL_SELECTOR = ".velora-dropdown__panel";

const openWrappers = new Set();

function findTrigger(wrapper) {
    for (const sel of TRIGGER_SELECTORS) {
        const t = wrapper.querySelector(sel);
        if (t) return t;
    }
    return wrapper.querySelector("button");
}

function closeWrapper(wrapper) {
    if (!wrapper.classList.contains(OPEN_CLASS)) return;
    wrapper.classList.remove(OPEN_CLASS);
    const trigger = findTrigger(wrapper);
    if (trigger) trigger.setAttribute("aria-expanded", "false");
    openWrappers.delete(wrapper);
}

function closeAll() {
    openWrappers.forEach(closeWrapper);
}

function openWrapper(wrapper) {
    openWrappers.forEach((other) => {
        if (other !== wrapper) closeWrapper(other);
    });
    wrapper.classList.add(OPEN_CLASS);
    const trigger = findTrigger(wrapper);
    if (trigger) trigger.setAttribute("aria-expanded", "true");
    openWrappers.add(wrapper);
}

function isInside(target) {
    let node = target;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
        if (openWrappers.has(node)) return true;
        node = node.parentElement;
    }
    return false;
}

let listenersInstalled = false;
function installListeners() {
    if (listenersInstalled) return;
    listenersInstalled = true;
    document.addEventListener("click", (event) => {
        if (openWrappers.size === 0) return;
        if (!isInside(event.target)) closeAll();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && openWrappers.size > 0) {
            const first = openWrappers.values().next().value;
            const trigger = first && findTrigger(first);
            closeAll();
            if (trigger && typeof trigger.focus === "function") trigger.focus();
        }
    });
}

const dropdown = {
    name: "dropdown",
    init(el) {
        const trigger = findTrigger(el);
        const panel = el.querySelector(PANEL_SELECTOR);
        if (!trigger || !panel) return;
        installListeners();
        trigger.setAttribute("aria-expanded", "false");
        trigger.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            if (el.classList.contains(OPEN_CLASS)) closeWrapper(el);
            else openWrapper(el);
        });
        panel.addEventListener("click", (event) => {
            const link = event.target && event.target.closest && event.target.closest("a[href]");
            if (link) closeWrapper(el);
        });
    },
};

export default dropdown;
