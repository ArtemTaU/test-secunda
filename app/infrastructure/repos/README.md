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
  RETURNING id
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

SELECT 'ok' AS Status;


WITH meat AS (
  SELECT a.id
  FROM activities a
  JOIN activities p ON p.id = a.parent_id
  WHERE a.name = 'Мясная продукция'
    AND p.name = 'Еда'
),
ins AS (
  INSERT INTO activities (name, parent_id)
  SELECT x.name, meat.id
  FROM meat
  CROSS JOIN (VALUES
    ('Курица'),
    ('Говядина'),
    ('Свининаэ')
  ) AS x(name)
  ON CONFLICT (parent_id, name) DO NOTHING
  RETURNING id, name, parent_id
)
SELECT * FROM ins;

INSERT INTO organizations (name, address_id)
VALUES
  ('ООО "Рога и Копыта"', 1),
  ('ИП "Молочный дом"', 1),
  ('ООО "Мясной двор"', 1),
  ('ООО "АвтоМир"', 2),
  ('ООО "Запчасть-Сервис"', 2)
RETURNING id, name, address_id;

INSERT INTO organization_phones (organization_id, phone)
VALUES
  (1, '2-222-222'),
  (1, '3-333-333'),
  (1, '8-923-666-13-13'),

  (2, '8-800-100-00-01'),
  (2, '8-800-100-00-02'),

  (3, '8-495-111-11-11'),

  (4, '8-812-222-22-22'),
  (4, '8-812-333-33-33'),

  (5, '8-812-444-44-44');

INSERT INTO organization_activities (organization_id, activity_id)
SELECT o.id, a.id
FROM ins_org o
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