import os
import smtplib
import sqlite3
import ssl
from contextlib import closing
from email.message import EmailMessage
from pathlib import Path

from flask import Flask, current_app, redirect, render_template, request, url_for


LANGUAGES = ("pl", "uk", "en")
SERVICE_IDS = (
    "renovation",
    "plumbing",
    "electrical",
    "cleaning",
    "moving",
    "furniture",
    "garden",
    "other",
)

COPY = {
    "pl": {
        "site_title": "Spplot — lokalni fachowcy w Poznaniu",
        "nav_label": "Główna nawigacja",
        "nav_menu": "Otwórz menu",
        "language_label": "Wybierz język",
        "back_top": "Wróć na górę",
        "form_contact_group": "KONTAKT",
        "meta_description": "Spplot łączy mieszkańców Poznania ze sprawdzonymi fachowcami od usług domowych i remontów.",
        "nav_home": "Start",
        "nav_services": "Usługi",
        "nav_how": "Jak działamy",
        "nav_request": "Opisz zlecenie",
        "hero_eyebrow": "POZNAŃ · DOBRZY FACHOWCY SĄ BLISKO",
        "hero_line_1": "Dobry fachowiec.",
        "hero_line_2": "Spokojna głowa.",
        "hero_text": "Remont, hydraulik, przeprowadzka? Opisz, czego potrzebujesz. Zaczynamy od lokalnych spraw, które naprawdę da się załatwić.",
        "hero_cta": "Opisz, czego potrzebujesz",
        "hero_secondary": "Zobacz usługi",
        "hero_note": "Poznań i okolice · Polski, ukraiński, English",
        "orbit_label": "MAŁE SPRAWY, DOBRZE OGARNIĘTE",
        "orbit_title": "Twoje zlecenie",
        "orbit_status": "Gotowe, by zacząć",
        "orbit_service": "Na przykład",
        "orbit_example": "Szukam hydraulika",
        "orbit_city": "Jeżyce, Poznań",
        "orbit_chip": "Lokalnie",
        "intro_kicker": "DOBRZE SIĘ SKŁADA",
        "intro_title": "Nie kolejna lista numerów.",
        "intro_text": "Spplot to prosty początek: mówisz, co jest do zrobienia, a my budujemy miejsce, w którym lokalne zlecenia spotykają się z dobrymi fachowcami.",
        "steps_title": "Trzy kroki. Bez labiryntu.",
        "step_one_title": "Wybierz usługę",
        "step_one_text": "Od drobnej naprawy po większy remont — zacznij od tego, czego potrzebujesz.",
        "step_two_title": "Opisz sprawę",
        "step_two_text": "Dodaj lokalizację i kilka szczegółów. Fachowiec będzie wiedział, o co chodzi.",
        "step_three_title": "Porozmawiajcie",
        "step_three_text": "Gdy dołączą lokalni wykonawcy, Twoje zapytanie pomoże Wam się znaleźć.",
        "services_kicker": "CO TRZEBA ZROBIĆ?",
        "services_title": "Znajdź właściwy początek.",
        "services_text": "Wybierz kategorię. Jeśli nie widzisz swojej sprawy, opisz ją w formularzu.",
        "all_services": "Wszystkie usługi",
        "browse_services": "Zobacz wszystkie usługi",
        "cta_title": "Co dziś trzeba ogarnąć?",
        "cta_text": "Zacznij od krótkiego opisu. Reszta nie musi być skomplikowana.",
        "footer_line": "Lokalne sprawy. Dobrzy ludzie.",
        "services_page_kicker": "KATALOG USŁUG",
        "services_page_title": "Od czego zaczynamy?",
        "services_page_text": "Wybierz temat i opisz zlecenie. Na razie skupiamy się na usługach domowych w Poznaniu i okolicy.",
        "service_action": "Opisz zlecenie",
        "request_kicker": "PIERWSZY KROK",
        "request_title": "Opowiedz nam o swojej sprawie.",
        "request_text": "Kilka konkretów pomoże lepiej zrozumieć, czego potrzebujesz.",
        "form_category": "Jakiej usługi potrzebujesz?",
        "form_choose": "Wybierz kategorię",
        "form_location": "Gdzie wykonać usługę?",
        "form_location_placeholder": "Dzielnica lub miejscowość",
        "form_details": "Co jest do zrobienia?",
        "form_details_placeholder": "Napisz kilka zdań: co, kiedy i na co zwrócić uwagę.",
        "form_name": "Jak masz na imię?",
        "form_contact": "Telefon lub e-mail do kontaktu",
        "form_contact_placeholder": "+48 000 000 000 lub adres e-mail",
        "form_consent": "Zgadzam się na zapisanie danych i kontakt w sprawie tego zgłoszenia.",
        "form_submit": "Wyślij zapytanie",
        "form_privacy": "Podajemy tylko dane potrzebne do obsługi zgłoszenia.",
        "form_demo_notice": "Zgłoszenie zapisujemy w systemie. Powiadomienie e-mail trafia do właściciela po skonfigurowaniu poczty; zgłoszenia nie są automatycznie wysyłane do wykonawców.",
        "form_success": "Dziękujemy — Twoje zgłoszenie zostało zapisane.",
        "form_email_sent": "Powiadomienie o zleceniu wysłaliśmy na e-mail właściciela.",
        "form_email_not_configured": "Zgłoszenie zapisaliśmy, ale powiadomienia e-mail nie są jeszcze skonfigurowane. Skontaktuj się bezpośrednio przez WhatsApp lub Telegram.",
        "form_email_failed": "Zgłoszenie zapisaliśmy, ale nie udało się wysłać powiadomienia e-mail. Skontaktuj się bezpośrednio przez WhatsApp lub Telegram.",
        "form_error": "Sprawdź formularz i uzupełnij wymagane pola.",
        "back_services": "Wróć do usług",
        "contact_whatsapp": "WhatsApp",
        "contact_telegram": "Telegram",
        "direct_contact": "Wolisz napisać bezpośrednio?",
        "language_name": {"pl": "PL", "uk": "UA", "en": "EN"},
        "services": [
            {"id": "renovation", "icon": "✳", "name": "Remont i wykończenie", "description": "Malowanie, płytki, gładzie i odświeżenie mieszkania."},
            {"id": "plumbing", "icon": "↗", "name": "Hydraulik", "description": "Naprawa kranu, instalacje i pilne awarie."},
            {"id": "electrical", "icon": "⌁", "name": "Elektryk", "description": "Oświetlenie, gniazdka i bezpieczna instalacja."},
            {"id": "cleaning", "icon": "◌", "name": "Sprzątanie", "description": "Porządki regularne, po remoncie lub przeprowadzce."},
            {"id": "moving", "icon": "▧", "name": "Przeprowadzki", "description": "Transport, pakowanie i pomoc przy przenosinach."},
            {"id": "furniture", "icon": "⌂", "name": "Meble i montaż", "description": "Składanie, wieszanie i drobne prace stolarskie."},
            {"id": "garden", "icon": "❋", "name": "Ogród", "description": "Pielęgnacja, przycinanie i przygotowanie ogrodu."},
            {"id": "other", "icon": "＋", "name": "Inna sprawa", "description": "Nie widzisz swojej usługi? Opisz, czego szukasz."},
        ],
    },
    "uk": {
        "site_title": "Spplot — місцеві майстри в Познані",
        "nav_label": "Головна навігація",
        "nav_menu": "Відкрити меню",
        "language_label": "Оберіть мову",
        "back_top": "На початок",
        "form_contact_group": "КОНТАКТ",
        "meta_description": "Spplot допомагає мешканцям Познані знайти фахівців для домашніх робіт і ремонту.",
        "nav_home": "Головна",
        "nav_services": "Послуги",
        "nav_how": "Як це працює",
        "nav_request": "Опишіть завдання",
        "hero_eyebrow": "ПОЗНАНЬ · ХОРОШІ МАЙСТРИ ПОРУЧ",
        "hero_line_1": "Добрий майстер.",
        "hero_line_2": "Спокійна голова.",
        "hero_text": "Ремонт, сантехнік, переїзд? Розкажіть, що потрібно. Починаємо з місцевих справ, які справді можна вирішити.",
        "hero_cta": "Опишіть, що потрібно",
        "hero_secondary": "Послуги",
        "hero_note": "Познань і околиці · Polski, українська, English",
        "orbit_label": "МАЛЕНЬКІ СПРАВИ, ДОБРЕ ВИРІШЕНІ",
        "orbit_title": "Ваше завдання",
        "orbit_status": "Можна починати",
        "orbit_service": "Наприклад",
        "orbit_example": "Шукаю сантехніка",
        "orbit_city": "Єжице, Познань",
        "orbit_chip": "Поруч",
        "intro_kicker": "УСЕ СКЛАДАЄТЬСЯ",
        "intro_title": "Не черговий список номерів.",
        "intro_text": "Spplot — простий початок: ви розповідаєте, що потрібно зробити, а ми створюємо місце, де місцеві завдання зустрічаються з хорошими майстрами.",
        "steps_title": "Три кроки. Без лабіринтів.",
        "step_one_title": "Оберіть послугу",
        "step_one_text": "Від невеликого ремонту до повного оновлення — почніть із того, що потрібно вам.",
        "step_two_title": "Опишіть завдання",
        "step_two_text": "Додайте місце й кілька деталей, щоб майстер зрозумів суть.",
        "step_three_title": "Домовтеся",
        "step_three_text": "Коли доєднаються місцеві виконавці, запит допоможе вам знайти одне одного.",
        "services_kicker": "ЩО ПОТРІБНО ЗРОБИТИ?",
        "services_title": "Знайдіть правильний початок.",
        "services_text": "Оберіть категорію та опишіть завдання. Якщо не знайшли потрібну послугу — розкажіть про неї у формі.",
        "all_services": "Усі послуги",
        "browse_services": "Переглянути послуги",
        "cta_title": "Що потрібно вирішити сьогодні?",
        "cta_text": "Почніть із короткого опису. Далі все буде простіше.",
        "footer_line": "Місцеві справи. Хороші люди.",
        "services_page_kicker": "КАТАЛОГ ПОСЛУГ",
        "services_page_title": "З чого почнемо?",
        "services_page_text": "Оберіть напрямок і опишіть завдання. Поки зосереджуємося на домашніх послугах у Познані та околицях.",
        "service_action": "Описати завдання",
        "request_kicker": "ПЕРШИЙ КРОК",
        "request_title": "Розкажіть, що сталося.",
        "request_text": "Кілька конкретних деталей допоможуть зрозуміти, що вам потрібно.",
        "form_category": "Яка послуга вам потрібна?",
        "form_choose": "Оберіть категорію",
        "form_location": "Де потрібна послуга?",
        "form_location_placeholder": "Район або населений пункт",
        "form_details": "Що потрібно зробити?",
        "form_details_placeholder": "Напишіть кілька речень: що саме, коли та на що звернути увагу.",
        "form_name": "Як вас звати?",
        "form_contact": "Телефон або email для зв’язку",
        "form_contact_placeholder": "+48 000 000 000 або email",
        "form_consent": "Погоджуюся на збереження даних і зв’язок щодо цього запиту.",
        "form_submit": "Надіслати запит",
        "form_privacy": "Запитуємо лише дані, необхідні для обробки завдання.",
        "form_demo_notice": "Ми зберігаємо запит у системі. Після налаштування пошти власник отримає сповіщення електронною поштою; запити не надсилаються виконавцям автоматично.",
        "form_success": "Дякуємо — ваш запит збережено.",
        "form_email_sent": "Повідомлення про завдання надіслано на пошту власника.",
        "form_email_not_configured": "Запит збережено, але сповіщення електронною поштою ще не налаштовані. Зв’яжіться напряму через WhatsApp або Telegram.",
        "form_email_failed": "Запит збережено, але не вдалося надіслати сповіщення електронною поштою. Зв’яжіться напряму через WhatsApp або Telegram.",
        "form_error": "Перевірте форму та заповніть обов’язкові поля.",
        "back_services": "Повернутися до послуг",
        "contact_whatsapp": "WhatsApp",
        "contact_telegram": "Telegram",
        "direct_contact": "Хочете написати напряму?",
        "language_name": {"pl": "PL", "uk": "UA", "en": "EN"},
        "services": [
            {"id": "renovation", "icon": "✳", "name": "Ремонт і оздоблення", "description": "Фарбування, плитка та оновлення оселі."},
            {"id": "plumbing", "icon": "↗", "name": "Сантехнік", "description": "Ремонт кранів, комунікації та термінові аварії."},
            {"id": "electrical", "icon": "⌁", "name": "Електрик", "description": "Освітлення, розетки та безпечна проводка."},
            {"id": "cleaning", "icon": "◌", "name": "Прибирання", "description": "Регулярне, після ремонту чи переїзду."},
            {"id": "moving", "icon": "▧", "name": "Переїзди", "description": "Перевезення, пакування та допомога з речами."},
            {"id": "furniture", "icon": "⌂", "name": "Меблі та монтаж", "description": "Збирання, монтаж і дрібні столярні роботи."},
            {"id": "garden", "icon": "❋", "name": "Сад", "description": "Догляд за ділянкою та підготовка саду."},
            {"id": "other", "icon": "＋", "name": "Інше завдання", "description": "Не знайшли своєї послуги? Опишіть, що шукаєте."},
        ],
    },
    "en": {
        "site_title": "Spplot — local professionals in Poznań",
        "nav_label": "Main navigation",
        "nav_menu": "Open menu",
        "language_label": "Choose language",
        "back_top": "Back to top",
        "form_contact_group": "CONTACT",
        "meta_description": "Spplot helps people in Poznań find local professionals for home services and renovation.",
        "nav_home": "Home",
        "nav_services": "Services",
        "nav_how": "How it works",
        "nav_request": "Describe a job",
        "hero_eyebrow": "POZNAŃ · GOOD PEOPLE, CLOSE BY",
        "hero_line_1": "A good pro.",
        "hero_line_2": "Peace of mind.",
        "hero_text": "Renovation, a plumber, a move? Tell us what you need. We start with local jobs that can actually get done.",
        "hero_cta": "Tell us what you need",
        "hero_secondary": "Explore services",
        "hero_note": "Poznań and nearby · Polski, українська, English",
        "orbit_label": "SMALL JOBS, WELL SORTED",
        "orbit_title": "Your project",
        "orbit_status": "Ready to get started",
        "orbit_service": "For example",
        "orbit_example": "Looking for a plumber",
        "orbit_city": "Jeżyce, Poznań",
        "orbit_chip": "Nearby",
        "intro_kicker": "THINGS FALL INTO PLACE",
        "intro_title": "Not another list of numbers.",
        "intro_text": "Spplot is a simpler start: tell us what needs doing, and we're building a place where local jobs meet good people.",
        "steps_title": "Three steps. No maze.",
        "step_one_title": "Pick a service",
        "step_one_text": "From a small repair to a full refresh, start with what you need.",
        "step_two_title": "Describe the job",
        "step_two_text": "Add a location and a few details so a professional knows what to expect.",
        "step_three_title": "Talk it through",
        "step_three_text": "As local providers join, your request will help you find one another.",
        "services_kicker": "WHAT NEEDS DOING?",
        "services_title": "Find the right place to start.",
        "services_text": "Choose a category and describe your job. If it is not listed, tell us about it in the form.",
        "all_services": "All services",
        "browse_services": "Explore all services",
        "cta_title": "What needs sorting today?",
        "cta_text": "Start with a short description. The rest can be simple.",
        "footer_line": "Local jobs. Good people.",
        "services_page_kicker": "SERVICE DIRECTORY",
        "services_page_title": "Where shall we start?",
        "services_page_text": "Choose a service and describe your job. We are starting with home services in Poznań and nearby.",
        "service_action": "Describe your job",
        "request_kicker": "THE FIRST STEP",
        "request_title": "Tell us what you need.",
        "request_text": "A few useful details help us understand what you are looking for.",
        "form_category": "What service do you need?",
        "form_choose": "Choose a category",
        "form_location": "Where is the job?",
        "form_location_placeholder": "Neighbourhood or town",
        "form_details": "What needs doing?",
        "form_details_placeholder": "A few sentences: what, when, and anything important to know.",
        "form_name": "What is your name?",
        "form_contact": "Phone or email",
        "form_contact_placeholder": "+48 000 000 000 or email address",
        "form_consent": "I agree to storing my details and being contacted about this request.",
        "form_submit": "Send request",
        "form_privacy": "We only ask for details needed to handle your request.",
        "form_demo_notice": "Your request is saved in the system. An email notification is sent to the owner once email is configured; requests are not automatically forwarded to service providers.",
        "form_success": "Thanks — your request has been saved.",
        "form_email_sent": "An email notification about your request was sent to the site owner.",
        "form_email_not_configured": "Your request was saved, but email notifications are not configured yet. Contact us directly via WhatsApp or Telegram.",
        "form_email_failed": "Your request was saved, but the email notification could not be sent. Contact us directly via WhatsApp or Telegram.",
        "form_error": "Please check the form and complete all required fields.",
        "back_services": "Back to services",
        "contact_whatsapp": "WhatsApp",
        "contact_telegram": "Telegram",
        "direct_contact": "Prefer to message us directly?",
        "language_name": {"pl": "PL", "uk": "UA", "en": "EN"},
        "services": [
            {"id": "renovation", "icon": "✳", "name": "Renovation & finishing", "description": "Painting, tiling, plastering and home refreshes."},
            {"id": "plumbing", "icon": "↗", "name": "Plumbing", "description": "Tap repairs, installations and urgent leaks."},
            {"id": "electrical", "icon": "⌁", "name": "Electrical", "description": "Lighting, outlets and safe installations."},
            {"id": "cleaning", "icon": "◌", "name": "Cleaning", "description": "Regular, post-renovation or move-out cleaning."},
            {"id": "moving", "icon": "▧", "name": "Moving", "description": "Transport, packing and moving-day help."},
            {"id": "furniture", "icon": "⌂", "name": "Furniture & assembly", "description": "Assembly, mounting and small carpentry jobs."},
            {"id": "garden", "icon": "❋", "name": "Garden", "description": "Garden care, trimming and seasonal prep."},
            {"id": "other", "icon": "＋", "name": "Something else", "description": "Can't find your service? Tell us what you need."},
        ],
    },
}


