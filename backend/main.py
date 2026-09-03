from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database import SessionLocal, GameRule

app = FastAPI()

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

@app.get("/games")
def list_games():
    db = SessionLocal()
    games = db.query(GameRule.game_name).distinct().all()
    db.close()
    return [g[0] for g in games]

@app.get("/")
def root():
    return {"message": "Помощник по правилам API работает"}

@app.get("/health")
def health():
    return {"status": "ok"}
