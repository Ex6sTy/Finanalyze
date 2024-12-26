# Finanalyze

**Finanalyze** – это Python-приложение для анализа банковских операций. Программа предоставляет различные аналитические сервисы, включая выгоду по категориям кешбэка, округление трат в копилку, поиск по описаниям операций, а также отчеты по категориям.

---

## 🗋 Функционал

### Веб-страницы
1. **Главная страница**: отображает общую информацию о загруженных данных.
2. **Страница событий**: предоставляет анализ событий и категорий.

### Сервисы
1. **Анализ выгодных категорий кешбэка**: определяет наиболее выгодные категории за выбранный период.
2. **Инвесткопилка**: позволяет копить через округление трат.
3. **Простой поиск**: ищет транзакции по ключевым словам.
4. **Поиск переводов физическим лицам**: фильтрует переводы по шаблону описания.

### Отчеты
1. **Траты по категориям**: анализирует траты за выбранный период.
2. **Траты по дням недели**: предоставляет информацию о тратах, распределенных по будням и выходным.

---

## 🚀 Установка

### Требования:
- Python 3.10 или выше
- Poetry для управления зависимостями

### Шаги установки:
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/Finanalyze.git
   cd Finanalyze
   ```
2. Установите зависимости:
   ```bash
   poetry install
   ```
3. Активируйте виртуальное окружение:
   ```bash
   poetry shell
   ```
   
## 📈 Использование

### Запуск приложения:
1. Убедитесь, что вы находитесь в виртуальном окружении:
   ```bash
   poetry shell
   ``` 
2. Запустите основное приложение:
   ```bash
   python src/main.py
   ```
 ### Запуск тестов:
1. Выполните тестирование, чтобы убедиться в корректной работе всех модулей
   ```bash
   pytest
   ```

 ### Проверка кода линтерами:
1. Запустите линтеры, чтобы проверить код на соответствие стилям и стандартам:
   ```bash
   poetry run lint
   ```