/**
 * Componenti Velora **senza** chart-from-table (nessun import di Chart.js).
 * Usato dall'entry core; il full entry aggiunge chart separatamente.
 */

import veloraSidebar from "./components/sidebar_nav.js";
import sidebarToggle from "./components/sidebar.js";
import confirmComponent from "./components/confirm.js";
import headerMenu from "./components/header_menu.js";
import tooltip from "./components/tooltip.js";
import dropdown from "./components/dropdown.js";
import dialog from "./components/dialog.js";
import toggleLink from "./components/toggle.js";
import copyLink from "./components/copy.js";
import datepicker from "./components/datepicker.js";
import multiselect from "./components/multiselect.js";
import autocomplete from "./components/autocomplete.js";
import imagePreview from "./components/image_preview.js";
import rating from "./components/rating.js";
import timerField from "./components/timer.js";
import redactor from "./components/redactor.js";
import tableCell from "./components/table_cell.js";
import selectAllTable from "./components/select_all_table.js";
import ioniconsGallery from "./components/ionicons_gallery.js";
import themeToggle from "./components/theme_toggle.js";

/**
 * @param {(c: { name: string, init: (el: HTMLElement) => void }) => void} register
 */
export function registerCoreComponents(register) {
    register(veloraSidebar);
    register(sidebarToggle);
    register(confirmComponent);
    register(headerMenu);
    register(tooltip);
    register(dropdown);
    register(dialog);
    register(toggleLink);
    register(copyLink);
    register(datepicker);
    register(multiselect);
    register(autocomplete);
    register(imagePreview);
    register(rating);
    register(timerField);
    register(redactor);
    register(tableCell);
    register(selectAllTable);
    register(ioniconsGallery);
    register(themeToggle);
}
