/**
 * Galleria Ionicons: ricerca AJAX (data-search-url) o manifest locale.
 * Ogni card mostra icona, classe stile ion-<slug> e snippet {% velora_icon %}.
 */

const DEBOUNCE_MS = 200;
const DEFAULT_LIMIT = 480;
const MAX_INITIAL_MANIFEST = 96;

function debounce(fn, ms) {
    let t = null;
    return (...args) => {
        if (t) clearTimeout(t);
        t = setTimeout(() => {
            t = null;
            fn(...args);
        }, ms);
    };
}

function ionClass(slug) {
    return `ion-${slug}`;
}

function tagSnippet(slug) {
    return `{% velora_icon '${slug}' %}`;
}

const ioniconsGallery = {
    name: "ionicons-gallery",
    init(el) {
        const manifestUrl =
            el.getAttribute("data-manifest-url") ||
            el.querySelector(".velora-ionicons-gallery__manifest")?.getAttribute(
                "data-url",
            );
        if (!manifestUrl && !el.getAttribute("data-search-url")) return;

        const searchUrl = el.getAttribute("data-search-url") || "";
        const searchId = el.getAttribute("data-search-id");
        const search = searchId ? document.getElementById(searchId) : null;
        const grid = el.querySelector(".velora-ionicons-gallery__grid");
        const countEl = el.querySelector(".velora-ionicons-gallery__count");
        const loaderEl = el.querySelector(".velora-ionicons-gallery__loader");
        const baseStatic = el.getAttribute("data-icons-base") || "";
        const copyHint =
            el.getAttribute("data-copy-hint") || "Copia slug negli appunti";

        if (!grid) return;

        let slugs = [];

        function showLoading(on) {
            el.classList.toggle("is-loading", on);
            if (loaderEl) {
                loaderEl.hidden = !on;
            }
            grid.setAttribute("aria-busy", on ? "true" : "false");
        }

        function copySlug(slug) {
            const run = (text) => {
                if (navigator.clipboard?.writeText) {
                    return navigator.clipboard.writeText(text);
                }
                return Promise.reject(new Error("no clipboard"));
            };
            run(slug).catch(() => {
                try {
                    const ta = document.createElement("textarea");
                    ta.value = slug;
                    ta.setAttribute("readonly", "");
                    ta.style.position = "absolute";
                    ta.style.left = "-9999px";
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand("copy");
                    document.body.removeChild(ta);
                } catch {
                    /* ignore */
                }
            });
        }

        function renderGrid(icons) {
            grid.innerHTML = "";
            const frag = document.createDocumentFragment();
            icons.forEach((slug) => {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "velora-ionicons-gallery__item";
                btn.setAttribute("role", "listitem");
                btn.setAttribute("data-slug", slug);
                btn.setAttribute("title", `${copyHint}: ${slug}`);

                const wrap = document.createElement("span");
                wrap.className = "velora-ionicons-gallery__icon-wrap";
                const img = document.createElement("img");
                img.src = `${baseStatic}${slug}.svg`;
                img.alt = "";
                img.loading = "lazy";
                img.width = 40;
                img.height = 40;
                wrap.appendChild(img);

                const meta = document.createElement("div");
                meta.className = "velora-ionicons-gallery__meta";
                const clsLine = document.createElement("code");
                clsLine.className = "velora-ionicons-gallery__class-name";
                clsLine.textContent = ionClass(slug);
                const useLine = document.createElement("code");
                useLine.className = "velora-ionicons-gallery__tag-snippet";
                useLine.textContent = tagSnippet(slug);

                meta.appendChild(clsLine);
                meta.appendChild(useLine);

                btn.appendChild(wrap);
                btn.appendChild(meta);
                btn.addEventListener("click", () => copySlug(slug));

                frag.appendChild(btn);
            });
            grid.appendChild(frag);
        }

        function formatCount(data) {
            if (!countEl) return;
            const total = data.total_icons ?? 0;
            const matched = data.matched ?? 0;
            const ret = data.returned ?? 0;
            const truncated = data.truncated;
            const initial = data.is_initial;

            if (!total) {
                countEl.textContent = "";
                return;
            }

            let msg = "";
            if (initial) {
                msg = `${ret} / ${total}`;
            } else {
                msg = `${ret} di ${matched} — catalogo ${total}`;
            }
            if (truncated) {
                msg += ` (massimo ${DEFAULT_LIMIT} in questa richiesta)`;
            }
            countEl.textContent = msg;
        }

        function ajaxLoad(qRaw) {
            const u = new URL(searchUrl, window.location.origin);
            u.searchParams.set("q", qRaw);
            u.searchParams.set("limit", String(DEFAULT_LIMIT));
            showLoading(true);
            fetch(u.toString(), {
                headers: { Accept: "application/json" },
            })
                .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
                .then((data) => {
                    renderGrid(data.icons || []);
                    formatCount(data);
                })
                .catch((err) => {
                    console.error("[velora] ionicons-gallery:", err);
                    grid.textContent =
                        "Impossibile caricare l'elenco icone. Verifica la rete o l'endpoint API.";
                })
                .finally(() => showLoading(false));
        }

        function manifestLoad() {
            fetch(manifestUrl)
                .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
                .then((data) => {
                    slugs = Array.isArray(data) ? data : [];
                    renderFromManifest("");
                })
                .catch((err) => {
                    console.error("[velora] ionicons-gallery:", err);
                    grid.textContent =
                        "Impossibile caricare il manifest delle icone.";
                });
        }

        function renderFromManifest(filter) {
            const q = (filter || "").toLowerCase().trim();
            const tutte = q === "tutte" || q === "all" || q === "*";
            const list = tutte
                ? slugs
                : q
                  ? slugs.filter((s) => s.includes(q))
                  : slugs.slice(0, MAX_INITIAL_MANIFEST);
            const cap = tutte || q ? 480 : MAX_INITIAL_MANIFEST;
            renderGrid(list.slice(0, cap));
            if (countEl) {
                countEl.textContent = tutte
                    ? `${list.length} di ${slugs.length}`
                    : q
                      ? `${Math.min(list.length, cap)} trovate su ${slugs.length}`
                      : `${Math.min(list.length, slugs.length)} su ${slugs.length}`;
            }
        }

        if (searchUrl) {
            ajaxLoad("");
            if (search) {
                search.addEventListener(
                    "input",
                    debounce(() => ajaxLoad(search.value.trim()), DEBOUNCE_MS),
                );
            }
        } else {
            manifestLoad();
            if (search) {
                search.addEventListener(
                    "input",
                    debounce(() => renderFromManifest(search.value), DEBOUNCE_MS),
                );
            }
        }
    },
};

export default ioniconsGallery;
