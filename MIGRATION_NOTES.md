# ============================================================
# Gausso Backend - Alembic Migration Yapılandirmasi
# ============================================================
# Bu dosya Alembic'in async SQLAlchemy ile calismasi icin
# gerekli ayarlari icerir. "alembic init alembic" komutu
# calistirildiktan sonra bu dosya ile degistirilmeli.
# ============================================================

# NOT: Bu dosya, ileriki adimda "alembic init alembic" komutu
# calistirildiktan sonra olusacak alembic/env.py dosyasinin
# uzerine yazilmalidir.
#
# Simdilik sadece calistirma talimatlarini icermektedir:
#
# 1. Migration altyapisini baslat:
#    alembic init alembic
#
# 2. alembic/alembic.ini dosyasinda sqlalchemy.url'i ayarla
#    ya da alembic/env.py'de config'den oku.
#
# 3. Ilk migration'i olustur:
#    alembic revision --autogenerate -m "initial_tables"
#
# 4. Migration'i uygula:
#    alembic upgrade head
