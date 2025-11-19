import os
import shutil
from app import create_app, db
from app.models import User, Task, Category

def reset_database():
    # Удаляем папки
    if os.path.exists('migrations'):
        shutil.rmtree('migrations')
        print("✅ Папка migrations удалена")
    
    if os.path.exists('instance'):
        shutil.rmtree('instance') 
        print("✅ Папка instance удалена")
    
    # Создаем приложение
    app = create_app()
    
    with app.app_context():
        # Создаем папку instance
        os.makedirs('instance', exist_ok=True)
        
        # Создаем все таблицы напрямую
        db.create_all()
        print("✅ Все таблицы созданы напрямую")
        
        # Инициализируем миграции
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
        
        import subprocess
        subprocess.run(['flask', 'db', 'init'])
        subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial tables'])
        subprocess.run(['flask', 'db', 'upgrade'])
        
        print("✅ База данных полностью пересоздана!")

if __name__ == '__main__':
    reset_database()