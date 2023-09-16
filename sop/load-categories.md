

```sql
WITH RECURSIVE category_cte AS (
    SELECT id, name, parent_id, slug, created_by_id
    FROM supernotes.books_category
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.parent_id, c.slug, c.created_by_id
    FROM supernotes.books_category AS c
    JOIN category_cte AS ct ON c.parent_id = ct.id
)
SELECT id, name, parent_id, slug, created_by_id FROM category_cte;

WITH RECURSIVE category_cte AS (
    SELECT id, name, slug, parent_id,  CAST(NULL AS CHAR(100)) AS parent_slug, created_by_id
    FROM old_category
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.name, c.slug, c.parent_id, ct.slug AS parent_slug, c.created_by_id
    FROM old_category AS c
    JOIN category_cte AS ct ON c.parent_id = ct.id
)
SELECT id, name, slug, parent_id, parent_slug, created_by_id FROM category_cte ORDER BY parent_id;

INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id IS NULL ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 22;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 1 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 31;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 3 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 37;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 4  ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 39;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 6 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 40;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 9 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 47;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 11 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 47;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 13 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 61;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 14 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 62;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, parent_id, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 17 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 63;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, 18, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 50 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 68;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, 19, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 61 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 81;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, 50, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 68 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 83;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, 20, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 73 ORDER BY id;

SELECT * FROM pkm.category;
ALTER TABLE pkm.category AUTO_INCREMENT = 84;
INSERT INTO pkm.category (name, parent_id, slug, created_by_id, created_at, updated_at)
SELECT name, 21, slug, created_by_id, NOW(), NOW() FROM supernotes.books_category
WHERE parent_id = 83 ORDER BY id;
```

```python
from book.models import Category

def print_category_tree(category, level=0):
    print('-' * level + f"- {category.name} ({category.slug})")
    for subcategory in category.subcategories.all():
        print_category_tree(subcategory, level + 1)

root_categories = Category.objects.filter(parent__isnull=True)

for root_category in root_categories:
    print_category_tree(root_category)

cs = Category.objects.prefetch_related("subcategories").get(slug='computer-science')
print_category_tree(cs)
```

```sql
SET foreign_key_checks = 0;
DELETE FROM category WHERE id >= 291;
SET foreign_key_checks = 1;

SELECT * FROM category;

```