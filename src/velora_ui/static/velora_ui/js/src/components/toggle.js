/**
 * Componente Velora "toggle-link" (10.7).
 *
 * Si attacca a `<a data-velora-component="toggle-link">` con attributi:
 *   - data-toggle-target: selettore CSS (es. "#dettagli")
 *   - data-toggle-label-show: label quando il target e` nascosto
 *   - data-toggle-label-hide: label quando il target e` visibile
 *   - data-toggle-state: "hidden" | "shown" (stato iniziale)
 *
 * Sul target applica/rimuove la classe `is-toggled-hidden` che il CSS
 * mappa a `display: none`. Il link non navigates: il click e` neutralizzato
 * con `preventDefault`.
 */

const HIDDEN_CLASS = "is-toggled-hidden";

function applyState(target, isHidden) {
    if (!target) return;
    target.classList.toggle(HIDDEN_CLASS, isHidden);
    target.setAttribute("aria-hidden", isHidden ? "true" : "false");
}

const toggleLink = {
    name: "toggle-link",
    init(el) {
        const targetSel = el.getAttribute("data-toggle-target") || "";
        const labelShow = el.getAttribute("data-toggle-label-show") || "Mostra";
        const labelHide = el.getAttribute("data-toggle-label-hide") || "Nascondi";
        let state = el.getAttribute("data-toggle-state") || "hidden";
        if (!targetSel) return;
        const target = document.querySelector(targetSel);
        if (!target) return;
        // Sincronizza stato iniziale: se il dev passa "shown" ma il target
        // ha la classe hidden (o viceversa), preferiamo lo stato del DOM.
        if (target.classList.contains(HIDDEN_CLASS)) state = "hidden";
        // Applica visibilita` iniziale coerente con lo stato dichiarato
        applyState(target, state === "hidden");
        el.textContent = state === "hidden" ? labelShow : labelHide;
        el.setAttribute("aria-expanded", state === "hidden" ? "false" : "true");

        el.addEventListener("click", (event) => {
            event.preventDefault();
            const nowHidden = !target.classList.contains(HIDDEN_CLASS);
            applyState(target, nowHidden);
            el.textContent = nowHidden ? labelShow : labelHide;
            el.setAttribute("aria-expanded", nowHidden ? "false" : "true");
            el.classList.toggle("is-active", !nowHidden);
        });
    },
};

export default toggleLink;
