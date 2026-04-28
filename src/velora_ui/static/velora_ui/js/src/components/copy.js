/**
 * Componente Velora "copy-link" (10.8).
 *
 * Si attacca a `<a data-velora-component="copy-link">` con attributi:
 *   - data-copy-value:        testo statico da copiare (priorita` su -target)
 *   - data-copy-target:       selettore CSS verso elemento da cui leggere
 *                             il testo (.value se input/textarea, altrimenti
 *                             .textContent)
 *   - data-copy-label:        label normale del link
 *   - data-copy-label-copied: label temporanea dopo la copia
 *
 * Comportamento: usa `navigator.clipboard.writeText(...)` (con fallback
 * `document.execCommand('copy')` per browser molto vecchi). Mostra un
 * toast Velora di successo se disponibile, altrimenti modifica solo
 * temporaneamente la label del link.
 */

const REVERT_MS = 1500;

function readValue(el) {
    const direct = el.getAttribute("data-copy-value") || "";
    if (direct) return direct;
    const sel = el.getAttribute("data-copy-target") || "";
    if (!sel) return "";
    const target = document.querySelector(sel);
    if (!target) return "";
    if ("value" in target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA")) {
        return target.value;
    }
    return target.textContent || "";
}

async function copyText(text) {
    if (!text) return false;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (_err) {
            // continua col fallback
        }
    }
    // Fallback per HTTP locali / browser legacy
    try {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "absolute";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        const ok = document.execCommand("copy");
        document.body.removeChild(ta);
        return !!ok;
    } catch (_err) {
        return false;
    }
}

function notify(success, copiedLabel) {
    if (window.Velora && window.Velora.toast) {
        if (success) {
            window.Velora.toast.success(copiedLabel || "Copiato");
        } else {
            window.Velora.toast.error("Copia fallita");
        }
    }
}

const copyLink = {
    name: "copy-link",
    init(el) {
        const labelDefault = el.getAttribute("data-copy-label") || el.textContent || "Copia";
        const labelCopied = el.getAttribute("data-copy-label-copied") || "Copiato";
        let revertTimer = null;
        el.addEventListener("click", async (event) => {
            event.preventDefault();
            const text = readValue(el);
            const ok = await copyText(text);
            if (ok) {
                el.textContent = labelCopied;
                el.classList.add("is-copied");
            }
            notify(ok, labelCopied);
            if (revertTimer !== null) window.clearTimeout(revertTimer);
            revertTimer = window.setTimeout(() => {
                el.textContent = labelDefault;
                el.classList.remove("is-copied");
                revertTimer = null;
            }, REVERT_MS);
        });
    },
};

export default copyLink;
