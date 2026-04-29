/**
 * Velora UI — entry **full** (include Chart.js / `chart-from-table`).
 */

import chartFromTable from "./components/chart_from_table.js";
import { registerCoreComponents } from "./velora_register_core_only.js";
import { startWithRegistrator, register, scan, VELORA_VERSION } from "./velora_runtime.js";

startWithRegistrator((reg) => {
    registerCoreComponents(reg);
    reg(chartFromTable);
});

const Velora = typeof window !== "undefined" ? window.Velora : undefined;

export default Velora;
export { register, scan, VELORA_VERSION };
