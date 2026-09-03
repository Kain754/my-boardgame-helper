from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, GameRule
import os
import subprocess

app = FastAPI()

# --- ЗАПУСК ИНДЕКСАЦИИ PDF ПРИ СТАРТЕ СЕРВЕРА ---
@app.on_event("startup")
def startup_event():
    print("🚀 Запуск индексации PDF...")
    try:
        result = subprocess.run(
            ["python", "extract_pdf.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print(result.stdout)
        if result.stderr:
            print("Ошибки:", result.stderr)
    except Exception as e:
        print(f"❌ Ошибка индексации: {e}")

# --- НАСТРОЙКА CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchQuery(BaseModel):
    query: str
    game_name: str = None

# --- ЭНДПОИНТ ПОИСКА ---
@app.post("/search")
def search_rules(search: SearchQuery):
    db = SessionLocal()
    
    query = db.query(GameRule)
    
    if search.game_name and search.game_name != "all":
        query = query.filter(GameRule.game_name == search.game_name)
    
    query = query.filter(GameRule.content.ilike(f"%{search.query}%"))
    results = query.limit(10).all()
    db.close()
    
    if not results:
        return {"results": [], "message": "Ничего не найдено"}
    
    pages = {}
    for r in results:
        key = f"{r.game_name}_{r.page_number}"
        if key not in pages:
            pages[key] = {
                "game": r.game_name,
                "page": r.page_number,
                "image": r.image,
                "snippets": []
            }
        pages[key]["snippets"].append(r.content[:200] + "...")
    
    return {"results": list(pages.values())}

# --- ЭНДПОИНТ СПИСОК ИГР ---
@app.get("/games")
def list_games():
    db = SessionLocal()
    games = db.query(GameRule.game_name).distinct().all()
    db.close()
    return [g[0] for g in games]

# --- ЭНДПОИНТ ПРОВЕРКИ ---
@app.get("/")
def root():
    return {"message": "Помощник по правилам API работает"}

@app.get("/health")
def health():
    return {"status": "ok"}

# --- ЭНДПОИНТ ДЛЯ РУЧНОЙ ЗАГРУЗКИ (на случай, если автоиндексация не сработала) ---
@app.post("/admin/load-rules")
def load_rules():
    try:
        result = subprocess.run(
            ["python", "extract_pdf.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        return {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# --- ЭНДПОИНТ ДЛЯ ОТЛАДКИ (проверка наличия файлов) ---
@app.get("/debug/files")
def debug_files():
    import os
    files = []
    for root, dirs, filenames in os.walk("."):
        for f in filenames:
            files.append(os.path.join(root, f))
    return {"files": files[:50]}
