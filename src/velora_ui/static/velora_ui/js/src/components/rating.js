/**
 * Componente Velora "rating" (rating_stars).
 *
 * Lo stato e` gestito da radio button nativi (puro CSS via :checked). Il JS
 * aggiunge solo: hover preview live e aggiornamento aria-label dinamico.
 */

const rating = {
    name: "rating",
    init(wrapper) {
        if (wrapper.getAttribute("data-disabled") === "true") return;
        const stars = Array.from(wrapper.querySelectorAll(".velora-rating__star"));
        if (!stars.length) return;

        const applyHover = (val) => {
            stars.forEach((s) => {
                const v = Number(s.getAttribute("data-value"));
                s.classList.toggle("is-hover", val !== null && v <= val);
            });
        };

        stars.forEach((s) => {
            s.addEventListener("mouseenter", () => applyHover(Number(s.getAttribute("data-value"))));
            s.addEventListener("mouseleave", () => applyHover(null));
        });

        wrapper.addEventListener("change", () => {
            const sel = wrapper.querySelector('input[type="radio"]:checked');
            if (!sel) return;
            stars.forEach((s) => s.classList.toggle("is-selected",
                Number(s.getAttribute("data-value")) <= Number(sel.value)));
        });
    },
};

export default rating;
