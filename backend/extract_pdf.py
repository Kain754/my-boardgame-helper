import os
import base64
from database import SessionLocal, GameRule
import PyPDF2

def extract_pdf_to_db(pdf_path, game_name):
    """Извлекает текст из PDF и сохраняет в БД (без картинок для Render)"""
    
    if not os.path.exists(pdf_path):
        print(f"❌ Файл {pdf_path} не найден!")
        return

    db = SessionLocal()
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text() or ""
            
            # Для Render: не сохраняем картинки (их будет сложно загрузить)
            # Вместо этого оставляем поле image пустым
            rule = GameRule(
                game_name=game_name,
                page_number=page_num + 1,
                content=text,
                image=None,  # Картинки не сохраняем
                image_url=None
            )
            db.add(rule)
            print(f"   Страница {page_num + 1}: {len(text)} символов")
    
    db.commit()
    db.close()
    print(f"✅ {game_name} загружена! Страниц: {len(reader.pages)}")

def load_all_pdfs_from_folder(folder_path):
    """Загружает все PDF из папки в БД"""
    
    if not os.path.exists(folder_path):
        print(f"❌ Папка {folder_path} не найдена!")
        return

    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"❌ В папке {folder_path} нет PDF-файлов!")
        return

    print(f"📂 Найдено {len(pdf_files)} PDF-файлов:")
    for f in pdf_files:
        print(f"   - {f}")

    for pdf_file in pdf_files:
        game_name = os.path.splitext(pdf_file)[0]
        pdf_path = os.path.join(folder_path, pdf_file)
        extract_pdf_to_db(pdf_path, game_name)

if __name__ == "__main__":
    rules_folder = "../public/rules"

    if not os.path.exists(rules_folder):
        os.makedirs(rules_folder)
        print(f"📁 Создана папка: {rules_folder}")
        print("   Положите туда PDF-файлы с правилами и запустите скрипт снова.")
    else:
        load_all_pdfs_from_folder(rules_folder)
