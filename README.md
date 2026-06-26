# Return Material Manager

Aplikasi web untuk mengelola return material — input data return, pelacakan status, laporan bulanan, dan cetak berita acara (Excel).

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** Jinja2 + HTMX + TailwindCSS
- **Migration:** Alembic
- **Export:** openpyxl (Excel)

## Fitur

- **CRUD Return Material** — input lot ref, qty, reason, condition, destination, note
- **Status Tracking** — pending → approved → rejected
- **Attachment** — upload file pendukung per return
- **Berita Acara** — generate & export berita acara ke Excel (.xlsx)
- **Reports** — statistik return bulanan & per reason
- **Auth** — session-based login (default: `admin` / `admin123`)

## Flowchart

```mermaid
flowchart TD
    A[Login] -->|authenticated| B[Dashboard]
    A -->|failed| A

    B --> C[Return Material]
    B --> D[Berita Acara]
    B --> E[Reports]
    B --> F[Export Excel]

    %% Return Material flow
    C --> C1[List Returns]
    C --> C2[Create Return]
    C1 --> C3[Detail Return]
    C2 --> C3
    C3 --> C4[Update Status]
    C3 --> C5[Upload Attachment]
    C4 --> C1

    C4 --> C4a{Status?}
    C4a -->|Approved| C4b[✅ Approved]
    C4a -->|Rejected| C4c[❌ Rejected]
    C4a -->|Pending| C4d[⏳ Pending]

    %% Berita Acara flow
    D --> D1[List Berita Acara]
    D --> D2[Create Berita Acara]
    D2 --> D2a[Select Return Items]
    D2a --> D3[Detail Berita Acara]
    D1 --> D3
    D3 --> D4[Download Excel]
    D3 --> D5[Delete]
    D4 --> D1

    %% Reports
    E --> E1[Bulanan Stats]
    E --> E2[Per Reason Stats]

    %% Export
    F --> F1[Download Full Excel]

    style A fill:#f96,stroke:#333
    style B fill:#6cf,stroke:#333
    style C4b fill:#6f6,stroke:#333
    style C4c fill:#f66,stroke:#333
    style C4d fill:#ff6,stroke:#333
```

## Setup

```bash
# Clone
git clone https://github.com/andrizpray/Return-material.git
cd Return-material

# Virtual env
python3 -m venv venv
source venv/bin/activate

# Install deps
pip install -r requirements.txt

# DB migration
alembic upgrade head

# Run
uvicorn app.main:app --host 0.0.0.0 --port 8082
```

Buka `http://localhost:8082`

## Default Login

| Username | Password |
|----------|----------|
| admin    | admin123 |

> ⚠️ Ganti password sebelum deploy ke production.

## Struktur

```
app/
├── main.py              # App entry, middleware, seed admin
├── config.py            # Settings (DB path, upload dir, pagination)
├── database.py          # SQLAlchemy engine & session
├── models/
│   └── models.py        # User, ReturnMaterial, ReturnReason, ReturnAttachment, BeritaAcara, AuditLog
├── routes/
│   ├── auth.py          # Login / logout
│   ├── returns.py       # CRUD return material
│   ├── berita_acara.py  # Berita acara + Excel export
│   ├── reports.py       # Laporan bulanan
│   ├── dashboard.py     # Dashboard utama
│   └── export.py        # Export data
├── static/              # CSS, JS, images
└── templates/           # Jinja2 HTML templates
alembic/                 # Database migrations
data/                    # SQLite database (gitignored)
uploads/                 # File attachments (gitignored)
```

## License

MIT