def get_connection():
    database_url = current_app.config["DATABASE_URL"]
    if database_url:
        import psycopg

        return psycopg.connect(database_url)

    database_path = Path(current_app.config["DATABASE"])
    database_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(database_path)


def execute_query(connection, query: str, parameters: tuple = ()):
    if current_app.config["DATABASE_URL"]:
        query = query.replace("?", "%s")
    return connection.execute(query, parameters)


def send_request_notification(
    *, service_name: str, values: dict[str, str], language: str
) -> str:
    username = current_app.config["SMTP_USERNAME"]
    password = current_app.config["SMTP_PASSWORD"]
    if not username or not password:
        current_app.logger.error(
            "Service request email notification is not configured; "
            "set SMTP_USERNAME and SMTP_PASSWORD."
        )
        return "not_configured"

    message = EmailMessage()
    message["Subject"] = f"New Spplot request: {service_name}"
    message["From"] = current_app.config["MAIL_FROM"] or username
    message["To"] = current_app.config["MAIL_TO"]
    message.set_content(
        "\n".join(
            (
                "A new service request was submitted on Spplot.",
                "",
                f"Language: {language}",
                f"Service: {service_name}",
                f"Location: {values['location']}",
                f"Name: {values['name']}",
                f"Contact: {values['contact']}",
                "",
                "Request details:",
                values["details"],
            )
        )
    )

    try:
        with smtplib.SMTP_SSL(
            current_app.config["SMTP_HOST"],
            current_app.config["SMTP_PORT"],
            timeout=15,
            context=ssl.create_default_context(),
        ) as server:
            server.login(username, password)
            server.send_message(message)
    except (smtplib.SMTPException, OSError):
        current_app.logger.exception(
            "Failed to send service request notification by email."
        )
        return "failed"

    return "sent"


