/**
 * Componente Velora "datepicker" (custom, zero deps).
 *
 * Si attacca a wrapper `data-velora-component="datepicker"`. Apre un calendario
 * popup quando l'utente clicca sull'input o sul trigger button. Supporta:
 *
 *   - data-format: pattern (default "YYYY-MM-DD"). Solo questo formato in v0.3.
 *   - data-time:   "true" => mostra anche selettore ore/minuti
 *   - data-time-format: pattern ora (default "HH:mm")
 *   - data-step-minutes: passi in minuti per il select (default 5)
 *   - data-min / data-max: vincoli (stesso formato di data-format)
 *   - data-first-day: 0 (Dom) o 1 (Lun, default)
 *
 * Il componente NON tenta di parsare formati arbitrari: usa il formato
 * canonico ISO `YYYY-MM-DD` (e ` HH:mm` per il datetime). Per formati locali
 * il consumer puo` post-processare lato server o registrare un componente
 * proprio.
 */

const DAY_NAMES_LONG_LUN = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"];
const DAY_NAMES_LONG_DOM = ["Dom", "Lun", "Mar", "Mer", "Gio", "Ven", "Sab"];
const MONTH_NAMES = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
];

function pad2(n) {
    return n < 10 ? "0" + n : "" + n;
}

function formatDate(d) {
    return d.getFullYear() + "-" + pad2(d.getMonth() + 1) + "-" + pad2(d.getDate());
}

function formatTime(d) {
    return pad2(d.getHours()) + ":" + pad2(d.getMinutes());
}

function parseDate(str) {
    if (!str) return null;
    const m = String(str).match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (!m) return null;
    const d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
    if (isNaN(d.getTime())) return null;
    return d;
}

function parseTime(str) {
    if (!str) return null;
    const m = String(str).match(/(\d{1,2}):(\d{2})/);
    if (!m) return null;
    return { h: Number(m[1]), m: Number(m[2]) };
}

function buildPanel(wrapper, input, options) {
    let panel = wrapper.querySelector(".velora-datepicker__panel");
    if (panel) return panel;
    panel = document.createElement("div");
    panel.className = "velora-datepicker__panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Selettore data");
    wrapper.appendChild(panel);
    return panel;
}

function renderCalendar(panel, state, options) {
    const cur = state.viewMonth;
    const year = cur.getFullYear();
    const month = cur.getMonth();
    const firstDay = options.firstDay;
    const days = firstDay === 0 ? DAY_NAMES_LONG_DOM : DAY_NAMES_LONG_LUN;

    const firstOfMonth = new Date(year, month, 1);
    const offset = (firstOfMonth.getDay() - firstDay + 7) % 7;
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    const cells = [];
    for (let i = 0; i < offset; i++) cells.push(null);
    for (let d = 1; d <= daysInMonth; d++) cells.push(new Date(year, month, d));
    while (cells.length % 7 !== 0) cells.push(null);

    const selected = state.selectedDate;
    const min = options.min ? parseDate(options.min) : null;
    const max = options.max ? parseDate(options.max) : null;

    const isInRange = (d) => {
        if (!d) return false;
        if (min && d < min) return false;
        if (max && d > max) return false;
        return true;
    };

    let html = '<div class="velora-datepicker__header">';
    html += '<button type="button" class="velora-datepicker__nav" data-nav="prev" aria-label="Mese precedente">‹</button>';
    html += '<span class="velora-datepicker__title">' + MONTH_NAMES[month] + " " + year + "</span>";
    html += '<button type="button" class="velora-datepicker__nav" data-nav="next" aria-label="Mese successivo">›</button>';
    html += '</div>';

    html += '<div class="velora-datepicker__weekdays">';
    days.forEach((d) => { html += '<span class="velora-datepicker__weekday">' + d + '</span>'; });
    html += '</div>';

    html += '<div class="velora-datepicker__grid">';
    cells.forEach((d) => {
        if (d === null) {
            html += '<span class="velora-datepicker__cell velora-datepicker__cell--empty"></span>';
            return;
        }
        const cls = ["velora-datepicker__cell"];
        if (selected && d.getTime() === selected.getTime()) cls.push("is-selected");
        const today = new Date(); today.setHours(0,0,0,0);
        if (d.getTime() === today.getTime()) cls.push("is-today");
        const inRange = isInRange(d);
        if (!inRange) cls.push("is-disabled");
        html += '<button type="button" class="' + cls.join(" ") + '" data-date="' + formatDate(d) + '"';
        if (!inRange) html += " disabled";
        html += '>' + d.getDate() + '</button>';
    });
    html += '</div>';

    if (options.withTime) {
        const t = state.selectedTime || { h: 9, m: 0 };
        const step = Math.max(1, options.stepMinutes);
        let hourOpts = "";
        for (let h = 0; h < 24; h++) {
            hourOpts += '<option value="' + h + '"' + (h === t.h ? " selected" : "") + ">" + pad2(h) + "</option>";
        }
        let minOpts = "";
        for (let m = 0; m < 60; m += step) {
            minOpts += '<option value="' + m + '"' + (m === t.m ? " selected" : "") + ">" + pad2(m) + "</option>";
        }
        html += '<div class="velora-datepicker__time">';
        html += '<select class="velora-datepicker__time-h" aria-label="Ore">' + hourOpts + '</select>';
        html += ' : ';
        html += '<select class="velora-datepicker__time-m" aria-label="Minuti">' + minOpts + '</select>';
        html += '</div>';
    }

    html += '<div class="velora-datepicker__footer">';
    html += '<button type="button" class="velora-datepicker__action" data-action="today">Oggi</button>';
    html += '<button type="button" class="velora-datepicker__action" data-action="clear">Pulisci</button>';
    html += '<button type="button" class="velora-datepicker__action velora-datepicker__action--primary" data-action="confirm">Conferma</button>';
    html += '</div>';

    panel.innerHTML = html;
}

