/**
 * Componente Velora "chart-from-table".
 *
 * Legge una tabella nel DOM (selettore in data-table-selector), costruisce
 * dataset per Chart.js e disegna nel canvas figlio.
 *
 * Tipi supportati: line, bar, pie (data-chart-type).
 *
 * line / bar: thead prima riga -> th[0] ignorato/label; th[1..] = categorie X.
 *   tbody -> td[0] = nome serie; td[1..] = numeri.
 * pie: tbody righe a 2 colonne (etichetta, valore). thead ignorato.
 */

import Chart from "chart.js/auto";

const DATASET_COLORS = [
    "rgb(245, 160, 0)", // brand orange
    "rgb(47, 111, 237)",
    "rgb(108, 181, 86)",
    "rgb(193, 40, 46)",
    "rgb(54, 163, 214)",
    "rgb(79, 93, 114)",
];

function parseNumber(text) {
    const t = String(text ?? "")
        .trim()
        .replace(/\s/g, "")
        .replace(/,/g, ".");
    const n = parseFloat(t);
    return Number.isFinite(n) ? n : NaN;
}

function collectRows(table) {
    const tbody = table.querySelector("tbody");
    if (!tbody) {
        return Array.from(table.querySelectorAll("tr")).filter(
            (tr) => !tr.closest("thead")
        );
    }
    return Array.from(tbody.querySelectorAll("tr"));
}

function parseLineBar(table, chartType) {
    const thead = table.querySelector("thead");
    let xLabels = [];
    if (thead) {
        const hr = thead.querySelector("tr");
        if (hr) {
            const ths = hr.querySelectorAll("th");
            xLabels = Array.from(ths)
                .slice(1)
                .map((th) => th.textContent.trim() || "");
        }
    }
    const rows = collectRows(table);
    if (!rows.length) return null;

    const datasets = [];
    let maxCols = 0;
    rows.forEach((tr) => {
        const cells = tr.querySelectorAll("td");
        maxCols = Math.max(maxCols, cells.length);
    });
    if (!xLabels.length && maxCols > 1) {
        for (let i = 1; i < maxCols; i++) {
            xLabels.push(String(i));
        }
    }
    rows.forEach((tr, rowIdx) => {
        const cells = tr.querySelectorAll("td");
        if (cells.length < 2) return;
        const label = cells[0].textContent.trim() || `Serie ${rowIdx + 1}`;
        const data = [];
        for (let i = 1; i < cells.length; i++) {
            const v = parseNumber(cells[i].textContent);
            data.push(Number.isFinite(v) ? v : 0);
        }
        while (data.length < xLabels.length) data.push(0);
        if (data.length > xLabels.length) {
            xLabels = xLabels.concat(
                Array.from({ length: data.length - xLabels.length }, (_, j) =>
                    String(j + xLabels.length + 1)
                )
            );
        }
        datasets.push({
            label,
            data,
            backgroundColor:
                chartType === "bar"
                    ? DATASET_COLORS[rowIdx % DATASET_COLORS.length]
                    : undefined,
            borderColor: DATASET_COLORS[rowIdx % DATASET_COLORS.length],
            tension: 0.2,
            fill: false,
        });
    });
    if (!datasets.length) return null;
    return {
        type: chartType,
        data: { labels: xLabels, datasets: datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } },
        },
    };
}

function parsePie(table) {
    const rows = collectRows(table);
    const labels = [];
    const data = [];
    rows.forEach((tr) => {
        const cells = tr.querySelectorAll("td");
        if (cells.length < 2) return;
        labels.push(cells[0].textContent.trim());
        const v = parseNumber(cells[1].textContent);
        data.push(Number.isFinite(v) ? v : 0);
    });
    if (!labels.length) return null;
    const bg = labels.map((_, i) => DATASET_COLORS[i % DATASET_COLORS.length]);
    return {
        type: "pie",
        data: {
            labels,
            datasets: [{ data, backgroundColor: bg }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: "bottom" } },
        },
    };
}

const chartFromTable = {
    name: "chart-from-table",
    init(el) {
        const sel = el.getAttribute("data-table-selector");
        const type = (el.getAttribute("data-chart-type") || "line").toLowerCase();
        const canvas = el.querySelector("canvas");
        if (!sel || !canvas) return;

        const table = document.querySelector(sel);
        if (!table) {
            console.warn("[velora] chart-from-table: tabella non trovata:", sel);
            return;
        }

        const prev = el.__veloraChart;
        if (prev && typeof prev.destroy === "function") {
            prev.destroy();
        }
        el.__veloraChart = null;

        let config = null;
        if (type === "pie") {
            config = parsePie(table);
        } else if (type === "line" || type === "bar") {
            config = parseLineBar(table, type);
        } else {
            config = parseLineBar(table, "line");
        }

        if (!config) {
            console.warn("[velora] chart-from-table: dati insufficienti da tabella:", sel);
            return;
        }

        el.__veloraChart = new Chart(canvas, config);
    },
};

export default chartFromTable;
