/**
 * Componente Velora "autocomplete" (locale + remoto).
 *
 * Locale: legge le opzioni da uno <script type="application/json"> dentro al
 * wrapper, filtra in memoria al keyup.
 *
 * Remoto (data-remote-url): debounce keyup, fetch GET con `?q=<term>`, attende
 * lista JSON [{value,label}] o `{results:[...]}`. Aggiorna un input hidden
 * con il `value` selezionato; l'input visibile mostra la `label`.
 */

const DEFAULT_DEBOUNCE = 300;
const DEFAULT_LIMIT = 10;

function debounce(fn, ms) {
    let t = null;
    return function (...args) {
        if (t) clearTimeout(t);
        t = setTimeout(() => fn.apply(this, args), ms);
    };
}

function buildResults(wrapper) {
    let panel = wrapper.querySelector(".velora-autocomplete__results");
    if (panel) return panel;
    panel = document.createElement("div");
    panel.className = "velora-autocomplete__results";
    panel.setAttribute("role", "listbox");
    wrapper.appendChild(panel);
    return panel;
}

function renderResults(panel, items, activeIndex) {
    panel.innerHTML = "";
    if (!items.length) {
        const empty = document.createElement("div");
        empty.className = "velora-autocomplete__empty";
        empty.textContent = "Nessun risultato";
        panel.appendChild(empty);
        return;
    }
    items.forEach((it, idx) => {
        const opt = document.createElement("button");
        opt.type = "button";
        opt.className = "velora-autocomplete__option";
        if (idx === activeIndex) opt.classList.add("is-active");
        opt.setAttribute("data-value", it.value);
        opt.setAttribute("data-label", it.label);
        opt.setAttribute("role", "option");
        opt.textContent = it.label;
        panel.appendChild(opt);
    });
}

const autocomplete = {
    name: "autocomplete",
    init(wrapper) {
        const input = wrapper.querySelector(".velora-autocomplete__input");
        const hidden = wrapper.querySelector(".velora-autocomplete__hidden");
        if (!input) return;

        const remoteUrl = wrapper.getAttribute("data-remote-url") || "";
        const queryParam = wrapper.getAttribute("data-query-param") || "q";
        const minChars = parseInt(wrapper.getAttribute("data-min-chars") || "1", 10);
        const debounceMs = parseInt(
            wrapper.getAttribute("data-debounce-ms") || String(DEFAULT_DEBOUNCE), 10
        );
        const limit = parseInt(wrapper.getAttribute("data-limit") || String(DEFAULT_LIMIT), 10);

        let localOptions = [];
        const dataNode = wrapper.querySelector(".velora-autocomplete__data");
        if (dataNode) {
            try { localOptions = JSON.parse(dataNode.textContent || "[]"); } catch (e) { localOptions = []; }
        }

        const panel = buildResults(wrapper);
        let active = -1;
        let currentItems = [];
        let currentAbort = null;

        const open = () => panel.classList.add("is-open");
        const close = () => { panel.classList.remove("is-open"); active = -1; };

        const fetchRemote = (term) => {
            if (currentAbort) currentAbort.abort();
            const ctrl = new AbortController();
            currentAbort = ctrl;
            const url = remoteUrl + (remoteUrl.includes("?") ? "&" : "?") +
                queryParam + "=" + encodeURIComponent(term);
            fetch(url, { signal: ctrl.signal, headers: { "X-Requested-With": "XMLHttpRequest" } })
                .then((r) => r.ok ? r.json() : Promise.reject(r.status))
                .then((data) => {
                    let arr = Array.isArray(data) ? data : (data && data.results) || [];
                    arr = arr.slice(0, limit).map((x) => ({
                        value: String(x.value !== undefined ? x.value : x.id || x.label || ""),
                        label: String(x.label !== undefined ? x.label : x.text || x.name || x.value || ""),
                    })).filter((x) => x.label);
                    currentItems = arr;
                    active = -1;
                    renderResults(panel, arr, active);
                    open();
                })
                .catch(() => {});
        };

        const fetchLocal = (term) => {
            const t = term.toLowerCase();
            currentItems = localOptions
                .filter((o) => String(o.label).toLowerCase().includes(t))
                .slice(0, limit);
            active = -1;
            renderResults(panel, currentItems, active);
            open();
        };

        const debounced = debounce(fetchRemote, debounceMs);

        input.addEventListener("input", () => {
            const term = input.value.trim();
            if (term.length < minChars) { close(); return; }
            if (remoteUrl) debounced(term); else fetchLocal(term);
            if (hidden) hidden.value = "";
        });

        input.addEventListener("focus", () => {
            if (input.value.trim().length >= minChars) {
                if (remoteUrl) debounced(input.value.trim());
                else fetchLocal(input.value.trim());
            }
        });

        input.addEventListener("keydown", (e) => {
            if (!panel.classList.contains("is-open")) return;
            if (e.key === "ArrowDown") {
                e.preventDefault();
                active = Math.min(active + 1, currentItems.length - 1);
                renderResults(panel, currentItems, active);
            } else if (e.key === "ArrowUp") {
                e.preventDefault();
                active = Math.max(active - 1, 0);
                renderResults(panel, currentItems, active);
            } else if (e.key === "Enter") {
                if (active >= 0 && currentItems[active]) {
                    e.preventDefault();
                    const sel = currentItems[active];
                    input.value = sel.label;
                    if (hidden) hidden.value = sel.value;
                    close();
                }
            } else if (e.key === "Escape") {
                close();
            }
        });

        panel.addEventListener("mousedown", (e) => {
            const opt = e.target.closest(".velora-autocomplete__option");
            if (!opt) return;
            e.preventDefault();
            input.value = opt.getAttribute("data-label");
            if (hidden) hidden.value = opt.getAttribute("data-value");
            close();
        });

        document.addEventListener("click", (e) => {
            if (!wrapper.contains(e.target)) close();
        });
    },
};

export default autocomplete;
