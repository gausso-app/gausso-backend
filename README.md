# Gausso Backend

Oyunlaştırılmış istatistik öğrenme platformunun FastAPI backend'i.

## 🚀 Hızlı Başlangıç

### 1. Sanal Ortam Oluştur & Aktifleştir
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 3. Ortam Değişkenlerini Ayarla
```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
# Ardından .env dosyasını düzenle
```

### 4. Uygulamayı Başlat
```bash
uvicorn app.main:app --reload
```

### 5. API'yi Keşfet
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **Sağlık Kontrolü**: http://127.0.0.1:8000/api/v1/health

## 📁 Proje Yapısı

```
gausso-backend/
├── app/
│   ├── main.py              # FastAPI uygulama giriş noktası
│   ├── core/
│   │   └── config.py        # Merkezi ayarlar (pydantic-settings)
│   ├── db/
│   │   ├── base.py          # Model kayıt dosyası (Alembic için)
│   │   └── session.py       # Async SQLAlchemy engine & session
│   ├── models/              # SQLAlchemy ORM modelleri
│   ├── schemas/             # Pydantic request/response şemaları
│   ├── routers/             # FastAPI router'ları (endpoint grupları)
│   │   └── health.py        # Sağlık kontrolü endpoint'i
│   └── services/            # İş mantığı katmanı
├── tests/
│   └── test_health.py       # Temel endpoint testleri
├── .env.example             # Ortam değişkenleri şablonu
├── .gitignore
├── pytest.ini
└── requirements.txt
```

## 🧪 Testleri Çalıştır

```bash
pytest -v
```

## 📚 Teknoloji Yığını

| Katman | Teknoloji |
|--------|-----------|
| Web Framework | FastAPI |
| Sunucu | Uvicorn |
| ORM | SQLAlchemy 2.0 (async) |
| Veri Doğrulama | Pydantic v2 |
| Kimlik Doğrulama | JWT (python-jose) |
| Test | pytest + httpx |