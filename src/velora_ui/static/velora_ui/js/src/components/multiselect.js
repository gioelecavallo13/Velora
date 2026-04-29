/**
 * Componente Velora "multiselect".
 *
 * Trasforma un <select multiple> nativo in una UI con chip + dropdown di
 * selezione. Senza JS l'utente continua a vedere il select nativo.
 *
 * Mantiene il <select> come sorgente di verita`: ogni operazione UI sincronizza
 * gli `<option selected>` per assicurare il submit corretto.
 */

function buildChip(label, value) {
    const chip = document.createElement("span");
    chip.className = "velora-multiselect__chip";
    chip.setAttribute("data-value", value);
    chip.innerHTML =
        '<span class="velora-multiselect__chip-label"></span>' +
        '<button type="button" class="velora-multiselect__chip-remove" aria-label="Rimuovi">×</button>';
    chip.querySelector(".velora-multiselect__chip-label").textContent = label;
    return chip;
}

const multiselect = {
    name: "multiselect",
    init(wrapper) {
        const select = wrapper.querySelector(".velora-multiselect__native");
        if (!select) return;

        const placeholder = wrapper.getAttribute("data-placeholder") || "Seleziona...";
        const disabled = select.disabled;

        // Costruisce il control "fake"
        const control = document.createElement("div");
        control.className = "velora-multiselect__control";
        control.setAttribute("tabindex", disabled ? "-1" : "0");
        control.setAttribute("role", "combobox");
        control.setAttribute("aria-haspopup", "listbox");
        control.setAttribute("aria-expanded", "false");
        if (disabled) control.classList.add("is-disabled");

        const chips = document.createElement("div");
        chips.className = "velora-multiselect__chips";
        const ph = document.createElement("span");
        ph.className = "velora-multiselect__placeholder";
        ph.textContent = placeholder;

        control.appendChild(chips);
        control.appendChild(ph);

        const dropdown = document.createElement("div");
        dropdown.className = "velora-multiselect__dropdown";
        dropdown.setAttribute("role", "listbox");

        // Popola le option dal select native
        Array.from(select.options).forEach((opt) => {
            if (opt.disabled) return;
            const item = document.createElement("button");
            item.type = "button";
            item.className = "velora-multiselect__option";
            item.setAttribute("data-value", opt.value);
            item.setAttribute("role", "option");
            item.textContent = opt.text;
            if (opt.selected) item.classList.add("is-selected");
            dropdown.appendChild(item);
        });

        // Hide native, ma lo lascia nel DOM per il submit
        select.classList.add("velora-multiselect__native--hidden");
        wrapper.appendChild(control);
        wrapper.appendChild(dropdown);

        const refreshChips = () => {
            chips.innerHTML = "";
            const selected = Array.from(select.selectedOptions);
            if (selected.length === 0) {
                ph.style.display = "";
                return;
            }
            ph.style.display = "none";
            selected.forEach((opt) => {
                chips.appendChild(buildChip(opt.text, opt.value));
            });
        };

        const setSelected = (value, on) => {
            Array.from(select.options).forEach((opt) => {
                if (opt.value === value) opt.selected = on;
            });
            const dropOpt = dropdown.querySelector('[data-value="' + CSS.escape(value) + '"]');
            if (dropOpt) dropOpt.classList.toggle("is-selected", on);
            select.dispatchEvent(new Event("change", { bubbles: true }));
            refreshChips();
        };

        const open = () => {
            if (disabled) return;
            wrapper.classList.add("is-open");
            control.setAttribute("aria-expanded", "true");
        };
        const close = () => {
            wrapper.classList.remove("is-open");
            control.setAttribute("aria-expanded", "false");
        };

        control.addEventListener("click", () => {
            wrapper.classList.contains("is-open") ? close() : open();
        });
        control.addEventListener("keydown", (e) => {
            if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
            if (e.key === "Escape") close();
        });

        dropdown.addEventListener("click", (e) => {
            const opt = e.target.closest(".velora-multiselect__option");
            if (!opt) return;
            const value = opt.getAttribute("data-value");
            const isOn = opt.classList.contains("is-selected");
            setSelected(value, !isOn);
        });

        chips.addEventListener("click", (e) => {
            const btn = e.target.closest(".velora-multiselect__chip-remove");
            if (!btn) return;
            e.stopPropagation();
            const chip = btn.closest(".velora-multiselect__chip");
            setSelected(chip.getAttribute("data-value"), false);
        });

        document.addEventListener("click", (e) => {
            if (!wrapper.contains(e.target)) close();
        });

        refreshChips();
    },
};

export default multiselect;