def initialize_database() -> None:
    with closing(get_connection()) as connection:
        if current_app.config["DATABASE_URL"]:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS service_requests (
                    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                    category TEXT NOT NULL,
                    location TEXT NOT NULL,
                    details TEXT NOT NULL,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        else:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS service_requests (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    location TEXT NOT NULL,
                    details TEXT NOT NULL,
                    name TEXT NOT NULL,
                    contact TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        connection.commit()


def get_language() -> str:
    requested = request.values.get("lang", "pl")
    return requested if requested in LANGUAGES else "pl"


def render_page(template: str, *, lang: str | None = None, **context):
    lang = lang or get_language()
    copy = COPY[lang]
    return render_template(
        template,
        lang=lang,
        copy=copy,
        page_title=context.pop("page_title", copy["site_title"]),
        **context,
    )


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE_URL=os.environ.get("DATABASE_URL"),
        DATABASE=os.environ.get(
            "DATABASE_PATH", str(Path(app.instance_path) / "site.db")
        ),
        SMTP_HOST=os.environ.get("SMTP_HOST", "smtp.gmail.com"),
        SMTP_PORT=int(os.environ.get("SMTP_PORT", "465")),
        SMTP_USERNAME=os.environ.get(
            "SMTP_USERNAME", os.environ.get("MAIL_TO", "danildyad@gmail.com")
        ),
        SMTP_PASSWORD=os.environ.get("SMTP_PASSWORD", ""),
        MAIL_FROM=os.environ.get("MAIL_FROM", ""),
        MAIL_TO=os.environ.get("MAIL_TO", "danildyad@gmail.com"),
    )
    if test_config:
        app.config.update(test_config)
    if os.environ.get("VERCEL") and not app.config["DATABASE_URL"]:
        raise RuntimeError(
            "Set DATABASE_URL to a persistent PostgreSQL database before deploying to Vercel."
        )

    with app.app_context():
        initialize_database()

    @app.get("/")
    def index():
        lang = get_language()
        return render_page("home.html", lang=lang)

    @app.get("/services")
    def services():
        lang = get_language()
        return render_page(
            "services.html", lang=lang, page_title=f"{COPY[lang]['services_page_title']} — Spplot"
        )

    @app.route("/request", methods=["GET", "POST"])
    def request_service():
        lang = get_language()
        copy = COPY[lang]
        services_by_id = {service["id"]: service for service in copy["services"]}
        service_id = request.values.get("category", "")
        if service_id not in services_by_id:
            service_id = ""

        values = {
            "category": service_id,
            "location": request.values.get("location", "").strip(),
            "details": request.values.get("details", "").strip(),
            "name": request.values.get("name", "").strip(),
            "contact": request.values.get("contact", "").strip(),
        }
        error = None
        sent = request.method == "GET" and request.args.get("sent") == "1"
        email_status = (
            request.args.get("email")
            if request.args.get("email") in ("sent", "not_configured", "failed")
            else None
        )

        if request.method == "POST":
            if (
                service_id not in SERVICE_IDS
                or len(values["location"]) > 120
                or not values["location"]
                or len(values["details"]) > 3000
                or not values["details"]
                or len(values["name"]) > 100
                or not values["name"]
                or len(values["contact"]) > 200
                or not values["contact"]
                or request.form.get("consent") != "yes"
            ):
                error = copy["form_error"]
            else:
                with closing(get_connection()) as connection:
                    execute_query(
                        connection,
                        """
                        INSERT INTO service_requests
                            (category, location, details, name, contact)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            service_id,
                            values["location"],
                            values["details"],
                            values["name"],
                            values["contact"],
                        ),
                    )
                    connection.commit()
                email_status = send_request_notification(
                    service_name=services_by_id[service_id]["name"],
                    values=values,
                    language=lang,
                )
                return redirect(
                    url_for(
                        "request_service",
                        lang=lang,
                        sent="1",
                        email=email_status,
                    ),
                    code=303,
                )

        status_code = 400 if error else 200
        return (
            render_page(
                "request.html",
                lang=lang,
                page_title=f"{copy['request_title']} — Spplot",
                values=values,
                error=error,
                sent=sent,
                email_status=email_status if sent else None,
                consented=not sent and request.form.get("consent") == "yes",
            ),
            status_code,
        )

    @app.get("/health")
    def health():
        with closing(get_connection()) as connection:
            execute_query(connection, "SELECT 1").fetchone()
        return {"status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    print("Spplot jest dostępny pod adresem: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000)
