/**
 * Componente Velora "header-menu".
 *
 * Si registra sul registry di Velora (vedi js/src/velora.js) e si attacca
 * a qualunque elemento con `data-velora-component="header-menu"`. Gestisce
 * apertura/chiusura del pannello dropdown dell'header per i tipi item v0.2:
 * `single-menu`, `multi-menu`, `apps-menu`, `notifications`.
 *
 * Comportamento:
 *   - Desktop (viewport ≥721px, hover primario e puntatore fine): menu su
 *     hover/focus sul wrapper; chiusura all’uscita del puntatore salvo
 *     `:focus-within`; chevron nascosto via CSS.
 *   - Touch, puntatore grossolano o viewport stretta: toggle con click; chevron
 *     visibile dove applicabile.
 *   - Click fuori dal wrapper -> chiude il pannello
 *   - Tasto ESC con focus dentro il pannello/trigger -> chiude
 *   - Apertura mutuamente esclusiva: aprendo un menu, gli altri si chiudono
 *   - aria-expanded del trigger sincronizzato con lo stato
 *
 * Nota: questo componente NON dipende da `dropdown.js` (baby step 10.5).
 * Quando dropdown.js sara` introdotto in 10.5, valutare se factor-out
 * dell'API di basso livello (open/close + outside-click + ESC) per
 * condividerla; per ora le esigenze del header sono diverse abbastanza
 * (badge notifiche, mega-menu, app grid) da giustificare un componente
 * dedicato.
 */

const OPEN_CLASS = "is-open";
const TRIGGER_SELECTOR = ".velora-header__menu-trigger";
const PANEL_SELECTOR = ".velora-header__menu-panel";

/** Allineato a `_header.scss` (caret visibile) e ai breakpoint pannello mobile. */
let _hoverDropdownMql = null;
function hoverDropdownMql() {
    if (!_hoverDropdownMql) {
        _hoverDropdownMql = window.matchMedia("(min-width: 721px) and (hover: hover)");
    }
    return _hoverDropdownMql;
}

function prefersHoverDropdowns() {
    return hoverDropdownMql().matches && finePointerMql().matches;
}

let _finePointerMql = null;
function finePointerMql() {
    if (!_finePointerMql) {
        _finePointerMql = window.matchMedia("(pointer: fine)");
    }
    return _finePointerMql;
}

// Set globale dei pannelli attivi: serve per chiudere gli altri quando se ne
// apre uno nuovo. La mutua esclusione e` voluta nello scope dell'header
// (un solo pannello aperto alla volta).
const openWrappers = new Set();

function closeWrapper(wrapper) {
    if (!wrapper.classList.contains(OPEN_CLASS)) {
        return;
    }
    wrapper.classList.remove(OPEN_CLASS);
    const trigger = wrapper.querySelector(TRIGGER_SELECTOR);
    if (trigger) {
        trigger.setAttribute("aria-expanded", "false");
    }
    openWrappers.delete(wrapper);
}

function closeAll() {
    openWrappers.forEach((wrapper) => closeWrapper(wrapper));
}

function openWrapper(wrapper) {
    // Chiude eventuali altri pannelli aperti (mutua esclusione)
    openWrappers.forEach((other) => {
        if (other !== wrapper) {
            closeWrapper(other);
        }
    });
    wrapper.classList.add(OPEN_CLASS);
    const trigger = wrapper.querySelector(TRIGGER_SELECTOR);
    if (trigger) {
        trigger.setAttribute("aria-expanded", "true");
    }
    openWrappers.add(wrapper);
}

function toggleWrapper(wrapper) {
    if (wrapper.classList.contains(OPEN_CLASS)) {
        closeWrapper(wrapper);
    } else {
        openWrapper(wrapper);
    }
}

function isInsideOpenWrapper(target) {
    let node = target;
    while (node && node.nodeType === Node.ELEMENT_NODE) {
        if (openWrappers.has(node)) {
            return true;
        }
        node = node.parentElement;
    }
    return false;
}

// Listener globali registrati una sola volta. Vengono installati al primo
// init di un'istanza, cosi` i moduli ESM caricati ma non utilizzati non
// inquinano il documento.
let globalListenersInstalled = false;

function installGlobalListeners() {
    if (globalListenersInstalled) {
        return;
    }
    globalListenersInstalled = true;

    hoverDropdownMql().addEventListener("change", () => {
        closeAll();
    });

    finePointerMql().addEventListener("change", () => {
        closeAll();
    });

    document.addEventListener("click", (event) => {
        if (openWrappers.size === 0) {
            return;
        }
        if (!isInsideOpenWrapper(event.target)) {
            closeAll();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && openWrappers.size > 0) {
            // Restituiamo il focus al primo trigger ancora visibile prima di
            // chiudere, cosi` lo screen reader non perde il contesto.
            const firstWrapper = openWrappers.values().next().value;
            const trigger = firstWrapper && firstWrapper.querySelector(TRIGGER_SELECTOR);
            closeAll();
            if (trigger && typeof trigger.focus === "function") {
                trigger.focus();
            }
        }
    });
}

const headerMenu = {
    name: "header-menu",
    init(el) {
        const trigger = el.querySelector(TRIGGER_SELECTOR);
        const panel = el.querySelector(PANEL_SELECTOR);
        if (!trigger || !panel) {
            return;
        }

        installGlobalListeners();

        trigger.setAttribute("aria-expanded", "false");

        trigger.addEventListener("click", (event) => {
            if (prefersHoverDropdowns()) {
                return;
            }
            event.stopPropagation();
            toggleWrapper(el);
        });

        el.addEventListener("mouseenter", () => {
            if (prefersHoverDropdowns()) {
                openWrapper(el);
            }
        });

        el.addEventListener("mouseleave", () => {
            if (!prefersHoverDropdowns()) {
                return;
            }
            requestAnimationFrame(() => {
                if (!el.matches(":focus-within")) {
                    closeWrapper(el);
                }
            });
        });

        el.addEventListener("focusin", () => {
            if (prefersHoverDropdowns()) {
                openWrapper(el);
            }
        });

        el.addEventListener("focusout", () => {
            if (!prefersHoverDropdowns()) {
                return;
            }
            requestAnimationFrame(() => {
                if (!el.contains(document.activeElement)) {
                    closeWrapper(el);
                }
            });
        });

        // Click dentro il pannello su un link -> chiudi (UX standard dropdown
        // header). Sui pulsanti/eventi non-link il click si propaga e basta.
        panel.addEventListener("click", (event) => {
            const link = event.target && event.target.closest && event.target.closest("a[href]");
            if (link) {
                closeWrapper(el);
            }
        });
    },
};

export default headerMenu;
