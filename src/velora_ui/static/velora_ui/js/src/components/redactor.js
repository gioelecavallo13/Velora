/**
 * Componente Velora "redactor" (rich text — toolbar minimale).
 *
 * Stub di base: aggiunge una toolbar contenteditable usando document.execCommand
 * (deprecata ma ancora supportata da tutti i browser principali, mantenuta
 * per compatibilita`). Non e` un editor full-featured: per esigenze avanzate
 * il consumer puo` registrare un proprio componente sostituendo questo (es.
 * Quill/TinyMCE/ProseMirror).
 *
 * Mantiene la <textarea> sottostante come sorgente di verita`: ad ogni input
 * dell'area editabile, il contenuto HTML viene scritto nella textarea.
 */

const TOOLBAR_DEFAULT = [
    { cmd: "bold", label: "B", title: "Grassetto" },
    { cmd: "italic", label: "I", title: "Corsivo" },
    { cmd: "underline", label: "U", title: "Sottolineato" },
    { cmd: "insertUnorderedList", label: "•", title: "Elenco puntato" },
    { cmd: "insertOrderedList", label: "1.", title: "Elenco numerato" },
    { cmd: "createLink", label: "🔗", title: "Link", needsValue: true },
    { cmd: "removeFormat", label: "✕", title: "Rimuovi formattazione" },
];

const redactor = {
    name: "redactor",
    init(wrapper) {
        const textarea = wrapper.querySelector(".velora-redactor__textarea");
        if (!textarea) return;
        if (textarea.disabled) return;

        const toolbar = document.createElement("div");
        toolbar.className = "velora-redactor__toolbar";
        TOOLBAR_DEFAULT.forEach((b) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "velora-redactor__btn";
            btn.title = b.title;
            btn.textContent = b.label;
            btn.addEventListener("mousedown", (e) => e.preventDefault());
            btn.addEventListener("click", () => {
                if (b.needsValue) {
                    const url = window.prompt("URL:", "https://");
                    if (!url) return;
                    document.execCommand(b.cmd, false, url);
                } else {
                    document.execCommand(b.cmd, false, null);
                }
                editable.dispatchEvent(new Event("input", { bubbles: true }));
            });
            toolbar.appendChild(btn);
        });

        const editable = document.createElement("div");
        editable.className = "velora-redactor__editable";
        editable.setAttribute("contenteditable", "true");
        editable.setAttribute("role", "textbox");
        editable.setAttribute("aria-multiline", "true");
        editable.innerHTML = textarea.value || "";

        editable.addEventListener("input", () => {
            textarea.value = editable.innerHTML;
            textarea.dispatchEvent(new Event("change", { bubbles: true }));
        });

        textarea.classList.add("velora-redactor__textarea--hidden");
        wrapper.insertBefore(toolbar, textarea);
        wrapper.insertBefore(editable, textarea);
    },
};

export default redactor;
