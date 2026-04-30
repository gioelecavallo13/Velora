/**
 * Runtime Velora: registry, scan, MutationObserver, bootstrap, global `window.Velora`.
 */

import toast from "./components/toast.js";

/** Deve coincidere con `velora_ui.__version__` / `pyproject.toml`. */
const VELORA_VERSION = "0.8.0";
const ATTR = "data-velora-component";
const INIT_FLAG = "__veloraInitialized";

const registry = new Map();

/**
 * @param {{name: string, init: (el: HTMLElement) => void}} component
 */
function register(component) {
    if (!component || typeof component !== "object") {
        throw new TypeError("Velora.register: argomento non valido (atteso oggetto)");
    }
    if (typeof component.name !== "string" || component.name.length === 0) {
        throw new TypeError("Velora.register: 'name' deve essere una stringa non vuota");
    }
    if (typeof component.init !== "function") {
        throw new TypeError("Velora.register: 'init' deve essere una funzione");
    }
    if (registry.has(component.name)) {
        console.warn(
            "[velora] componente '" + component.name + "' gia' registrato, sovrascrivo"
        );
    }
    registry.set(component.name, component);
}

/**
 * @param {Element|Document} [root]
 */
function scan(root) {
    if (!root) {
        root = document;
    }
    const elements = root.querySelectorAll(`[${ATTR}]`);
    elements.forEach((el) => {
        if (el[INIT_FLAG]) {
            return;
        }
        const name = el.getAttribute(ATTR);
        const component = registry.get(name);
        if (!component) {
            return;
        }
        try {
            component.init(el);
            el[INIT_FLAG] = true;
        } catch (err) {
            console.error(`[velora] errore in init('${name}')`, err);
        }
    });
}

function startObserver() {
    if (!("MutationObserver" in window)) {
        return;
    }
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    scan(node);
                }
            });
        });
    });
    observer.observe(document.body, { childList: true, subtree: true });
}

function bootstrap() {
    scan();
    startObserver();
}

/**
 * @param {(reg: (c: unknown) => void) => void} registerComponents callback che registra tutti i componenti
 */
export function startWithRegistrator(registerComponents) {
    registerComponents(register);

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bootstrap);
    } else {
        bootstrap();
    }

    const Velora = {
        version: VELORA_VERSION,
        register,
        scan,
    };
    Velora.toast = toast;

    if (typeof window !== "undefined") {
        window.Velora = Velora;
        window.Velora.toast = toast;
    }
}

export { register, scan, VELORA_VERSION };
