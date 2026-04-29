/**
 * Sidebar principale: accordion in modalità espansa, flyout in modalità collassata.
 * Richiede `data-velora-component="velora-sidebar"` sul wrapper (.velora-sidebar).
 *
 * I flyout fullscreen stanno sopra alla colonna sidebar (z-index); chiuderli deve
 * avvenire a ogni toggle espandi/comprimi (evento da `sidebar.js`).
 */

const COLLAPSED_CLASS = "velora-app--sidebar-collapsed";

function isCollapsed() {
    return document.body.classList.contains(COLLAPSED_CLASS);
}

function closeAllBranches(root) {
    root.querySelectorAll("[data-velora-sidebar-branch].is-open").forEach((li) => {
        li.classList.remove("is-open");
        const btn = li.querySelector("[data-velora-sidebar-branch-btn]");
        if (btn) btn.setAttribute("aria-expanded", "false");
    });
}

function closeFlyout(root) {
    const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
    if (!layer) return;
    layer.hidden = true;
    layer.setAttribute("aria-hidden", "true");
    root.querySelectorAll("[data-velora-sidebar-flyout-panel]").forEach((p) => {
        p.hidden = true;
    });
    document.body.classList.remove("velora-app--sidebar-flyout-open");
}

document.addEventListener("velora:sidebar-collapsed", (ev) => {
    const collapsed = Boolean(ev.detail && ev.detail.collapsed);
    document.querySelectorAll('[data-velora-component="velora-sidebar"]').forEach((root) => {
        closeFlyout(root);
        if (!collapsed) {
            closeAllBranches(root);
        }
    });
});

function openFlyout(root, panelId) {
    const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
    if (!layer || !panelId) return;
    const panel = document.getElementById(panelId);
    if (!panel) return;
    closeFlyout(root);
    layer.hidden = false;
    layer.setAttribute("aria-hidden", "false");
    panel.hidden = false;
    document.body.classList.add("velora-app--sidebar-flyout-open");
    const back = panel.querySelector("[data-velora-sidebar-flyout-back]");
    if (back) back.focus();
}

const veloraSidebar = {
    name: "velora-sidebar",
    init(root) {
        const list = root.querySelector("[data-velora-sidebar-list]");
        if (!list) return;

        list.addEventListener("click", (ev) => {
            const btn = ev.target.closest("[data-velora-sidebar-branch-btn]");
            if (!btn || !root.contains(btn)) return;
            ev.preventDefault();
            const li = btn.closest("[data-velora-sidebar-branch]");
            if (!li) return;

            if (isCollapsed()) {
                const fid = li.getAttribute("data-velora-flyout-id");
                openFlyout(root, fid);
                return;
            }

            const open = !li.classList.contains("is-open");
            closeAllBranches(root);
            if (open) {
                li.classList.add("is-open");
                btn.setAttribute("aria-expanded", "true");
            } else {
                btn.setAttribute("aria-expanded", "false");
            }
        });

        const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
        if (layer) {
            layer.addEventListener("click", (ev) => {
                if (ev.target.closest("[data-velora-sidebar-flyout-backdrop]")) {
                    closeFlyout(root);
                }
            });
            layer.querySelectorAll("[data-velora-sidebar-flyout-back]").forEach((b) => {
                b.addEventListener("click", () => closeFlyout(root));
            });
        }

        document.addEventListener("keydown", (ev) => {
            if (ev.key !== "Escape") return;
            if (root.querySelector("[data-velora-sidebar-flyout-layer]:not([hidden])")) {
                closeFlyout(root);
            } else {
                closeAllBranches(root);
            }
        });

        // Search (collassato): focus sull’input tramite pulsante ricerca compatto.
        const searchBtn = root.querySelector("[data-velora-sidebar-search-btn]");
        const searchInput = root.querySelector("[data-velora-sidebar-search-input]");
        if (searchBtn && searchInput) {
            searchBtn.addEventListener("click", () => {
                if (isCollapsed() && document.activeElement !== searchInput) {
                    searchInput.focus();
                }
            });
        }
    },
};

export default veloraSidebar;
