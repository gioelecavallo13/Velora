/**
 * Componente Velora "table-cell" (form-in-cell, v0.3).
 *
 * Si attacca a `<span data-velora-component="table-cell">`. Ascolta
 * change/blur/Enter sull'input figlio, costruisce FormData e fa fetch()
 * verso `data-fic-url` con metodo `data-fic-method`.
 *
 * Per il CSRF Django: legge `__velora_csrf__` dal `<meta name="csrf-token">`
 * (convenzione: il consumer iniettare nel base template
 * `<meta name="csrf-token" content="{{ csrf_token }}">`).
 */

function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute("content") || "";
    const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieMatch ? cookieMatch[1] : "";
}

function setStatus(wrapper, type, msg) {
    const node = wrapper.querySelector(".velora-cell-form__status");
    if (!node) return;
    node.classList.remove("is-saving", "is-saved", "is-error");
    if (type) node.classList.add("is-" + type);
    node.textContent = msg || "";
    if (type === "saved") {
        setTimeout(() => {
            node.classList.remove("is-saved");
            node.textContent = "";
        }, 1500);
    }
}

function readValue(wrapper, type) {
    if (type === "select") return wrapper.querySelector("select").value;
    if (type === "checkbox") return wrapper.querySelector("input[type=checkbox]").checked ? "1" : "0";
    if (type === "onoff") {
        const btn = wrapper.querySelector(".velora-cell-form__onoff");
        return btn && btn.classList.contains("is-on") ? "1" : "0";
    }
    return wrapper.querySelector("input").value;
}

function submit(wrapper) {
    const url = wrapper.getAttribute("data-fic-url");
    const method = (wrapper.getAttribute("data-fic-method") || "patch").toUpperCase();
    const name = wrapper.getAttribute("data-fic-name");
    const type = wrapper.getAttribute("data-fic-type");
    const csrf = wrapper.getAttribute("data-fic-csrf") === "1";
    const rowId = wrapper.getAttribute("data-fic-row-id") || "";

    const value = readValue(wrapper, type);
    const fd = new FormData();
    fd.append(name, value);
    if (rowId) fd.append("id", rowId);

    const headers = { "X-Requested-With": "XMLHttpRequest" };
    if (csrf) {
        const token = getCSRFToken();
        if (token) headers["X-CSRFToken"] = token;
    }

    setStatus(wrapper, "saving", "Salvataggio...");
    fetch(url, { method, body: fd, headers })
        .then((r) => {
            if (!r.ok) throw new Error("HTTP " + r.status);
            setStatus(wrapper, "saved", "✓");
        })
        .catch((err) => {
            setStatus(wrapper, "error", "Errore");
            console.error("[velora] table-cell submit failed", err);
        });
}

const tableCell = {
    name: "table-cell",
    init(wrapper) {
        const type = wrapper.getAttribute("data-fic-type");
        const auto = wrapper.getAttribute("data-fic-auto-submit") === "1";

        if (type === "onoff") {
            const btn = wrapper.querySelector(".velora-cell-form__onoff");
            if (!btn) return;
            btn.addEventListener("click", () => {
                const isOn = btn.classList.toggle("is-on");
                btn.setAttribute("aria-checked", isOn ? "true" : "false");
                if (auto) submit(wrapper);
            });
            return;
        }

        const inputEl = wrapper.querySelector("input, select");
        if (!inputEl) return;

        if (type === "checkbox") {
            inputEl.addEventListener("change", () => { if (auto) submit(wrapper); });
            return;
        }

        if (type === "select") {
            inputEl.addEventListener("change", () => { if (auto) submit(wrapper); });
            return;
        }

        // text/number: submit su blur o Enter (debounce 400ms se auto)
        let lastValue = inputEl.value;
        let timer = null;
        const trigger = () => { if (inputEl.value !== lastValue) { lastValue = inputEl.value; submit(wrapper); } };
        inputEl.addEventListener("blur", trigger);
        inputEl.addEventListener("keydown", (e) => {
            if (e.key === "Enter") { e.preventDefault(); inputEl.blur(); }
        });
        if (auto) {
            inputEl.addEventListener("input", () => {
                if (timer) clearTimeout(timer);
                timer = setTimeout(trigger, 400);
            });
        }
    },
};

export default tableCell;
