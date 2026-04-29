/**
 * Toggle tema chiaro/scuro: `data-velora-theme="dark"` su <html> + localStorage.
 */

const themeToggle = {
    name: "theme-toggle",
    init(el) {
        const storageKey = el.getAttribute("data-storage-key") || "velora-theme";
        const labelDark = el.getAttribute("data-label-dark") || "Tema scuro";
        const labelLight = el.getAttribute("data-label-light") || "Tema chiaro";

        const sync = () => {
            const dark =
                document.documentElement.getAttribute("data-velora-theme") ===
                "dark";
            el.setAttribute("aria-pressed", dark ? "true" : "false");
            el.textContent = dark ? labelLight : labelDark;
        };

        sync();
        el.addEventListener("click", () => {
            const dark =
                document.documentElement.getAttribute("data-velora-theme") ===
                "dark";
            const nextDark = !dark;
            if (nextDark) {
                document.documentElement.setAttribute(
                    "data-velora-theme",
                    "dark"
                );
            } else {
                document.documentElement.removeAttribute("data-velora-theme");
            }
            try {
                localStorage.setItem(storageKey, nextDark ? "dark" : "light");
            } catch (_e) {
                /* private mode / disabled */
            }
            sync();
        });
    },
};

export default themeToggle;
