/**
 * Toast manager di Velora UI (M5 - Fase 7 del piano).
 *
 * Espone l'API pubblica `Velora.toast.success(msg, opts)`, `.error()`,
 * `.warning()`, `.info()` per emettere notifiche temporanee dalla
 * pagina, e legge a DOMContentLoaded eventuali payload emessi dal
 * template tag {% velora_toast_messages %} (collegato al framework
 * `django.contrib.messages`).
 *
 * Architettura:
 *   - un container fisso `.velora-toast-container` viene creato lazy al
 *     primo show() e ancorato a body con position:fixed
 *   - ogni toast e` un `<div class="velora-toast velora-toast--<variant>">`
 *     con close button e auto-dismiss configurabile (default 5s)
 *   - opzioni per chiamata: { duration:ms, dismissible:bool, persistent:bool }
 *     persistent=true disattiva l'auto-dismiss (utile per errori critici)
 *
 * Niente dipendenze esterne: ~80 righe di JS vanilla. Lo stile e` tutto
 * in _toast.scss.
 */

const CONTAINER_CLASS = "velora-toast-container";
const TOAST_CLASS = "velora-toast";
const VALID_VARIANTS = new Set(["success", "error", "warning", "info"]);

const DEFAULT_OPTIONS = {
    duration: 5000,
    dismissible: true,
    persistent: false,
};

let container = null;

function ensureContainer() {
    if (container && document.body.contains(container)) {
        return container;
    }
    container = document.createElement("div");
    container.className = CONTAINER_CLASS;
    container.setAttribute("role", "region");
    container.setAttribute("aria-label", "Notifiche");
    container.setAttribute("aria-live", "polite");
    document.body.appendChild(container);
    return container;
}

function dismissToast(toast) {
    if (!toast || !toast.parentNode) {
        return;
    }
    toast.classList.add("velora-toast--leaving");
    toast.addEventListener(
        "transitionend",
        () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        },
        { once: true },
    );
    // Fallback: se il browser non triggerera` transitionend (es. prefers-
    // reduced-motion + transition: none) rimuoviamo dopo un timeout breve.
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 400);
}

function show(variant, message, opts) {
    if (!VALID_VARIANTS.has(variant)) {
        variant = "info";
    }
    const options = Object.assign({}, DEFAULT_OPTIONS, opts || {});
    const root = ensureContainer();

    const toast = document.createElement("div");
    toast.className = `${TOAST_CLASS} ${TOAST_CLASS}--${variant}`;
    toast.setAttribute("role", variant === "error" ? "alert" : "status");

    const body = document.createElement("div");
    body.className = `${TOAST_CLASS}__body`;
    body.textContent = message == null ? "" : String(message);
    toast.appendChild(body);

    if (options.dismissible) {
        const close = document.createElement("button");
        close.type = "button";
        close.className = `${TOAST_CLASS}__close`;
        close.setAttribute("aria-label", "Chiudi notifica");
        close.textContent = "\u00D7"; // ×
        close.addEventListener("click", () => dismissToast(toast));
        toast.appendChild(close);
    }

    root.appendChild(toast);

    if (!options.persistent && options.duration > 0) {
        setTimeout(() => dismissToast(toast), options.duration);
    }

    return toast;
}

const toast = {
    show,
    success(message, opts) {
        return show("success", message, opts);
    },
    error(message, opts) {
        return show("error", message, opts);
    },
    warning(message, opts) {
        return show("warning", message, opts);
    },
    info(message, opts) {
        return show("info", message, opts);
    },
    dismissAll() {
        if (!container) return;
        Array.from(container.querySelectorAll("." + TOAST_CLASS)).forEach(
            dismissToast,
        );
    },
};

/**
 * Drena i payload emessi da {% velora_toast_messages %}: <script
 * type="application/json" data-velora-toast>...</script>. Eseguito al
 * DOMContentLoaded e una sola volta (rimuoviamo il <script> dopo aver
 * letto il payload, cosi` il MutationObserver non re-esegue).
 */
function drainServerPayloads() {
    const scripts = document.querySelectorAll(
        "script[data-velora-toast]",
    );
    scripts.forEach((node) => {
        try {
            const payload = JSON.parse(node.textContent || "{}");
            const opts = {};
            if (payload.tags && payload.tags.indexOf("persistent") !== -1) {
                opts.persistent = true;
            }
            show(payload.variant || "info", payload.message || "", opts);
        } catch (err) {
            console.warn("[velora][toast] payload non valido", err, node);
        } finally {
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        }
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", drainServerPayloads);
} else {
    drainServerPayloads();
}

export default toast;
