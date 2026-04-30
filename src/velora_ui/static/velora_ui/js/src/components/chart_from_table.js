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
 *
 * Estetica cartesiane ispirata ai grafici lineari di Highcharts (linee pulite,
 * griglia orizzontale, marker con alone) restando su Chart.js (licenza MIT).
 */

import Chart from "chart.js/auto";

/** Palette vicina ai default Highcharts (Core), adatta a serie multiple. */
const DATASET_COLORS = [
    "#f28f43",
    "#7cb5ec",
    "#90ed7d",
    "#f15c80",
    "#8085e9",
    "#e4d354",
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
            (tr) => !tr.closest("thead"),
        );
    }
    return Array.from(tbody.querySelectorAll("tr"));
}

function datasetStyleForRow(rowIdx, chartType) {
    const c = DATASET_COLORS[rowIdx % DATASET_COLORS.length];
    if (chartType === "bar") {
        return {
            backgroundColor: c,
            borderColor: c,
            borderWidth: 0,
            borderRadius: 3,
            borderSkipped: false,
        };
    }
    return {
        borderColor: c,
        backgroundColor: "transparent",
        borderWidth: 2.5,
        tension: 0,
        fill: false,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: "#ffffff",
        pointBorderColor: c,
        pointBorderWidth: 2,
        pointHitRadius: 10,
    };
}

function cartesianOptions() {
    const axisFont = {
        size: 11,
        family:
            'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    };
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: "index",
            intersect: false,
        },
        plugins: {
            legend: {
                position: "bottom",
                align: "center",
                labels: {
                    boxWidth: 14,
                    boxHeight: 10,
                    padding: 18,
                    usePointStyle: false,
                    color: "#333333",
                    font: axisFont,
                },
            },
            tooltip: {
                backgroundColor: "rgba(255, 255, 255, 0.97)",
                titleColor: "#333333",
                bodyColor: "#333333",
                borderColor: "#c9d2df",
                borderWidth: 1,
                padding: 10,
                cornerRadius: 2,
                titleFont: { ...axisFont, size: 12, weight: "600" },
                bodyFont: { ...axisFont, size: 12 },
                displayColors: true,
                boxPadding: 6,
            },
        },
        scales: {
            x: {
                offset: true,
                grid: {
                    display: false,
                },
                ticks: {
                    color: "#666666",
                    font: axisFont,
                },
                border: {
                    display: true,
                    color: "#c9d2df",
                },
            },
            y: {
                grace: "8%",
                grid: {
                    color: "rgba(193, 200, 208, 0.65)",
                    lineWidth: 1,
                    drawTicks: false,
                },
                ticks: {
                    color: "#666666",
                    font: axisFont,
                    padding: 8,
                },
                border: {
                    display: false,
                },
            },
        },
    };
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
                    String(j + xLabels.length + 1),
                ),
            );
        }
        datasets.push({
            label,
            data,
            ...datasetStyleForRow(rowIdx, chartType),
        });
    });
    if (!datasets.length) return null;
    return {
        type: chartType,
        data: { labels: xLabels, datasets: datasets },
        options: cartesianOptions(),
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
    const axisFont = {
        size: 11,
        family:
            'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    };
    return {
        type: "pie",
        data: {
            labels,
            datasets: [{ data, backgroundColor: bg, borderWidth: 1, borderColor: "#fff" }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    align: "center",
                    labels: {
                        boxWidth: 12,
                        boxHeight: 10,
                        padding: 16,
                        color: "#333333",
                        font: axisFont,
                    },
                },
                tooltip: {
                    backgroundColor: "rgba(255, 255, 255, 0.97)",
                    titleColor: "#333333",
                    bodyColor: "#333333",
                    borderColor: "#c9d2df",
                    borderWidth: 1,
                    padding: 10,
                    cornerRadius: 2,
                    bodyFont: { size: 12, ...axisFont },
                },
            },
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
