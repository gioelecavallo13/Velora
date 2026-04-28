/**
 * Componente Velora "confirm".
 *
 * Si attacca a qualunque elemento `<a data-velora-component="confirm">`
 * (tipicamente generato da {% velora_delete_link %}). Al click:
 *   1. mostra `window.confirm(message)` con il messaggio in
 *      `data-confirm-message` (fallback "Confermi?")
 *   2. se l'utente accetta, crea un form HTML al volo, lo POPola con
 *      il token CSRF (cercato fra `<input name=csrfmiddlewaretoken>` o
 *      cookie `csrftoken`), imposta method da `data-confirm-method`
 *      (default POST) e lo invia
 *   3. se l'utente rifiuta, blocca la navigazione (preventDefault)
 *
 * In assenza di JS il link funziona come `<a>` normale -- la view
 * server-side dovrebbe in quel caso mostrare una pagina di conferma
 * intermedia. Per le delete e` la prassi Django consigliata.
 */

const STORAGE_NAME = "csrftoken";

function readCsrfToken() {
    const input = document.querySelector("input[name='csrfmiddlewaretoken']");
    if (input && input.value) {
        return input.value;
    }
    const cookies = (document.cookie || "").split(";");
    for (let i = 0; i < cookies.length; i++) {
        const trimmed = cookies[i].trim();
        if (trimmed.indexOf(STORAGE_NAME + "=") === 0) {
            return decodeURIComponent(trimmed.substring(STORAGE_NAME.length + 1));
        }
    }
    return "";
}

function submitWithMethod(url, method) {
    const form = document.createElement("form");
    form.method = method;
    form.action = url;
    form.style.display = "none";

    const csrf = readCsrfToken();
    if (csrf) {
        const csrfField = document.createElement("input");
        csrfField.type = "hidden";
        csrfField.name = "csrfmiddlewaretoken";
        csrfField.value = csrf;
        form.appendChild(csrfField);
    }

    document.body.appendChild(form);
    form.submit();
}

const confirmComponent = {
    name: "confirm",
    init(el) {
        el.addEventListener("click", (event) => {
            if (el.classList.contains("is-disabled")) {
                event.preventDefault();
                return;
            }
            const message =
                el.getAttribute("data-confirm-message") || "Confermi?";
            const method =
                (el.getAttribute("data-confirm-method") || "post").toLowerCase();
            // window.confirm e` sincrono: blocca il thread finche` l'utente non
            // sceglie. E` sufficiente per v0.1: dialog Velora arriva in v0.2.
            const ok = window.confirm(message);
            if (!ok) {
                event.preventDefault();
                return;
            }
            if (method === "get") {
                // lasciamo proseguire la navigazione del link
                return;
            }
            event.preventDefault();
            const url = el.getAttribute("href");
            if (!url || url === "#") {
                console.warn("[velora][confirm] href mancante, niente da fare");
                return;
            }
            submitWithMethod(url, method);
        });
    },
};

export default confirmComponent;
