/**
 * Componente Velora "image-preview".
 *
 * Mostra anteprima dell'immagine selezionata via <input type=file>. Supporta:
 *
 *   - data-max-size-kb: hint client-side; se > 0 e il file supera, mostra
 *     un toast error e annulla la selezione (lato server resta la verita`).
 *   - bottone "Rimuovi" (presente se `clearable=True` lato Python e c'e` un
 *     value iniziale): clear input + nasconde preview.
 *
 * Nota: per la rimozione "vera" lato backend serve una convenzione applicativa
 * (es. inviare anche un campo hidden `<name>__clear=1`). In v0.3 questo non
 * e` integrato per non imporre uno schema; il consumer puo` listanre il
 * custom event `velora-image-clear` sul wrapper.
 */

const imagePreview = {
    name: "image-preview",
    init(wrapper) {
        const input = wrapper.querySelector(".velora-image-preview__input");
        const thumb = wrapper.querySelector(".velora-image-preview__thumb");
        const clearBtn = wrapper.querySelector("[data-clear]");
        if (!input || !thumb) return;

        const maxKb = parseInt(wrapper.getAttribute("data-max-size-kb") || "0", 10);

        input.addEventListener("change", () => {
            const file = input.files && input.files[0];
            if (!file) return;
            if (maxKb > 0 && file.size > maxKb * 1024) {
                if (window.Velora && window.Velora.toast) {
                    window.Velora.toast.error(
                        "File troppo grande (max " + maxKb + " KB)"
                    );
                }
                input.value = "";
                return;
            }
            const reader = new FileReader();
            reader.onload = (e) => {
                thumb.classList.remove("is-empty");
                thumb.innerHTML =
                    '<img src="' + e.target.result + '" class="velora-image-preview__img" alt="Anteprima">';
            };
            reader.readAsDataURL(file);
        });

        if (clearBtn) {
            clearBtn.addEventListener("click", () => {
                input.value = "";
                thumb.classList.add("is-empty");
                thumb.innerHTML =
                    '<span class="velora-image-preview__placeholder" aria-hidden="true">🖼</span>';
                wrapper.dispatchEvent(new CustomEvent("velora-image-clear", { bubbles: true }));
                clearBtn.style.display = "none";
            });
        }
    },
};

export default imagePreview;
