from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, GameRule

# --- 1. Создаем приложение ---
app = FastAPI(title="Помощник по правилам", description="API для поиска по PDF-правилам")

# --- 2. Настройка CORS (разрешаем запросы с фронтенда) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Адрес вашего React-приложения
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)


# --- 3. Модель для поискового запроса ---
class SearchQuery(BaseModel):
    query: str
    game_name: str = None  # Если None — ищем по всем играм


# --- 4. Эндпоинт для поиска ---
@app.post("/search")
def search_rules(search: SearchQuery):
    """
    Поиск по тексту правил.
    Возвращает страницы с найденными фрагментами и их изображения.
    """
    db = SessionLocal()

    # Базовый запрос
    query = db.query(GameRule)

    # Фильтр по названию игры (если указано и не "all")
    if search.game_name and search.game_name != "all":
        query = query.filter(GameRule.game_name == search.game_name)

    # Поиск по тексту (регистронезависимый)
    query = query.filter(GameRule.content.ilike(f"%{search.query}%"))

    # Берем первые 10 результатов
    results = query.limit(10).all()
    db.close()

    # Если ничего не найдено
    if not results:
        return {"results": [], "message": "Ничего не найдено"}

    # Группируем по страницам (чтобы не показывать одну страницу несколько раз)
    pages = {}
    for r in results:
        key = f"{r.game_name}_{r.page_number}"
        if key not in pages:
            pages[key] = {
                "game": r.game_name,
                "page": r.page_number,
                "image": r.image,  # base64 картинка
                "snippets": []
            }
        # Добавляем найденный фрагмент текста (первые 200 символов)
        pages[key]["snippets"].append(r.content[:200] + "...")

    return {
        "results": list(pages.values()),
        "message": f"Найдено на {len(pages)} страницах"
    }


# --- 5. Эндпоинт для получения списка игр ---
@app.get("/games")
def list_games():
    """
    Возвращает список всех игр, загруженных в базу данных.
    """
    db = SessionLocal()
    games = db.query(GameRule.game_name).distinct().all()
    db.close()
    return [g[0] for g in games]


# --- 6. Эндпоинт для проверки статуса бэкенда ---
@app.get("/")
def root():
    return {
        "message": "Помощник по правилам API работает!",
        "endpoints": {
            "/search": "POST - поиск по правилам",
            "/games": "GET - список игр",
            "/docs": "GET - документация Swagger"
        }
    }


# --- 7. Эндпоинт для проверки здоровья сервиса ---
@app.get("/health")
def health():
    return {"status": "ok"}


# --- 8. (Опционально) Запуск напрямую ---
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)