function commit(input, state, options) {
    if (!state.selectedDate) {
        input.value = "";
        return;
    }
    const dateStr = formatDate(state.selectedDate);
    if (options.withTime) {
        const t = state.selectedTime || { h: 0, m: 0 };
        input.value = dateStr + " " + pad2(t.h) + ":" + pad2(t.m);
    } else {
        input.value = dateStr;
    }
    input.dispatchEvent(new Event("change", { bubbles: true }));
}

function openPanel(panel) { panel.classList.add("is-open"); }
function closePanel(panel) { panel.classList.remove("is-open"); }

const datepicker = {
    name: "datepicker",
    init(wrapper) {
        const input = wrapper.querySelector(".velora-datepicker__input");
        const trigger = wrapper.querySelector(".velora-datepicker__trigger");
        if (!input) return;

        const options = {
            withTime: wrapper.getAttribute("data-time") === "true",
            stepMinutes: parseInt(wrapper.getAttribute("data-step-minutes") || "5", 10),
            min: wrapper.getAttribute("data-min") || "",
            max: wrapper.getAttribute("data-max") || "",
            firstDay: parseInt(wrapper.getAttribute("data-first-day") || "1", 10),
        };

        const initialDate = parseDate(input.value) || new Date();
        const state = {
            viewMonth: new Date(initialDate.getFullYear(), initialDate.getMonth(), 1),
            selectedDate: parseDate(input.value),
            selectedTime: parseTime(input.value),
        };

        const panel = buildPanel(wrapper, input, options);

        const open = () => {
            renderCalendar(panel, state, options);
            openPanel(panel);
        };
        const close = () => closePanel(panel);

        input.addEventListener("focus", open);
        input.addEventListener("click", open);
        if (trigger) trigger.addEventListener("click", open);

        panel.addEventListener("click", (e) => {
            const navBtn = e.target.closest("[data-nav]");
            if (navBtn) {
                const dir = navBtn.getAttribute("data-nav") === "prev" ? -1 : 1;
                state.viewMonth = new Date(state.viewMonth.getFullYear(), state.viewMonth.getMonth() + dir, 1);
                renderCalendar(panel, state, options);
                return;
            }
            const cell = e.target.closest("[data-date]");
            if (cell && !cell.disabled) {
                state.selectedDate = parseDate(cell.getAttribute("data-date"));
                if (!options.withTime) {
                    commit(input, state, options);
                    close();
                } else {
                    renderCalendar(panel, state, options);
                }
                return;
            }
            const action = e.target.closest("[data-action]");
            if (action) {
                const which = action.getAttribute("data-action");
                if (which === "today") {
                    const today = new Date(); today.setHours(0,0,0,0);
                    state.selectedDate = today;
                    state.viewMonth = new Date(today.getFullYear(), today.getMonth(), 1);
                    renderCalendar(panel, state, options);
                } else if (which === "clear") {
                    state.selectedDate = null;
                    state.selectedTime = null;
                    commit(input, state, options);
                    close();
                } else if (which === "confirm") {
                    if (options.withTime) {
                        const hSel = panel.querySelector(".velora-datepicker__time-h");
                        const mSel = panel.querySelector(".velora-datepicker__time-m");
                        if (hSel && mSel) {
                            state.selectedTime = { h: Number(hSel.value), m: Number(mSel.value) };
                        }
                    }
                    commit(input, state, options);
                    close();
                }
            }
        });

        document.addEventListener("click", (e) => {
            if (!wrapper.contains(e.target)) close();
        });
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && panel.classList.contains("is-open")) {
                close();
                input.focus();
            }
        });
    },
};

export default datepicker;
