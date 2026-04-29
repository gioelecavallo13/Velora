/**
 * Componente Velora "select-all-table".
 *
 * Coordina:
 *   - master checkbox in <thead>
 *   - per-row checkbox in <tbody>
 *   - contatore [data-count]
 *   - bottoni bulk-action [data-action]
 *
 * Bulk submit: POST/PATCH a `data-url` (override per action via data-url
 * sul bottone) con FormData `{action: <value>, ids: "1,2,3"}`.
 */

function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute("content") || "";
    const cookieMatch = document.cookie.match(/csrftoken=([^;]+)/);
    return cookieMatch ? cookieMatch[1] : "";
}

const selectAll = {
    name: "select-all-table",
    init(toolbar) {
        const targetSelector = toolbar.getAttribute("data-target");
        if (!targetSelector) return;
        const table = document.querySelector(targetSelector);
        if (!table) return;

        const master = table.querySelector(".velora-table__select-master");
        const rows = () => Array.from(table.querySelectorAll(".velora-table__select-row"));
        const counter = toolbar.querySelector("[data-count]");
        const actions = Array.from(toolbar.querySelectorAll("[data-action]"));
        const url = toolbar.getAttribute("data-url") || "";
        const idsName = toolbar.getAttribute("data-name") || "ids";

        const updateCount = () => {
            const selected = rows().filter((cb) => cb.checked);
            const n = selected.length;
            if (counter) counter.textContent = String(n);
            actions.forEach((a) => { a.disabled = n === 0; });
            if (master) {
                const total = rows().length;
                master.checked = n > 0 && n === total;
                master.indeterminate = n > 0 && n < total;
            }
        };

        if (master) {
            master.addEventListener("change", () => {
                rows().forEach((cb) => { cb.checked = master.checked; });
                updateCount();
            });
        }

        table.addEventListener("change", (e) => {
            if (e.target.classList.contains("velora-table__select-row")) {
                updateCount();
            }
        });

        actions.forEach((btn) => {
            btn.addEventListener("click", () => {
                const ids = rows().filter((cb) => cb.checked).map((cb) => cb.value);
                if (!ids.length) return;
                const confirmMsg = btn.getAttribute("data-confirm");
                if (confirmMsg && !window.confirm(confirmMsg)) return;
                const targetUrl = btn.getAttribute("data-url") || url;
                if (!targetUrl) {
                    console.warn("[velora] select-all-table: nessuna URL configurata");
                    return;
                }
                const method = (btn.getAttribute("data-method") || "post").toUpperCase();
                const fd = new FormData();
                fd.append("action", btn.getAttribute("data-action"));
                fd.append(idsName, ids.join(","));

                const token = getCSRFToken();
                const headers = { "X-Requested-With": "XMLHttpRequest" };
                if (token) headers["X-CSRFToken"] = token;

                btn.disabled = true;
                fetch(targetUrl, { method, body: fd, headers })
                    .then((r) => {
                        if (!r.ok) throw new Error("HTTP " + r.status);
                        if (window.Velora && window.Velora.toast) {
                            window.Velora.toast.success("Operazione completata");
                        }
                        // Soft reload: lasciamo al consumer la decisione di
                        // ricaricare la pagina o aggiornare via AJAX.
                        toolbar.dispatchEvent(new CustomEvent("velora-bulk-done", {
                            bubbles: true,
                            detail: { action: btn.getAttribute("data-action"), ids },
                        }));
                    })
                    .catch((err) => {
                        if (window.Velora && window.Velora.toast) {
                            window.Velora.toast.error("Errore durante l'operazione");
                        }
                        console.error("[velora] bulk action failed", err);
                    })
                    .finally(() => { updateCount(); });
            });
        });

        updateCount();
    },
};

export default selectAll;
