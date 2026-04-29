# Velora UI — Vision e posizionamento

> Documento di posizionamento prodotto, output della Fase 1 del piano operativo.
> Cristallizza le decisioni strategiche prese prima dell'inizio dello sviluppo (Fase 2 / M0 Bootstrap).
> Riferimento: `~/.cursor/plans/velora-ui_django_framework_61f8855e.plan.md` sezione 0 e Fase 1.

## 1. Target utente (baby step 1.1)

**Decisione**: non strategicamente rilevante in questa fase.

L'identita` dell'utente finale del framework non viene fissata in v0.1. Velora viene costruito come strumento generico Django-centric, senza ottimizzazioni specifiche per un segmento (community OSS, team, clienti, progetti personali). Verra` rivalutato dopo v0.1 in base a chi effettivamente lo adottera`.

## 2. Tipologia di app servita (baby step 1.2)

**Decisione**: **admin panel / pannello di controllo interno**.

Velora e` ottimizzato per costruire interfacce di tipo gestionale-amministrativo: dashboard, liste con filtri, form di data-entry, tabelle di gestione record, viste di configurazione. Questa scelta guida tutte le decisioni di design successive:

- Densita` informativa alta (molti dati su poco spazio)
- Tipografia compatta (14px base)
- Palette sobria (grigio + arancio CTA), niente decorazioni gratuite
- Componenti utility-first: tabelle, form, link azione, alert
- Niente attenzione particolare a hero section, marketing pages, animazioni d'effetto
- Niente responsive mobile-first spinto: l'utente target lavora prevalentemente da desktop

Cosa Velora **non** vuole essere: un framework per portali pubblici, e-commerce vetrina, landing page, blog editoriali.

## 3. Criteri di successo v0.1 (baby step 1.3)

**Decisione**: **ogni commit deve portare valore tangibile e lasciare il progetto in stato funzionante**.

Traduzione operativa:

- Ogni commit nella cronologia chiude uno o piu` baby step del piano e ha un messaggio nel formato semver `vX.Y.Z - feature/patch/release ...`.
- Dopo ogni commit il progetto deve essere avviabile: `docker compose -f docker-compose.dev.yml up` parte senza errori e l'app risponde su http://velora.local. Niente commit "rotti" volontariamente.
- Non si fanno commit puramente cosmetici/documentali fuori dai punti previsti dal piano (CHANGELOG, README, AGENTS.md): la documentazione cresce insieme al codice, non a fine ciclo.
- Il vero validation gate per dichiarare v0.1.0 rilasciata resta quello dei criteri di accettazione del piano (sezione 13): tag testati, showcase completo, deploy dev e prod verificati.

Implicazione pratica: le release anche minori (`-alpha.N`) sono permesse e incoraggiate ad ogni milestone. La cronologia git deve raccontare un progetto che cresce in modo lineare e leggibile.

## 4. Distribuzione v0.1 (baby step 1.4)

**Decisione**: **solo Git privato**.

Velora v0.1.0 vive sul repository GitHub `https://github.com/gioelecavallo13/Velora.git` come repository privato. Niente pubblicazione su PyPI (ne` privato ne` pubblico) in v0.1.

Conseguenze:

- L'installazione in progetti terzi avviene via `pip install git+ssh://git@github.com/gioelecavallo13/Velora.git@v0.1.0` o equivalente.
- Niente burocrazia di registrazione namespace su PyPI.
- Nessuna pressione di backward compatibility verso un pubblico esterno: l'API puo` evolvere fra v0.1 e v0.2 senza vincoli, finche` resta documentata nel CHANGELOG.
- Decisione su PyPI rimandata a dopo v0.2, quando l'API sara` stata validata in almeno un progetto reale.

## 5. Licenza (baby step 1.5)

**Decisione**: **Apache License 2.0**.

Motivazioni:

- Permissiva (riuso, modifica, ridistribuzione, anche commerciale, sono liberi).
- Include una clausola esplicita di concessione di brevetto, che la rende piu` solida legalmente di MIT in caso di adozione futura da parte di organizzazioni con asset brevettuali.
- E` lo standard di fatto in molti progetti enterprise-friendly e Django-related.
- Compatibile con qualsiasi futura scelta su PyPI pubblico/privato.

Il file `LICENSE` con il testo completo della Apache 2.0 verra` creato in Fase 2 (baby step di M0 Bootstrap, parte di setup repo) o al piu` tardi in Fase 9 (M7 Release, parte di packaging).

## 6. Decisioni differite (consapevolmente)

Non sono trattate in v0.1 e verranno affrontate solo se/quando emergera` un'esigenza concreta:

- Multi-tenant: nessun supporto built-in, verra` lasciato al consumatore del framework
- i18n: solo italiano in v0.1, ma tutte le stringhe gia` in `gettext_lazy` per non bloccare il futuro
- Tema dark: niente in v0.1, predisposto via CSS custom properties nel design system di v0.4
- PyPI pubblico: rivalutare dopo v0.2
- Documentazione utente esterna (sito statico, MkDocs): rivalutare dopo v0.2

## 7. Stato della Fase 1

| Baby step | Decisione | Stato |
|---|---|---|
| 1.1 Target utente | Non rilevante per ora | Completato |
| 1.2 Tipologia app | Admin panel | Completato |
| 1.3 Criteri successo v0.1 | Ogni commit = valore tangibile + progetto funzionante | Completato |
| 1.4 Distribuzione v0.1 | Solo Git privato | Completato |
| 1.5 Licenza | Apache 2.0 | Completato |

Si puo` procedere con Fase 2 (M0 Bootstrap).

## 8. Markup SSoT e consumo Web statico (piano web-first)

**Criterio go/no-go (Fase 4, baby step 4.1 del piano *Velora web-first assets*):** introdurre in repo un registro markup + gate CI quando esiste consumo documentato senza Django (`docs/INTEGRATION_STATIC.md`, `docs/examples/`) e si vuole impedire il drift tra snippet e partial Django senza una fonte unica.

**Decisione:** go — attivata la cartella [`ui_registry/`](ui_registry/) con `registry.json`, frammenti neutri in `ui_registry/parts/` e lo script [`tools/sync_ui_registry.py`](tools/sync_ui_registry.py) (`--check` in CI). La scelta resta revocabile se il team non riceve adozione del consumo Web; in tal caso si può lasciare aperta una PR senza merge del gate o documentare qui un “no-go” datato.
