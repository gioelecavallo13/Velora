# Velora UI

Framework grafico Django per pannelli admin: template tag riusabili, design system SCSS, JavaScript vanilla a moduli ES, infrastruttura Docker pronta all'uso (dev + prod) e showcase vivente come living styleguide.

> **Stato**: pre-alpha (v0.0.1 / v0.1.0-alpha.x). README placeholder, verra` riscritto come quickstart definitivo in M7 (baby step 9.1).
>
> Documentazione operativa attuale: [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) per l'infrastruttura, [VISION.md](VISION.md) per il posizionamento prodotto, e il piano operativo `velora-ui_django_framework_*.plan.md` nel proprio cartella piani.

## Avvio rapido (sviluppo)

Prerequisiti: Colima (o Docker Desktop) e git. Aggiungere `127.0.0.1   velora.local` al file hosts (vedi [docs/INFRASTRUCTURE.md](docs/INFRASTRUCTURE.md) sezione 2.3).

```bash
colima start --cpu 4 --memory 6
git clone git@github.com:gioelecavallo13/Velora.git
cd Velora
cp .env.example .env
docker compose -f docker-compose.dev.yml up
```

L'app risponde su <http://velora.local>.

## Licenza

[Apache License 2.0](LICENSE).
