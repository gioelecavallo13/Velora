# ui_registry — Single Source of Truth (markup)

Directory **`ui_registry/`** è il registro **neutro** per i componenti coperti dalla pipeline di sync: frammenti HTML riusabili (`parts/`), intestazioni documentate (`literals/`) e la tabella di montaggio **`registry.json`**.

## Ruolo

- **`parts/*.html`**: solo HTML “neutro”. Segnaposto per i partial Django: `|||nome_variabile|||` (es. `|||variant|||` → `{{ variant }}` nel template generato).
- **`literals/*.txt`**: blocco `{% comment %}…{% endcomment %}` in testo puro, condiviso tra generazioni.
- **`registry.json`**: per ogni target definisce `output` (path del partial Django sotto `src/velora_ui/templates/`) e una lista di `segments`:
  - `{ "literal_file": "…" }`
  - `{ "part": "…" }` (HTML neutro + segnaposto)
  - `{ "django": "…" }` (righe/boccioli Django montati tra i pezzi neutri)

Opzionale: `static_example` genera un frammento per `docs/examples/_generated/` (sostituzioni letterali al posto dei segnaposto).

## Comandi

Dal root del repo:

```bash
python tools/sync_ui_registry.py --check   # nessun write; exit ≠ 0 se drift
python tools/sync_ui_registry.py --write    # aggiorna partial Django + frammenti statici registrati
```

Dopo aver modificato **solo** `ui_registry/`, eseguire `--write` e committare anche i file generati sotto `src/…/templates/` e `docs/examples/_generated/`.

## Aggiungere un componente

1. Aggiungere i file in `parts/` (e se serve `literals/`).
2. Aggiungere una voce in `registry.json` con `segments` nell’ordine corretto (comment → struttura → `{% if %}` ecc.).
3. Eseguire `python tools/sync_ui_registry.py --write`.
4. Verificare con `--check` e con la suite `pytest` (include `tests/test_ui_registry_sync.py`).
5. Aggiornare **manualmente** le pagine intere in `docs/examples/*.html` se serve nuovo copy-paste, oppure estendere `static_example`.

**Release asset Web:** invariata — una GitHub Release continua a essere l’unico delivery layer per CSS/JS; `ui_registry` incide solo su markup Django e documentazione nel repo.

Per integrazione statica degli asset vedi [docs/INTEGRATION_STATIC.md](../docs/INTEGRATION_STATIC.md).
