Нужные провайдеры на RapidAPI и их зоны ответственности

GeoDB Cities (wft-geo-db.p.rapidapi.com) – уже используем; покрывает базовые сведения о городе (id, население, координаты, регион, часовой пояс). Ничего менять не нужно, лишь сохранить рабочий ключ.
Numbers API (numbersapi.p.rapidapi.com) – пригодится только для демонстрации/фактов; мы уже проверили, что текущий RapidAPI‑ключ подходит.
Numbeo Cost of Living / Prices / Rent / Quality of Life – нужны для cost_of_living_index, rent_price_index, housing_price_index, average_salary, а также для прокси-показателей качества жизни (культура, спорт, загрязнение и т.д.). На RapidAPI несколько пакетов от Numbeo, важно узнать точные X-RapidAPI-Host (чаще всего numbeo.p.rapidapi.com или numbeo-community.p.rapidapi.com).
TomTom Traffic Index (или аналогичный провайдер трафика) – используется для traffic_congestion_score.
World Happiness Report API (или любой сервис, отдающий happiness/health/education индексы по городам/странам) – для happiness_index, health_index, education_level_score. Нужен host и список эндпоинтов.
World Bank (GDP growth) – для economic_growth_rate. Есть официальное открытое API, но на RapidAPI тоже можно найти «World Bank Data»; нужен host.
Воздушные качества (если хотим альтернативу OpenWeather) – например, «World Air Quality Index» (world-air-quality-index.p.rapidapi.com) или «AirVisual» – пока на выбор.
При желании: API с crime/pollution/green spaces (есть у Numbeo), транспортными индексами, культурными событиями и т.д., если хотим обогатить модель.
Как узнаешь точные RapidAPI‑страницы (и, главное, X-RapidAPI-Host/эндпоинты), сообщи — проверю запросы и переведу код на requests.