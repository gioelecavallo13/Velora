/**
 * Velora UI - entry point JavaScript
 *
 * Component registry + auto-init via DOMContentLoaded e MutationObserver.
 *
 * Architettura (vedi piano sezione 8):
 *   - Ogni componente vive in un proprio file ES module sotto components/
 *   - Esporta { name, init(el) } e si registra qui
 *   - Al DOMContentLoaded viene fatto uno scan iniziale del DOM cercando
 *     elementi con `data-velora-component="<name>"`
 *   - Un MutationObserver osserva il body e auto-inizializza i nuovi nodi
 *     (es. dialog modali aperti via AJAX, righe di tabella aggiunte, ecc.)
 *
 * In v0.1 il registry e` minimale: il componente `sidebar-toggle` arriva in
 * M2 (Fase 4), `toast.js` e `form.js` in M5 (Fase 7). Questo file fornisce
 * l'infrastruttura runtime e importa i componenti registrati di default.
 */

const VELORA_VERSION = "0.0.1";
const ATTR = "data-velora-component";
const INIT_FLAG = "__veloraInitialized";

const registry = new Map();

/**
 * Registra un componente.
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
 * Esegue lo scan di un sottoalbero del DOM cercando elementi
 * `data-velora-component="..."` e inizializzando il componente
 * corrispondente se registrato e non gia` inizializzato.
 *
 * @param {Element|Document} root nodo radice da cui partire (default: document)
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

/**
 * Avvia l'osservazione del DOM per auto-inizializzare componenti dinamici.
 * Chiamata internamente al DOMContentLoaded; non serve invocarla a mano.
 */
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

if (typeof window !== "undefined") {
    window.Velora = Velora;
}

// Componenti registrati di default. Gli import sono ESM-hoisted: i componenti
// non importano da questo file per evitare cicli; ognuno esporta un oggetto
// {name, init} che noi passiamo al registry tramite register().
import sidebarToggle from "./components/sidebar.js";
import confirmComponent from "./components/confirm.js";

register(sidebarToggle);
register(confirmComponent);

export default Velora;
export { register, scan, VELORA_VERSION };

