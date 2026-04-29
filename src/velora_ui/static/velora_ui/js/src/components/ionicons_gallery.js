/**
 * Galleria Ionicons nel showcase: carica ionicons-manifest.json e mostra una
 * griglia filtrabile per nome (ricerca client-side).
 */

const MAX_INITIAL = 96;
const MAX_FILTERED = 240;

const ioniconsGallery = {
    name: "ionicons-gallery",
    init(el) {
        const url =
            el.getAttribute("data-manifest-url") ||
            el.querySelector(".velora-ionicons-gallery__manifest")?.getAttribute(
                "data-url"
            );
        if (!url) return;

        const searchId = el.getAttribute("data-search-id");
        const search = searchId ? document.getElementById(searchId) : null;
        const grid = el.querySelector(".velora-ionicons-gallery__grid");
        const countEl = el.querySelector(".velora-ionicons-gallery__count");
        const baseStatic = el.getAttribute("data-icons-base") || "";

        if (!grid) return;

        let slugs = [];

        function render(filter) {
            const q = (filter || "").toLowerCase().trim();
            const list = q
                ? slugs.filter((s) => s.includes(q)).slice(0, MAX_FILTERED)
                : slugs.slice(0, MAX_INITIAL);
            grid.innerHTML = "";
            const frag = document.createDocumentFragment();
            list.forEach((slug) => {
                const item = document.createElement("div");
                item.className = "velora-ionicons-gallery__item";
                item.setAttribute("data-slug", slug);
                const img = document.createElement("img");
                img.src = `${baseStatic}${slug}.svg`;
                img.alt = "";
                img.loading = "lazy";
                img.width = 32;
                img.height = 32;
                const cap = document.createElement("span");
                cap.className = "velora-ionicons-gallery__caption";
                cap.textContent = slug;
                item.appendChild(img);
                item.appendChild(cap);
                frag.appendChild(item);
            });
            grid.appendChild(frag);
            if (countEl) {
                countEl.textContent =
                    q && slugs.filter((s) => s.includes(q)).length > list.length
                        ? list.length +
                          "+ (filtra di più — restringi la ricerca per vedere tutte)"
                        : `${list.length} visibili`;
            }
        }

        fetch(url)
            .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
            .then((data) => {
                slugs = Array.isArray(data) ? data : [];
                render("");
                if (search) {
                    let t = null;
                    search.addEventListener("input", () => {
                        if (t) clearTimeout(t);
                        t = setTimeout(() => render(search.value), 120);
                    });
                }
            })
            .catch((err) => {
                console.error("[velora] ionicons-gallery:", err);
                grid.textContent = "Impossibile caricare il manifest delle icone.";
            });
    },
};

export default ioniconsGallery;
