/**
 * Sidebar principale: per le voci con figli si apre sempre lo stesso pannello
 * flyout (overlay + colonna link), sia con sidebar espansa che collassata.
 * Richiede `data-velora-component="velora-sidebar"` sul wrapper (.velora-sidebar).
 *
 * Con sidebar espansa, l'apertura del flyout collassa temporaneamente la colonna
 * (come in modalità slim) senza scrivere localStorage; alla chiusura del flyout
 * la larghezza precedente viene ripristinata se era stata forzata da questo flusso.
 *
 * La classe `is-active` sulle voci principali e sui link del flyout è gestita
 * solo lato client in base ai click (non dalla URL / server).
 *
 * Chiudere il flyout: backdrop, Indietro, Escape, toggle stessa sezione, o
 * evento `velora:sidebar-collapsed` da `sidebar.js`.
 */

const COLLAPSED_CLASS = "velora-app--sidebar-collapsed";

function isCollapsed() {
    return document.body.classList.contains(COLLAPSED_CLASS);
}

/** Allineato a sidebar.js: aria sui pulsanti expand/collapse header+footer. */
function syncSidebarToggleAria(collapsed) {
    document.querySelectorAll('[data-velora-component="sidebar-toggle"]').forEach((btn) => {
        btn.setAttribute("aria-pressed", collapsed ? "true" : "false");
    });
}

function setMainActive(root, li) {
    root.querySelectorAll(".velora-sidebar__item.is-active").forEach((el) => {
        el.classList.remove("is-active");
    });
    if (li) li.classList.add("is-active");
}

function clearFlyoutLinksActive(root) {
    root.querySelectorAll(".velora-sidebar__flyout-link.is-active").forEach((a) => {
        a.classList.remove("is-active");
    });
}

function stripServerActiveClasses(root) {
    setMainActive(root, null);
    clearFlyoutLinksActive(root);
}

function syncBranchFlyoutState(root, panelId) {
    root.querySelectorAll("[data-velora-sidebar-branch]").forEach((li) => {
        const fid = li.getAttribute("data-velora-flyout-id");
        const open = Boolean(panelId && fid === panelId);
        li.classList.toggle("is-branch-flyout-open", open);
        const btn = li.querySelector("[data-velora-sidebar-branch-btn]");
        if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
}

function restoreFlyoutForcedLayout(root) {
    if (!root._veloraFlyoutRestoreExpanded) return;
    root._veloraFlyoutRestoreExpanded = false;
    document.body.classList.remove(COLLAPSED_CLASS);
    syncSidebarToggleAria(false);
}

/**
 * @param {object} [options]
 * @param {boolean} [options.skipLayoutRestore] - true quando si passa da un pannello
 *   flyout a un altro senza ripristinare la sidebar larga.
 */
function closeFlyout(root, options) {
    const skipLayoutRestore = Boolean(options && options.skipLayoutRestore);
    const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
    if (!layer) return;
    layer.hidden = true;
    layer.setAttribute("aria-hidden", "true");
    root.querySelectorAll("[data-velora-sidebar-flyout-panel]").forEach((p) => {
        p.hidden = true;
    });
    document.body.classList.remove("velora-app--sidebar-flyout-open");
    syncBranchFlyoutState(root, null);
    if (!skipLayoutRestore) {
        restoreFlyoutForcedLayout(root);
    }
}

function isFlyoutOpenForPanel(root, panelId) {
    const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
    if (!layer || layer.hidden || !panelId) return false;
    const panel = document.getElementById(panelId);
    return Boolean(panel && !panel.hidden);
}

function openFlyout(root, panelId) {
    const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
    if (!layer || !panelId) return;
    const panel = document.getElementById(panelId);
    if (!panel) return;

    closeFlyout(root, { skipLayoutRestore: true });
    clearFlyoutLinksActive(root);
    layer.hidden = false;
    layer.setAttribute("aria-hidden", "false");
    panel.hidden = false;
    document.body.classList.add("velora-app--sidebar-flyout-open");
    syncBranchFlyoutState(root, panelId);

    if (!isCollapsed()) {
        root._veloraFlyoutRestoreExpanded = true;
        document.body.classList.add(COLLAPSED_CLASS);
        syncSidebarToggleAria(true);
    }

    const branchLi = root.querySelector(`[data-velora-flyout-id="${CSS.escape(panelId)}"]`);
    setMainActive(root, branchLi);
    const back = panel.querySelector("[data-velora-sidebar-flyout-back]");
    if (back) back.focus();
}

document.addEventListener("velora:sidebar-collapsed", () => {
    document.querySelectorAll('[data-velora-component="velora-sidebar"]').forEach((root) => {
        closeFlyout(root);
    });
});

const veloraSidebar = {
    name: "velora-sidebar",
    init(root) {
        const list = root.querySelector("[data-velora-sidebar-list]");
        if (!list) return;

        stripServerActiveClasses(root);

        list.addEventListener("click", (ev) => {
            const link = ev.target.closest("a.velora-sidebar__row--link");
            if (link && list.contains(link)) {
                const li = link.closest(".velora-sidebar__item");
                setMainActive(root, li);
                clearFlyoutLinksActive(root);
                closeFlyout(root);
                return;
            }

            const btn = ev.target.closest("[data-velora-sidebar-branch-btn]");
            if (!btn || !root.contains(btn)) return;
            ev.preventDefault();
            const li = btn.closest("[data-velora-sidebar-branch]");
            if (!li) return;

            const fid = li.getAttribute("data-velora-flyout-id");
            if (!fid) return;

            if (isFlyoutOpenForPanel(root, fid)) {
                closeFlyout(root);
                return;
            }
            openFlyout(root, fid);
        });

        const layer = root.querySelector("[data-velora-sidebar-flyout-layer]");
        if (layer) {
            layer.addEventListener("click", (ev) => {
                const flyLink = ev.target.closest("a.velora-sidebar__flyout-link");
                if (flyLink && layer.contains(flyLink)) {
                    const panel = flyLink.closest("[data-velora-sidebar-flyout-panel]");
                    if (panel && panel.id) {
                        const branchLi = root.querySelector(
                            `[data-velora-flyout-id="${CSS.escape(panel.id)}"]`,
                        );
                        setMainActive(root, branchLi);
                        clearFlyoutLinksActive(root);
                        flyLink.classList.add("is-active");
                    }
                    closeFlyout(root);
                    return;
                }
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
            }
        });

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
