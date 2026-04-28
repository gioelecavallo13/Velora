/**
 * Componente Velora "dialog" (10.6).
 *
 * Trigger di apertura modale. Si attacca a qualunque elemento con
 * `data-velora-component="dialog"` e supporta due modalita`:
 *
 *   - **Inline**: `data-dialog-target="#dialog-id"`. Il dialog e` gia` nel
 *     DOM (un nodo `.velora-dialog` con id corrispondente). Il componente
 *     lo mostra applicando `is-open`.
 *
 *   - **Remote**: `data-dialog-url="/path/to/fragment"`. Il componente
 *     fa `fetch(url)`, inietta l'HTML in un dialog generato al volo,
 *     poi mostra. Il fragment dovrebbe essere HTML "pulito" (no <html>,
 *     no <body>): in caso contrario lo prendiamo cosi` come arriva.
 *
 * Chiusura: click sul backdrop, click sul pulsante `[data-dialog-close]`
 * dentro al dialog, tasto ESC.
 *
 * NB: focus management e` "soft" (focus al primo focusable + restore al
 * trigger su close). Il focus trapping completo richiederebbe un componente
 * piu` corposo: rimandato a una eventuale v0.3 se l'esperienza lo richiede.
 */

const ATTR_TARGET = "data-dialog-target";
const ATTR_URL = "data-dialog-url";
const ATTR_SIZE = "data-dialog-size";
const ATTR_TITLE = "data-dialog-title";

const OPEN_CLASS = "is-open";
const BODY_LOCK_CLASS = "velora-app--dialog-open";

let activeDialog = null;
let activeTrigger = null;

function lockBody() {
    if (document.body) document.body.classList.add(BODY_LOCK_CLASS);
}

function unlockBody() {
    if (document.body) document.body.classList.remove(BODY_LOCK_CLASS);
}

function focusFirst(dialog) {
    const focusable = dialog.querySelector(
        "button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])"
    );
    if (focusable && typeof focusable.focus === "function") {
        focusable.focus();
    }
}

function open(dialog, trigger) {
    if (!dialog) return;
    if (activeDialog && activeDialog !== dialog) close();
    dialog.classList.add(OPEN_CLASS);
    dialog.setAttribute("aria-hidden", "false");
    activeDialog = dialog;
    activeTrigger = trigger || null;
    lockBody();
    // Defer focus per dare tempo al CSS di applicare display:flex
    window.setTimeout(() => focusFirst(dialog), 0);
}

function close() {
    if (!activeDialog) return;
    activeDialog.classList.remove(OPEN_CLASS);
    activeDialog.setAttribute("aria-hidden", "true");
    // Se il dialog era stato generato al volo, lo rimuoviamo per evitare
    // accumulo nel DOM su aperture remote ripetute.
    if (activeDialog.dataset.veloraDialogGenerated === "1") {
        activeDialog.remove();
    }
    activeDialog = null;
    unlockBody();
    if (activeTrigger && typeof activeTrigger.focus === "function") {
        activeTrigger.focus();
    }
    activeTrigger = null;
}

function buildShellDialog({ title, size }) {
    const dialog = document.createElement("div");
    dialog.className = `velora-dialog velora-dialog--${size || "md"}`;
    dialog.setAttribute("role", "dialog");
    dialog.setAttribute("aria-modal", "true");
    dialog.setAttribute("aria-hidden", "true");
    dialog.dataset.veloraDialogGenerated = "1";
    dialog.innerHTML =
        '<div class="velora-dialog__backdrop" data-dialog-close></div>' +
        '<div class="velora-dialog__panel" role="document">' +
        (title
            ? `<header class="velora-dialog__header"><h2 class="velora-dialog__title">${escapeHtml(title)}</h2><button type="button" class="velora-dialog__close" data-dialog-close aria-label="Chiudi">&times;</button></header>`
            : '<button type="button" class="velora-dialog__close velora-dialog__close--floating" data-dialog-close aria-label="Chiudi">&times;</button>') +
        '<div class="velora-dialog__body" data-dialog-body></div>' +
        "</div>";
    document.body.appendChild(dialog);
    return dialog;
}

function escapeHtml(s) {
    const span = document.createElement("span");
    span.textContent = s;
    return span.innerHTML;
}

async function openRemote({ url, size, title }, trigger) {
    const dialog = buildShellDialog({ title, size });
    const body = dialog.querySelector("[data-dialog-body]");
    body.innerHTML = '<p class="velora-dialog__loading">Caricamento...</p>';
    open(dialog, trigger);
    try {
        const resp = await fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const html = await resp.text();
        body.innerHTML = html;
        // Esegue scan Velora per inizializzare i componenti del fragment
        if (window.Velora && typeof window.Velora.scan === "function") {
            window.Velora.scan(body);
        }
        focusFirst(dialog);
    } catch (err) {
        body.innerHTML = `<p class="velora-dialog__error">Errore: ${escapeHtml(err.message || String(err))}</p>`;
    }
}

function ensureInlineDialogShape(dialog) {
    // Garantisce che un dialog inline abbia gli attributi ARIA di base senza
    // ricostruirlo: il dev puo` aver scritto solo `<div class="velora-dialog">...</div>`.
    if (!dialog.hasAttribute("role")) dialog.setAttribute("role", "dialog");
    if (!dialog.hasAttribute("aria-modal")) dialog.setAttribute("aria-modal", "true");
    if (!dialog.hasAttribute("aria-hidden")) dialog.setAttribute("aria-hidden", "true");
}

let globalListenersInstalled = false;
function installGlobal() {
    if (globalListenersInstalled) return;
    globalListenersInstalled = true;
    document.addEventListener("click", (event) => {
        if (!activeDialog) return;
        const target = event.target;
        if (target && target.closest && target.closest("[data-dialog-close]")) {
            event.preventDefault();
            close();
        }
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && activeDialog) {
            close();
        }
    });
}

const dialog = {
    name: "dialog",
    init(el) {
        installGlobal();
        const targetSel = el.getAttribute(ATTR_TARGET) || "";
        const url = el.getAttribute(ATTR_URL) || "";
        const size = el.getAttribute(ATTR_SIZE) || "md";
        const title = el.getAttribute(ATTR_TITLE) || "";
        if (!targetSel && !url) return;
        el.addEventListener("click", (event) => {
            event.preventDefault();
            if (targetSel) {
                const inline = document.querySelector(targetSel);
                if (inline) {
                    ensureInlineDialogShape(inline);
                    open(inline, el);
                }
            } else {
                openRemote({ url, size, title }, el);
            }
        });
    },
};

export default dialog;
export { open as openDialog, close as closeDialog };
