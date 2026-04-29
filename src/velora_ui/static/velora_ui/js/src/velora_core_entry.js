/**
 * Velora UI — entry **core** (senza Chart.js; niente `chart-from-table`).
 */

import { registerCoreComponents } from "./velora_register_core_only.js";
import { startWithRegistrator, register, scan, VELORA_VERSION } from "./velora_runtime.js";

startWithRegistrator(registerCoreComponents);

const Velora = typeof window !== "undefined" ? window.Velora : undefined;

export default Velora;
export { register, scan, VELORA_VERSION };
