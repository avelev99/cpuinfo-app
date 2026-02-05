# CPU Info CLI

Конзолно приложение за извеждане на информация за процесора и основни системни параметри.

## Основни възможности
- Модел/бранд на CPU, архитектура, ядра и нишки
- Честоти (min/max/current) и текущо натоварване
- Основна системна информация (OS, hostname, uptime)
- Памет (RAM) – общо и свободно
- JSON режим за лесна интеграция

## Бърз старт (uv)
```bash
uv venv .venv
uv pip install -r requirements.txt
uv run python main.py
```

## Бърз старт (без uv)
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## CLI опции
- `--json` – извежда чист JSON
- `--full` / `--verbose` – детайлен режим
- `--no-color` – без оцветяване
- `--wait-exit` – показва `Press any key to exit...` и изчаква клавиш
- `--no-wait-exit` – изключва автоматичното изчакване при Windows `.exe`

## Build (Windows)
```powershell
.\build_windows.ps1
```
Резултатът е в `dist\cpu_info.exe`.
