# ============================================================
# Gausso Backend - Yönetim Paneli (Admin Panel)
# ============================================================
# sqladmin kütüphanesi ile FastAPI'ye entegre yönetim arayüzü.
# /admin rotasında çalışır. User ve Question modellerini yönetir.
#
# KRİTİK NOT (sqladmin 0.18):
#   form_excluded_columns dışındaki alanlar data dict'e yazılsa bile
#   sqladmin tarafından görmezden gelinir. Bu yüzden hashed_password'u
#   on_model_change içinde doğrudan model nesnesi üzerine yazıyoruz.
# ============================================================

from passlib.context import CryptContext
from sqladmin import Admin, ModelView
from starlette.requests import Request
from wtforms import PasswordField
from wtforms.validators import Optional

from app.db.session import engine
from app.models.question import Question
from app.models.user import User

# Şifre hashleme bağlamı (services/user.py ile aynı algoritma)
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================
# Kullanıcı Yönetim Görünümü
# ============================================================
class UserAdmin(ModelView, model=User):
    """
    Kullanıcılar için admin arayüzü.
    hashed_password formdan gizlenir; yerine düz-metin 'Şifre' alanı eklenir.
    """

    # Panel başlığı ve menü simgesi
    name = "Kullanıcı"
    name_plural = "Kullanıcılar"
    icon = "fa-solid fa-users"

    # Listede görünecek sütunlar (hashed_password gizli tutulur)
    column_list = [
        User.id,
        User.username,
        User.email,
        User.score,
        User.level,
        User.is_active,
    ]

    # Arama yapılabilecek sütunlar
    column_searchable_list = [
        User.username,
        User.email,
    ]

    # Sıralama yapılabilecek sütunlar
    column_sortable_list = [
        User.id,
        User.username,
        User.score,
        User.level,
        User.is_active,
    ]

    # String kullan — ORM attribute referansı sqladmin 0.18'de form dışlama
    # için güvenilir değil.
    form_excluded_columns = ["hashed_password"]

    # Sütun etiketleri (Türkçe)
    column_labels = {
        User.id: "ID",
        User.username: "Kullanıcı Adı",
        User.email: "E-posta",
        User.score: "Puan",
        User.level: "Seviye",
        User.is_active: "Aktif mi?",
    }

    # ----------------------------------------------------------
    # Forma 'Şifre' alanını elle ekle
    # ----------------------------------------------------------
    async def scaffold_form(self) -> type:
        """
        sqladmin'in otomatik ürettiği WTForms sınıfına
        düz-metin 'password' alanını ekler.
        """
        form_class = await super().scaffold_form()
        form_class.password = PasswordField(
            "Şifre",
            validators=[Optional()],
            description=(
                "Yeni kullanıcı için zorunlu. "
                "Düzenlemede boş bırakırsanız mevcut şifre korunur."
            ),
        )
        return form_class

    # ----------------------------------------------------------
    # Kaydetmeden önce şifreyi doğrudan modele hash'le
    # ----------------------------------------------------------
    async def on_model_change(
        self, data: dict, model: User, is_created: bool, request: Request
    ) -> None:
        """
        Form verisi veritabanına yazılmadan hemen önce çalışır.

        ÖNEMLI: hashed_password form dışı olduğu için data dict'e
        yazmak yetmez — sqladmin bunu işlemez. Değeri doğrudan
        `model.hashed_password` üzerine yazıyoruz.

        - Yeni kayıt (is_created=True) : 'password' zorunlu.
        - Düzenleme  (is_created=False): 'password' boş = mevcut hash korunur.
        """
        plain_password: str = data.pop("password", None) or ""

        if plain_password:
            # bcrypt passlib ile hash'le (kütüphane 72-byte limitini kendisi yönetir)
            model.hashed_password = _pwd_context.hash(plain_password)
        elif is_created:
            # Yeni kayıtta şifre zorunlu
            raise ValueError("Yeni kullanıcı oluştururken 'Şifre' alanı boş bırakılamaz.")
        # else → düzenlemede şifre alanı boş: model.hashed_password mevcut değeriyle kalır


# ============================================================
# Soru Yönetim Görünümü
# ============================================================
class QuestionAdmin(ModelView, model=Question):
    """
    İstatistik soruları için admin arayüzü.
    Tüm alanlar listelenebilir ve düzenlenebilir.
    """

    # Panel başlığı ve menü simgesi
    name = "Soru"
    name_plural = "Sorular"
    icon = "fa-solid fa-circle-question"

    # Listede görünecek sütunlar
    column_list = [
        Question.id,
        Question.topic,
        Question.difficulty_level,
        Question.content,
        Question.correct_answer,
        Question.points_awarded,
    ]

    # Arama yapılabilecek sütunlar
    column_searchable_list = [
        Question.topic,
        Question.content,
        Question.correct_answer,
    ]

    # Sıralama yapılabilecek sütunlar
    column_sortable_list = [
        Question.id,
        Question.topic,
        Question.difficulty_level,
        Question.points_awarded,
    ]

    # Sütun etiketleri (Türkçe)
    column_labels = {
        Question.id: "ID",
        Question.topic: "Konu",
        Question.difficulty_level: "Zorluk (1-5)",
        Question.content: "Soru Metni",
        Question.correct_answer: "Doğru Cevap",
        Question.points_awarded: "Puan",
    }


# ============================================================
# Admin nesnesi oluşturucu (main.py'de kullanılır)
# ============================================================
def create_admin(app) -> Admin:
    """
    sqladmin Admin nesnesini oluşturur ve modelleri kaydeder.
    main.py içinde çağrılır.

    Güvenlik notu: Kimlik doğrulamasız (geliştirme ortamı).
    Üretimde authentication_backend ile korumak gerekir.
    """
    admin = Admin(
        app,
        engine,
        title="Gausso Yönetim Paneli",
        base_url="/admin",
    )

    admin.add_view(UserAdmin)
    admin.add_view(QuestionAdmin)

    return admin
