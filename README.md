# test-secunda
Тестовое задание от secunda

Вот просто набор команд (без скриптов), в нужном порядке.

### 1) Поднять контейнеры

```bash
docker compose up --build -d
```

### 2) Накатить миграции внутри `api`

```bash
docker compose exec api sh -lc "cd /app/app && uv run alembic upgrade head"
```

### 3) Засеять базу (seed) внутри `db`

### 3.1) Войти в контейнер с бд
```bash
docker compose exec -T db psql -U postgres -d "secunda-test"
```

### 3.2) Создать тестовые данные
```bash
INSERT INTO addresses (country, city, street, house, building, lat, lon)
VALUES
  ('Россия', 'Москва', 'Тверская', 1, 2, 55.757000, 37.615000),
  ('Россия', 'Санкт-Петербург', 'Невский проспект', 10, NULL, 59.934300, 30.335100);

WITH
food AS (
  INSERT INTO activities (name, parent_id)
  VALUES ('Еда', NULL)
  RETURNING id
),
food_children AS (
  INSERT INTO activities (name, parent_id)
  SELECT x.name, food.id
  FROM food
  CROSS JOIN (VALUES
    ('Мясная продукция'),
    ('Молочная продукция')
  ) AS x(name)
  RETURNING id, name, parent_id
),

cars AS (
  INSERT INTO activities (name, parent_id)
  VALUES ('Автомобили', NULL)
  RETURNING id
),
cars_children AS (
  INSERT INTO activities (name, parent_id)
  SELECT x.name, cars.id
  FROM cars
  CROSS JOIN (VALUES
    ('Грузовые'),
    ('Легковые')
  ) AS x(name)
  RETURNING id, name, parent_id
),

passenger AS (
  SELECT id
  FROM cars_children
  WHERE name = 'Легковые'
),
passenger_children AS (
  INSERT INTO activities (name, parent_id)
  SELECT x.name, passenger.id
  FROM passenger
  CROSS JOIN (VALUES
    ('Запчасти'),
    ('Аксессуары')
  ) AS x(name)
  RETURNING id
)
SELECT 1;

WITH meat AS (
  SELECT a.id
  FROM activities a
  JOIN activities p ON p.id = a.parent_id
  WHERE a.name = 'Мясная продукция'
    AND p.name = 'Еда'
  ORDER BY a.id
  LIMIT 1
)
INSERT INTO activities (name, parent_id)
SELECT x.name, meat.id
FROM meat
CROSS JOIN (VALUES
  ('Курица'),
  ('Говядина'),
  ('Свинина')
) AS x(name);

WITH
a1 AS (
  SELECT id
  FROM addresses
  WHERE country='Россия' AND city='Москва' AND street='Тверская' AND house=1 AND building=2
  ORDER BY id LIMIT 1
),
a2 AS (
  SELECT id
  FROM addresses
  WHERE country='Россия' AND city='Санкт-Петербург' AND street='Невский проспект' AND house=10 AND building IS NULL
  ORDER BY id LIMIT 1
),
ins_org AS (
  INSERT INTO organizations (name, address_id)
  VALUES
    ('ООО "Рога и Копыта"', (SELECT id FROM a1)),
    ('ИП "Молочный дом"', (SELECT id FROM a1)),
    ('ООО "Мясной двор"', (SELECT id FROM a1)),
    ('ООО "АвтоМир"', (SELECT id FROM a2)),
    ('ООО "Запчасть-Сервис"', (SELECT id FROM a2))
  RETURNING id, name
)
INSERT INTO organization_phones (organization_id, phone)
SELECT o.id, x.phone
FROM ins_org o
JOIN (VALUES
  ('ООО "Рога и Копыта"', '2-222-222'),
  ('ООО "Рога и Копыта"', '3-333-333'),
  ('ООО "Рога и Копыта"', '8-923-666-13-13'),
  ('ИП "Молочный дом"', '8-800-100-00-01'),
  ('ИП "Молочный дом"', '8-800-100-00-02'),
  ('ООО "Мясной двор"', '8-495-111-11-11'),
  ('ООО "АвтоМир"', '8-812-222-22-22'),
  ('ООО "АвтоМир"', '8-812-333-33-33'),
  ('ООО "Запчасть-Сервис"', '8-812-444-44-44')
) AS x(org_name, phone)
  ON x.org_name = o.name;

INSERT INTO organization_activities (organization_id, activity_id)
SELECT o.id, a.id
FROM organizations o
JOIN (VALUES
  ('ООО "Рога и Копыта"', 'Молочная продукция'),
  ('ООО "Рога и Копыта"', 'Мясная продукция'),
  ('ИП "Молочный дом"', 'Молочная продукция'),
  ('ООО "Мясной двор"', 'Мясная продукция'),
  ('ООО "АвтоМир"', 'Грузовые'),
  ('ООО "АвтоМир"', 'Легковые'),
  ('ООО "Запчасть-Сервис"', 'Запчасти')
) AS x(org_name, activity_name)
  ON x.org_name = o.name
JOIN activities a
  ON a.name = x.activity_name;
```

### 4) Проверка (по желанию)

```bash
docker compose exec db psql -U postgres -d "secunda-test" -c "select count(*) from addresses;"
docker compose exec db psql -U postgres -d "secunda-test" -c "select count(*) from organizations;"
```

### 5) Остановить

```bash
docker compose down
```
