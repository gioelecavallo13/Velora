/**
 * Componente Velora "timer" (timer_fields).
 *
 * Sincronizza i sub-input numerici (uno per unita`) con un campo hidden che
 * contiene il totale in secondi. L'attributo `data-seconds` di ogni sub-input
 * dichiara quanti secondi vale 1 unita` di quel campo.
 */

const timer = {
    name: "timer",
    init(wrapper) {
        const hidden = wrapper.querySelector(".velora-timer__hidden");
        const fields = Array.from(wrapper.querySelectorAll(".velora-timer__field"));
        if (!hidden || !fields.length) return;

        const recompute = () => {
            let total = 0;
            fields.forEach((f) => {
                const v = parseInt(f.value || "0", 10);
                const secsPer = parseInt(f.getAttribute("data-seconds") || "1", 10);
                if (!isNaN(v) && v >= 0) total += v * secsPer;
            });
            hidden.value = String(total);
            hidden.dispatchEvent(new Event("change", { bubbles: true }));
        };

        fields.forEach((f) => {
            f.addEventListener("input", recompute);
            f.addEventListener("change", recompute);
            f.addEventListener("blur", () => {
                if (f.value === "" || isNaN(parseInt(f.value, 10))) f.value = "0";
                recompute();
            });
        });
    },
};

export default timer;
