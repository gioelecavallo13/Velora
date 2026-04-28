/**
 * Componente Velora "sidebar-toggle".
 *
 * Si registra sul registry di Velora (vedi js/src/velora.js) e si attacca
 * a qualunque elemento con `data-velora-component="sidebar-toggle"`. Al
 * click commuta la classe `velora-app--sidebar-collapsed` sul body e
 * persiste lo stato in localStorage con chiave `velora.sidebar.collapsed`,
 * cosi` la preferenza dell'utente sopravvive al reload.
 *
 * Allo script-load (prima del DOMContentLoaded) ripristiniamo subito lo
 * stato salvato per evitare il flash della sidebar piena -> ridotta:
 * applichiamo la classe direttamente a document.body se gia` parsato, o
 * registriamo un listener `DOMContentLoaded` come fallback.
 */

// Nota: questo modulo NON importa da `../velora.js` per evitare cicli ESM.
// Esporta un oggetto componente {name, init}; e` `velora.js` (entry point)
// che lo importa e lo passa al registry tramite Velora.register(...).

const STORAGE_KEY = "velora.sidebar.collapsed";
const COLLAPSED_CLASS = "velora-app--sidebar-collapsed";

function readPersistedState() {
    try {
        return window.localStorage.getItem(STORAGE_KEY) === "1";
    } catch (_err) {
        return false;
    }
}

function writePersistedState(collapsed) {
    try {
        window.localStorage.setItem(STORAGE_KEY, collapsed ? "1" : "0");
    } catch (_err) {
        // localStorage indisponibile (modalita` privata, quota): silenzioso
    }
}

function applyState(collapsed) {
    if (!document.body) {
        return;
    }
    document.body.classList.toggle(COLLAPSED_CLASS, collapsed);
}

function restoreInitialState() {
    const collapsed = readPersistedState();
    if (document.body) {
        applyState(collapsed);
    } else {
        document.addEventListener("DOMContentLoaded", () => applyState(collapsed));
    }
}

restoreInitialState();

const sidebarToggle = {
    name: "sidebar-toggle",
    init(el) {
        el.addEventListener("click", () => {
            const next = !document.body.classList.contains(COLLAPSED_CLASS);
            applyState(next);
            writePersistedState(next);
            el.setAttribute("aria-pressed", next ? "true" : "false");
        });
        el.setAttribute(
            "aria-pressed",
            document.body.classList.contains(COLLAPSED_CLASS) ? "true" : "false",
        );
    },
};

export default sidebarToggle;
