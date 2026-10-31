# EXPLAIN Baseline — New Features

Generated: 2026-10-29T18:10:47.425751+00:00

Dataset: 10 households, 100 categories, 100,000 transactions, 500 recurring templates, 1,000 report jobs

All plans use `EXPLAIN (ANALYZE, BUFFERS)` with literal-bound parameters.

---


## get_all_categories


### `household_id=1`

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id, budgets_1.id AS id_1, budgets_1.goal, budgets_1.currency, budgets_1.category_id 
FROM categories LEFT OUTER JOIN budgets AS budgets_1 ON categories.id = budgets_1.category_id 
WHERE categories.household_id = 1 ORDER BY categories.id ASC
```

**Plan:**

```
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.104..0.106 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=5
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.045..0.072 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.004..0.012 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.026..0.026 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.009..0.017 rows=10 loops=1)
                    Filter: (household_id = 1)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=169
Planning Time: 1.118 ms
Execution Time: 0.186 ms
```


### `household_id=5`

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id, budgets_1.id AS id_1, budgets_1.goal, budgets_1.currency, budgets_1.category_id 
FROM categories LEFT OUTER JOIN budgets AS budgets_1 ON categories.id = budgets_1.category_id 
WHERE categories.household_id = 5 ORDER BY categories.id ASC
```

**Plan:**

```
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.062..0.063 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=2
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.037..0.052 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.002..0.009 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.019..0.019 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.008..0.012 rows=10 loops=1)
                    Filter: (household_id = 5)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.168 ms
Execution Time: 0.089 ms
```


### `household_id=10`

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id, budgets_1.id AS id_1, budgets_1.goal, budgets_1.currency, budgets_1.category_id 
FROM categories LEFT OUTER JOIN budgets AS budgets_1 ON categories.id = budgets_1.category_id 
WHERE categories.household_id = 10 ORDER BY categories.id ASC
```

**Plan:**

```
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.058..0.060 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=2
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.043..0.050 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.002..0.009 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.017..0.017 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.010..0.012 rows=10 loops=1)
                    Filter: (household_id = 10)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.144 ms
Execution Time: 0.085 ms
```


## get_category


### `household_id=1, category_id=1`

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id, budgets_1.id AS id_1, budgets_1.goal, budgets_1.currency, budgets_1.category_id 
FROM categories LEFT OUTER JOIN budgets AS budgets_1 ON categories.id = budgets_1.category_id 
WHERE categories.id = 1 AND categories.household_id = 1
```

**Plan:**

```
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.013..0.021 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.008..0.015 rows=1 loops=1)
        Filter: ((id = 1) AND (household_id = 1))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.003..0.003 rows=1 loops=1)
        Filter: (category_id = 1)
        Buffers: shared hit=1
Planning Time: 0.088 ms
Execution Time: 0.035 ms
```


### `household_id=5, category_id=50`

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id, budgets_1.id AS id_1, budgets_1.goal, budgets_1.currency, budgets_1.category_id 
FROM categories LEFT OUTER JOIN budgets AS budgets_1 ON categories.id = budgets_1.category_id 
WHERE categories.id = 50 AND categories.household_id = 5
```

**Plan:**

```
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.024..0.028 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.014..0.019 rows=1 loops=1)
        Filter: ((id = 50) AND (household_id = 5))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.008..0.008 rows=1 loops=1)
        Filter: (category_id = 50)
        Rows Removed by Filter: 49
        Buffers: shared hit=1
Planning Time: 0.126 ms
Execution Time: 0.044 ms
```


### `household_id=10, category_id=100`

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id, budgets_1.id AS id_1, budgets_1.goal, budgets_1.currency, budgets_1.category_id 
FROM categories LEFT OUTER JOIN budgets AS budgets_1 ON categories.id = budgets_1.category_id 
WHERE categories.id = 100 AND categories.household_id = 10
```

**Plan:**

```
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.026..0.027 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.015..0.016 rows=1 loops=1)
        Filter: ((id = 100) AND (household_id = 10))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.010..0.010 rows=1 loops=1)
        Filter: (category_id = 100)
        Rows Removed by Filter: 99
        Buffers: shared hit=1
Planning Time: 0.084 ms
Execution Time: 0.040 ms
```


## get_all_transactions (parent, selectinload)


### `household_id=1`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by 
FROM transactions 
WHERE transactions.household_id = 1 ORDER BY transactions.id ASC
```

**Plan:**

```
Sort  (cost=1874.79..1899.14 rows=9740 width=53) (actual time=7.541..8.058 rows=9918 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1121kB
  Buffers: shared hit=984 read=13
  ->  Bitmap Heap Scan on transactions  (cost=123.78..1229.53 rows=9740 width=53) (actual time=0.808..5.423 rows=9918 loops=1)
        Recheck Cond: (household_id = 1)
        Heap Blocks: exact=984
        Buffers: shared hit=984 read=13
        ->  Bitmap Index Scan on ix_transaction_household_id_date_desc  (cost=0.00..121.34 rows=9740 width=0) (actual time=0.653..0.654 rows=9918 loops=1)
              Index Cond: (household_id = 1)
              Buffers: shared read=13
Planning:
  Buffers: shared hit=138 read=1
Planning Time: 0.970 ms
Execution Time: 8.667 ms
```


### `household_id=5`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by 
FROM transactions 
WHERE transactions.household_id = 5 ORDER BY transactions.id ASC
```

**Plan:**

```
Sort  (cost=1890.45..1915.22 rows=9907 width=53) (actual time=6.088..6.571 rows=10146 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1138kB
  Buffers: shared hit=985 read=13
  ->  Bitmap Heap Scan on transactions  (cost=125.07..1232.91 rows=9907 width=53) (actual time=0.662..4.116 rows=10146 loops=1)
        Recheck Cond: (household_id = 5)
        Heap Blocks: exact=984
        Buffers: shared hit=985 read=13
        ->  Bitmap Index Scan on ix_transaction_household_id_date_desc  (cost=0.00..122.59 rows=9907 width=0) (actual time=0.533..0.534 rows=10146 loops=1)
              Index Cond: (household_id = 5)
              Buffers: shared hit=1 read=13
Planning Time: 0.123 ms
Execution Time: 7.126 ms
```


### `household_id=10`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by 
FROM transactions 
WHERE transactions.household_id = 10 ORDER BY transactions.id ASC
```

**Plan:**

```
Sort  (cost=1898.24..1923.21 rows=9990 width=53) (actual time=4.718..5.525 rows=9836 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1115kB
  Buffers: shared hit=985 read=12
  ->  Bitmap Heap Scan on transactions  (cost=125.72..1234.59 rows=9990 width=53) (actual time=0.686..3.159 rows=9836 loops=1)
        Recheck Cond: (household_id = 10)
        Heap Blocks: exact=984
        Buffers: shared hit=985 read=12
        ->  Bitmap Index Scan on ix_transaction_household_id_date_desc  (cost=0.00..123.22 rows=9990 width=0) (actual time=0.573..0.574 rows=9836 loops=1)
              Index Cond: (household_id = 10)
              Buffers: shared hit=1 read=12
Planning Time: 0.107 ms
Execution Time: 6.015 ms
```


### selectinload child query (representative)

The child query uses `WHERE categories.id IN (...)` with the ids of the
household's categories. We EXPLAIN it with the actual id list for household 1.

**SQL:**

```sql
SELECT categories.id, categories.name, categories.household_id 
FROM categories 
WHERE categories.id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
```

**Plan:**

```
Seq Scan on categories  (cost=0.03..2.52 rows=10 width=16) (actual time=0.006..0.013 rows=10 loops=1)
  Filter: (id = ANY ('{1,2,3,4,5,6,7,8,9,10}'::integer[]))
  Rows Removed by Filter: 90
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=3
Planning Time: 0.087 ms
Execution Time: 0.020 ms
```


## get_transaction


### `household_id=1, transaction_id=1`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id 
WHERE transactions.id = 1 AND transactions.household_id = 1
```

**Plan:**

```
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.018..0.019 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.010..0.011 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2
        ->  Index Scan using ix_transactions_household_id_id on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.010..0.010 rows=0 loops=1)
              Index Cond: ((household_id = 1) AND (id = 1))
              Buffers: shared hit=2
Planning:
  Buffers: shared hit=8
Planning Time: 0.165 ms
Execution Time: 0.040 ms
```


### `household_id=5, transaction_id=50000`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id 
WHERE transactions.id = 50000 AND transactions.household_id = 5
```

**Plan:**

```
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.015..0.015 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.009..0.009 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2
        ->  Index Scan using ix_transactions_household_id_id on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.009..0.009 rows=0 loops=1)
              Index Cond: ((household_id = 5) AND (id = 50000))
              Buffers: shared hit=2
Planning:
  Buffers: shared hit=4
Planning Time: 0.110 ms
Execution Time: 0.031 ms
```


### `household_id=10, transaction_id=100000`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id 
WHERE transactions.id = 100000 AND transactions.household_id = 10
```

**Plan:**

```
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.016..0.016 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.009..0.010 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2
        ->  Index Scan using ix_transactions_household_id_id on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.009..0.009 rows=0 loops=1)
              Index Cond: ((household_id = 10) AND (id = 100000))
              Buffers: shared hit=2
Planning:
  Buffers: shared hit=4
Planning Time: 0.109 ms
Execution Time: 0.032 ms
```


## get_total_amount_by_type (expense)


### `household_id=1, transaction_type=expense`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.type = 'expense' AND transactions.household_id = 1
```

**Plan:**

```
Aggregate  (cost=302.23..302.24 rows=1 width=8) (actual time=1.025..1.026 rows=1 loops=1)
  Buffers: shared hit=37
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..285.14 rows=6836 width=4) (actual time=0.044..0.689 rows=7013 loops=1)
        Index Cond: ((household_id = 1) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=37
Planning:
  Buffers: shared hit=3
Planning Time: 0.054 ms
Execution Time: 1.039 ms
```


### `household_id=5, transaction_type=expense`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.type = 'expense' AND transactions.household_id = 5
```

**Plan:**

```
Aggregate  (cost=304.84..304.85 rows=1 width=8) (actual time=1.207..1.207 rows=1 loops=1)
  Buffers: shared hit=35
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..287.46 rows=6952 width=4) (actual time=0.029..0.797 rows=7060 loops=1)
        Index Cond: ((household_id = 5) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=35
Planning Time: 0.077 ms
Execution Time: 1.228 ms
```


### `household_id=10, transaction_type=expense`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.type = 'expense' AND transactions.household_id = 10
```

**Plan:**

```
Aggregate  (cost=306.17..306.18 rows=1 width=8) (actual time=1.005..1.005 rows=1 loops=1)
  Buffers: shared hit=34
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..288.64 rows=7011 width=4) (actual time=0.018..0.652 rows=6920 loops=1)
        Index Cond: ((household_id = 10) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=34
Planning Time: 0.038 ms
Execution Time: 1.021 ms
```


## get_total_amount_by_type (income)


### `household_id=1, transaction_type=income`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.type = 'income' AND transactions.household_id = 1
```

**Plan:**

```
Aggregate  (cost=129.76..129.77 rows=1 width=8) (actual time=0.415..0.416 rows=1 loops=1)
  Buffers: shared hit=20
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..122.50 rows=2904 width=4) (actual time=0.017..0.277 rows=2905 loops=1)
        Index Cond: ((household_id = 1) AND (type = 'income'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=20
Planning Time: 0.039 ms
Execution Time: 0.425 ms
```


### `household_id=5, transaction_type=income`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.type = 'income' AND transactions.household_id = 5
```

**Plan:**

```
Aggregate  (cost=130.88..130.89 rows=1 width=8) (actual time=0.554..0.555 rows=1 loops=1)
  Buffers: shared hit=20
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..123.50 rows=2954 width=4) (actual time=0.015..0.381 rows=3086 loops=1)
        Index Cond: ((household_id = 5) AND (type = 'income'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=20
Planning Time: 0.031 ms
Execution Time: 0.569 ms
```


### `household_id=10, transaction_type=income`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.type = 'income' AND transactions.household_id = 10
```

**Plan:**

```
Aggregate  (cost=131.45..131.46 rows=1 width=8) (actual time=0.462..0.462 rows=1 loops=1)
  Buffers: shared hit=16
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..124.00 rows=2979 width=4) (actual time=0.020..0.315 rows=2916 loops=1)
        Index Cond: ((household_id = 10) AND (type = 'income'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=16
Planning Time: 0.036 ms
Execution Time: 0.478 ms
```


## get_category_balance


### `household_id=1, category_id=1`

**SQL:**

```sql
SELECT categories.name AS category_name, budgets.goal AS budget_goal, coalesce(sum(transactions.amount), 0) AS spent 
FROM categories JOIN budgets ON categories.id = budgets.category_id LEFT OUTER JOIN transactions ON categories.id = transactions.category_id AND transactions.type = 'expense' AND transactions.household_id = 1 
WHERE categories.id = 1 AND categories.household_id = 1 GROUP BY categories.id, categories.name, budgets.goal
```

**Plan:**

```
HashAggregate  (cost=11.16..11.17 rows=1 width=24) (actual time=0.250..0.251 rows=1 loops=1)
  Group Key: budgets.goal
  Batches: 1  Memory Usage: 24kB
  Buffers: shared hit=9
  ->  Nested Loop Left Join  (cost=0.42..10.90 rows=53 width=20) (actual time=0.032..0.173 rows=708 loops=1)
        Buffers: shared hit=9
        ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.009..0.017 rows=1 loops=1)
              Buffers: shared hit=2
              ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.005..0.009 rows=1 loops=1)
                    Filter: ((id = 1) AND (household_id = 1))
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
              ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.003..0.007 rows=1 loops=1)
                    Filter: (category_id = 1)
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
        ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.61 rows=53 width=8) (actual time=0.021..0.092 rows=708 loops=1)
              Index Cond: ((household_id = 1) AND (category_id = 1) AND (type = 'expense'::transaction_type))
              Heap Fetches: 0
              Buffers: shared hit=7
Planning:
  Buffers: shared hit=3
Planning Time: 0.133 ms
Execution Time: 0.276 ms
```


### `household_id=5, category_id=50`

**SQL:**

```sql
SELECT categories.name AS category_name, budgets.goal AS budget_goal, coalesce(sum(transactions.amount), 0) AS spent 
FROM categories JOIN budgets ON categories.id = budgets.category_id LEFT OUTER JOIN transactions ON categories.id = transactions.category_id AND transactions.type = 'expense' AND transactions.household_id = 5 
WHERE categories.id = 50 AND categories.household_id = 5 GROUP BY categories.id, categories.name, budgets.goal
```

**Plan:**

```
HashAggregate  (cost=11.13..11.14 rows=1 width=24) (actual time=0.258..0.258 rows=1 loops=1)
  Group Key: budgets.goal
  Batches: 1  Memory Usage: 24kB
  Buffers: shared hit=9
  ->  Nested Loop Left Join  (cost=0.42..10.87 rows=52 width=20) (actual time=0.030..0.171 rows=712 loops=1)
        Buffers: shared hit=9
        ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.009..0.014 rows=1 loops=1)
              Buffers: shared hit=2
              ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.005..0.007 rows=1 loops=1)
                    Filter: ((id = 50) AND (household_id = 5))
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
              ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.004..0.006 rows=1 loops=1)
                    Filter: (category_id = 50)
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
        ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.59 rows=52 width=8) (actual time=0.021..0.092 rows=712 loops=1)
              Index Cond: ((household_id = 5) AND (category_id = 50) AND (type = 'expense'::transaction_type))
              Heap Fetches: 0
              Buffers: shared hit=7
Planning:
  Buffers: shared hit=3
Planning Time: 0.089 ms
Execution Time: 0.283 ms
```


### `household_id=10, category_id=100`

**SQL:**

```sql
SELECT categories.name AS category_name, budgets.goal AS budget_goal, coalesce(sum(transactions.amount), 0) AS spent 
FROM categories JOIN budgets ON categories.id = budgets.category_id LEFT OUTER JOIN transactions ON categories.id = transactions.category_id AND transactions.type = 'expense' AND transactions.household_id = 10 
WHERE categories.id = 100 AND categories.household_id = 10 GROUP BY categories.id, categories.name, budgets.goal
```

**Plan:**

```
HashAggregate  (cost=11.32..11.33 rows=1 width=24) (actual time=0.285..0.285 rows=1 loops=1)
  Group Key: budgets.goal
  Batches: 1  Memory Usage: 24kB
  Buffers: shared hit=9
  ->  Nested Loop Left Join  (cost=0.42..11.03 rows=57 width=20) (actual time=0.030..0.199 rows=761 loops=1)
        Buffers: shared hit=9
        ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.013..0.014 rows=1 loops=1)
              Buffers: shared hit=2
              ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.007..0.007 rows=1 loops=1)
                    Filter: ((id = 100) AND (household_id = 10))
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
              ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.005..0.006 rows=1 loops=1)
                    Filter: (category_id = 100)
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
        ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.70 rows=57 width=8) (actual time=0.016..0.116 rows=761 loops=1)
              Index Cond: ((household_id = 10) AND (category_id = 100) AND (type = 'expense'::transaction_type))
              Heap Fetches: 0
              Buffers: shared hit=7
Planning:
  Buffers: shared hit=3
Planning Time: 0.103 ms
Execution Time: 0.306 ms
```


## get_all_categories_balance


### `household_id=1`

**SQL:**

```sql
SELECT categories.name AS category_name, budgets.goal AS budget_goal, coalesce(sum(transactions.amount), 0) AS spent 
FROM categories JOIN budgets ON categories.id = budgets.category_id LEFT OUTER JOIN transactions ON categories.id = transactions.category_id AND transactions.household_id = 1 AND transactions.type = 'expense' 
WHERE categories.household_id = 1 GROUP BY categories.id, categories.name, budgets.goal ORDER BY categories.id ASC
```

**Plan:**

```
GroupAggregate  (cost=16.24..109.73 rows=684 width=24) (actual time=0.657..3.371 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=64
  ->  Incremental Sort  (cost=16.24..97.76 rows=684 width=20) (actual time=0.307..2.755 rows=7013 loops=1)
        Sort Key: categories.id, budgets.goal
        Presorted Key: categories.id
        Full-sort Groups: 10  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        Pre-sorted Groups: 10  Sort Method: quicksort  Average Memory: 58kB  Peak Memory: 58kB
        Buffers: shared hit=64
        ->  Nested Loop Left Join  (cost=8.16..68.16 rows=684 width=20) (actual time=0.065..1.565 rows=7013 loops=1)
              Buffers: shared hit=64
              ->  Merge Join  (cost=7.74..8.39 rows=10 width=16) (actual time=0.046..0.054 rows=10 loops=1)
                    Merge Cond: (categories.id = budgets.category_id)
                    Buffers: shared hit=2
                    ->  Sort  (cost=2.42..2.44 rows=10 width=12) (actual time=0.019..0.020 rows=10 loops=1)
                          Sort Key: categories.id
                          Sort Method: quicksort  Memory: 25kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.004..0.009 rows=10 loops=1)
                                Filter: (household_id = 1)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
                    ->  Sort  (cost=5.32..5.57 rows=100 width=8) (actual time=0.024..0.025 rows=10 loops=1)
                          Sort Key: budgets.category_id
                          Sort Method: quicksort  Memory: 28kB
                          Buffers: shared hit=1
                          ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.002..0.009 rows=100 loops=1)
                                Buffers: shared hit=1
              ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.50 rows=48 width=8) (actual time=0.008..0.081 rows=701 loops=10)
                    Index Cond: ((household_id = 1) AND (category_id = categories.id) AND (type = 'expense'::transaction_type))
                    Heap Fetches: 0
                    Buffers: shared hit=62
Planning:
  Buffers: shared hit=15
Planning Time: 0.224 ms
Execution Time: 3.430 ms
```


### `household_id=5`

**SQL:**

```sql
SELECT categories.name AS category_name, budgets.goal AS budget_goal, coalesce(sum(transactions.amount), 0) AS spent 
FROM categories JOIN budgets ON categories.id = budgets.category_id LEFT OUTER JOIN transactions ON categories.id = transactions.category_id AND transactions.household_id = 5 AND transactions.type = 'expense' 
WHERE categories.household_id = 5 GROUP BY categories.id, categories.name, budgets.goal ORDER BY categories.id ASC
```

**Plan:**

```
GroupAggregate  (cost=16.32..110.80 rows=695 width=24) (actual time=0.625..3.226 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=63
  ->  Incremental Sort  (cost=16.32..98.64 rows=695 width=20) (actual time=0.318..2.632 rows=7060 loops=1)
        Sort Key: categories.id, budgets.goal
        Presorted Key: categories.id
        Full-sort Groups: 10  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        Pre-sorted Groups: 10  Sort Method: quicksort  Average Memory: 58kB  Peak Memory: 58kB
        Buffers: shared hit=63
        ->  Nested Loop Left Join  (cost=8.16..68.49 rows=695 width=20) (actual time=0.055..1.498 rows=7060 loops=1)
              Buffers: shared hit=63
              ->  Merge Join  (cost=7.74..8.39 rows=10 width=16) (actual time=0.039..0.047 rows=10 loops=1)
                    Merge Cond: (categories.id = budgets.category_id)
                    Buffers: shared hit=2
                    ->  Sort  (cost=2.42..2.44 rows=10 width=12) (actual time=0.013..0.014 rows=10 loops=1)
                          Sort Key: categories.id
                          Sort Method: quicksort  Memory: 25kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.005..0.008 rows=10 loops=1)
                                Filter: (household_id = 5)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
                    ->  Sort  (cost=5.32..5.57 rows=100 width=8) (actual time=0.020..0.023 rows=50 loops=1)
                          Sort Key: budgets.category_id
                          Sort Method: quicksort  Memory: 28kB
                          Buffers: shared hit=1
                          ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.002..0.009 rows=100 loops=1)
                                Buffers: shared hit=1
              ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.52 rows=49 width=8) (actual time=0.007..0.081 rows=706 loops=10)
                    Index Cond: ((household_id = 5) AND (category_id = categories.id) AND (type = 'expense'::transaction_type))
                    Heap Fetches: 0
                    Buffers: shared hit=61
Planning:
  Buffers: shared hit=15
Planning Time: 0.197 ms
Execution Time: 3.282 ms
```


### `household_id=10`

**SQL:**

```sql
SELECT categories.name AS category_name, budgets.goal AS budget_goal, coalesce(sum(transactions.amount), 0) AS spent 
FROM categories JOIN budgets ON categories.id = budgets.category_id LEFT OUTER JOIN transactions ON categories.id = transactions.category_id AND transactions.household_id = 10 AND transactions.type = 'expense' 
WHERE categories.household_id = 10 GROUP BY categories.id, categories.name, budgets.goal ORDER BY categories.id ASC
```

**Plan:**

```
GroupAggregate  (cost=16.34..111.21 rows=701 width=24) (actual time=0.642..3.398 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=62
  ->  Incremental Sort  (cost=16.34..98.94 rows=701 width=20) (actual time=0.328..2.795 rows=6920 loops=1)
        Sort Key: categories.id, budgets.goal
        Presorted Key: categories.id
        Full-sort Groups: 10  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        Pre-sorted Groups: 10  Sort Method: quicksort  Average Memory: 58kB  Peak Memory: 58kB
        Buffers: shared hit=62
        ->  Nested Loop Left Join  (cost=8.16..68.49 rows=701 width=20) (actual time=0.063..1.578 rows=6920 loops=1)
              Buffers: shared hit=62
              ->  Merge Join  (cost=7.74..8.39 rows=10 width=16) (actual time=0.045..0.051 rows=10 loops=1)
                    Merge Cond: (categories.id = budgets.category_id)
                    Buffers: shared hit=2
                    ->  Sort  (cost=2.42..2.44 rows=10 width=12) (actual time=0.013..0.015 rows=10 loops=1)
                          Sort Key: categories.id
                          Sort Method: quicksort  Memory: 25kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.007..0.009 rows=10 loops=1)
                                Filter: (household_id = 10)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
                    ->  Sort  (cost=5.32..5.57 rows=100 width=8) (actual time=0.021..0.025 rows=100 loops=1)
                          Sort Key: budgets.category_id
                          Sort Method: quicksort  Memory: 28kB
                          Buffers: shared hit=1
                          ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.002..0.009 rows=100 loops=1)
                                Buffers: shared hit=1
              ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.52 rows=49 width=8) (actual time=0.009..0.078 rows=692 loops=10)
                    Index Cond: ((household_id = 10) AND (category_id = categories.id) AND (type = 'expense'::transaction_type))
                    Heap Fetches: 0
                    Buffers: shared hit=60
Planning:
  Buffers: shared hit=15
Planning Time: 0.209 ms
Execution Time: 3.442 ms
```


## get_category_total_spent


### `household_id=1, category_id=1`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.category_id = 1 AND transactions.household_id = 1 AND transactions.type = 'expense'
```

**Plan:**

```
Aggregate  (cost=5.74..5.75 rows=1 width=8) (actual time=0.126..0.126 rows=1 loops=1)
  Buffers: shared hit=7
  ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.61 rows=53 width=4) (actual time=0.013..0.080 rows=708 loops=1)
        Index Cond: ((household_id = 1) AND (category_id = 1) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=7
Planning Time: 0.035 ms
Execution Time: 0.136 ms
```


### `household_id=5, category_id=50`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.category_id = 50 AND transactions.household_id = 5 AND transactions.type = 'expense'
```

**Plan:**

```
Aggregate  (cost=5.72..5.73 rows=1 width=8) (actual time=0.109..0.109 rows=1 loops=1)
  Buffers: shared hit=7
  ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.59 rows=52 width=4) (actual time=0.012..0.075 rows=712 loops=1)
        Index Cond: ((household_id = 5) AND (category_id = 50) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=7
Planning Time: 0.033 ms
Execution Time: 0.119 ms
```


### `household_id=10, category_id=100`

**SQL:**

```sql
SELECT coalesce(sum(transactions.amount), 0) AS coalesce_1 
FROM transactions 
WHERE transactions.category_id = 100 AND transactions.household_id = 10 AND transactions.type = 'expense'
```

**Plan:**

```
Aggregate  (cost=5.84..5.85 rows=1 width=8) (actual time=0.123..0.123 rows=1 loops=1)
  Buffers: shared hit=7
  ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.70 rows=57 width=4) (actual time=0.013..0.084 rows=761 loops=1)
        Index Cond: ((household_id = 10) AND (category_id = 100) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=7
Planning Time: 0.033 ms
Execution Time: 0.135 ms
```


## get_personal_household_id


### `user_id=1`

**SQL:**

```sql
SELECT household.id 
FROM household JOIN household_members ON household.id = household_members.household_id 
WHERE household_members.user_id = 1 AND household.is_personal IS true
```

**Plan:**

```
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.018..0.020 rows=1 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=2
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.003..0.003 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.009..0.010 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.004..0.005 rows=1 loops=1)
              Filter: (user_id = 1)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=55
Planning Time: 0.353 ms
Execution Time: 0.035 ms
```


### `user_id=10`

**SQL:**

```sql
SELECT household.id 
FROM household JOIN household_members ON household.id = household_members.household_id 
WHERE household_members.user_id = 10 AND household.is_personal IS true
```

**Plan:**

```
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.013..0.014 rows=1 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=2
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.002..0.003 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.006..0.006 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.002..0.002 rows=1 loops=1)
              Filter: (user_id = 10)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.069 ms
Execution Time: 0.027 ms
```


### `user_id=20`

**SQL:**

```sql
SELECT household.id 
FROM household JOIN household_members ON household.id = household_members.household_id 
WHERE household_members.user_id = 20 AND household.is_personal IS true
```

**Plan:**

```
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.015..0.016 rows=0 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=2
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.002..0.003 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.007..0.007 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.002..0.003 rows=1 loops=1)
              Filter: (user_id = 20)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.077 ms
Execution Time: 0.031 ms
```


## get_user_role


### `user_id=1, household_id=1`

**SQL:**

```sql
SELECT household_members.role 
FROM household_members 
WHERE household_members.user_id = 1 AND household_members.household_id = 1
```

**Plan:**

```
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.002..0.003 rows=1 loops=1)
  Filter: ((user_id = 1) AND (household_id = 1))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=3
Planning Time: 0.035 ms
Execution Time: 0.025 ms
```


### `user_id=10, household_id=5`

**SQL:**

```sql
SELECT household_members.role 
FROM household_members 
WHERE household_members.user_id = 10 AND household_members.household_id = 5
```

**Plan:**

```
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.003..0.003 rows=1 loops=1)
  Filter: ((user_id = 10) AND (household_id = 5))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning Time: 0.016 ms
Execution Time: 0.006 ms
```


### `user_id=20, household_id=10`

**SQL:**

```sql
SELECT household_members.role 
FROM household_members 
WHERE household_members.user_id = 20 AND household_members.household_id = 10
```

**Plan:**

```
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.003..0.003 rows=1 loops=1)
  Filter: ((user_id = 20) AND (household_id = 10))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning Time: 0.015 ms
Execution Time: 0.007 ms
```


## get_budget_by_category_id


### `category_id=1`

**SQL:**

```sql
SELECT budgets.id, budgets.goal, budgets.currency, budgets.category_id 
FROM budgets 
WHERE budgets.category_id = 1
```

**Plan:**

```
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.003..0.007 rows=1 loops=1)
  Filter: (category_id = 1)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.016 ms
Execution Time: 0.011 ms
```


### `category_id=50`

**SQL:**

```sql
SELECT budgets.id, budgets.goal, budgets.currency, budgets.category_id 
FROM budgets 
WHERE budgets.category_id = 50
```

**Plan:**

```
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.005..0.007 rows=1 loops=1)
  Filter: (category_id = 50)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.014 ms
Execution Time: 0.010 ms
```


### `category_id=100`

**SQL:**

```sql
SELECT budgets.id, budgets.goal, budgets.currency, budgets.category_id 
FROM budgets 
WHERE budgets.category_id = 100
```

**Plan:**

```
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.007..0.007 rows=1 loops=1)
  Filter: (category_id = 100)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.016 ms
Execution Time: 0.011 ms
```


## get_all_templates


### `household_id=1`

**SQL:**

```sql
SELECT recurring_transactions.id, recurring_transactions.household_id, recurring_transactions.category_id, recurring_transactions.created_by, recurring_transactions.amount, recurring_transactions.type, recurring_transactions.created_at, recurring_transactions.currency, recurring_transactions.note, recurring_transactions.frequency, recurring_transactions.next_run_date, recurring_transactions.is_active 
FROM recurring_transactions 
WHERE recurring_transactions.household_id = 1 ORDER BY recurring_transactions.id ASC
```

**Plan:**

```
Sort  (cost=14.66..14.79 rows=50 width=68) (actual time=0.057..0.059 rows=50 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 30kB
  Buffers: shared hit=7
  ->  Seq Scan on recurring_transactions  (cost=0.00..13.25 rows=50 width=68) (actual time=0.005..0.047 rows=50 loops=1)
        Filter: (household_id = 1)
        Rows Removed by Filter: 450
        Buffers: shared hit=7
Planning:
  Buffers: shared hit=52
Planning Time: 0.194 ms
Execution Time: 0.093 ms
```


### `household_id=5`

**SQL:**

```sql
SELECT recurring_transactions.id, recurring_transactions.household_id, recurring_transactions.category_id, recurring_transactions.created_by, recurring_transactions.amount, recurring_transactions.type, recurring_transactions.created_at, recurring_transactions.currency, recurring_transactions.note, recurring_transactions.frequency, recurring_transactions.next_run_date, recurring_transactions.is_active 
FROM recurring_transactions 
WHERE recurring_transactions.household_id = 5 ORDER BY recurring_transactions.id ASC
```

**Plan:**

```
Sort  (cost=14.66..14.79 rows=50 width=68) (actual time=0.039..0.042 rows=50 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 30kB
  Buffers: shared hit=7
  ->  Seq Scan on recurring_transactions  (cost=0.00..13.25 rows=50 width=68) (actual time=0.013..0.030 rows=50 loops=1)
        Filter: (household_id = 5)
        Rows Removed by Filter: 450
        Buffers: shared hit=7
Planning Time: 0.019 ms
Execution Time: 0.059 ms
```


### `household_id=10`

**SQL:**

```sql
SELECT recurring_transactions.id, recurring_transactions.household_id, recurring_transactions.category_id, recurring_transactions.created_by, recurring_transactions.amount, recurring_transactions.type, recurring_transactions.created_at, recurring_transactions.currency, recurring_transactions.note, recurring_transactions.frequency, recurring_transactions.next_run_date, recurring_transactions.is_active 
FROM recurring_transactions 
WHERE recurring_transactions.household_id = 10 ORDER BY recurring_transactions.id ASC
```

**Plan:**

```
Sort  (cost=14.66..14.79 rows=50 width=68) (actual time=0.038..0.040 rows=50 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 30kB
  Buffers: shared hit=7
  ->  Seq Scan on recurring_transactions  (cost=0.00..13.25 rows=50 width=68) (actual time=0.025..0.029 rows=50 loops=1)
        Filter: (household_id = 10)
        Rows Removed by Filter: 450
        Buffers: shared hit=7
Planning Time: 0.015 ms
Execution Time: 0.050 ms
```


## get_template_by_id


### `household_id=1, template_id=1`

**SQL:**

```sql
SELECT recurring_transactions.id, recurring_transactions.household_id, recurring_transactions.category_id, recurring_transactions.created_by, recurring_transactions.amount, recurring_transactions.type, recurring_transactions.created_at, recurring_transactions.currency, recurring_transactions.note, recurring_transactions.frequency, recurring_transactions.next_run_date, recurring_transactions.is_active 
FROM recurring_transactions 
WHERE recurring_transactions.id = 1 AND recurring_transactions.household_id = 1
```

**Plan:**

```
Index Scan using pk_recurring_transactions on recurring_transactions  (cost=0.27..8.29 rows=1 width=68) (actual time=0.014..0.014 rows=1 loops=1)
  Index Cond: (id = 1)
  Filter: (household_id = 1)
  Buffers: shared hit=3
Planning Time: 0.020 ms
Execution Time: 0.021 ms
```


### `household_id=5, template_id=250`

**SQL:**

```sql
SELECT recurring_transactions.id, recurring_transactions.household_id, recurring_transactions.category_id, recurring_transactions.created_by, recurring_transactions.amount, recurring_transactions.type, recurring_transactions.created_at, recurring_transactions.currency, recurring_transactions.note, recurring_transactions.frequency, recurring_transactions.next_run_date, recurring_transactions.is_active 
FROM recurring_transactions 
WHERE recurring_transactions.id = 250 AND recurring_transactions.household_id = 5
```

**Plan:**

```
Index Scan using pk_recurring_transactions on recurring_transactions  (cost=0.27..8.29 rows=1 width=68) (actual time=0.012..0.012 rows=1 loops=1)
  Index Cond: (id = 250)
  Filter: (household_id = 5)
  Buffers: shared hit=3
Planning Time: 0.019 ms
Execution Time: 0.022 ms
```


### `household_id=10, template_id=500`

**SQL:**

```sql
SELECT recurring_transactions.id, recurring_transactions.household_id, recurring_transactions.category_id, recurring_transactions.created_by, recurring_transactions.amount, recurring_transactions.type, recurring_transactions.created_at, recurring_transactions.currency, recurring_transactions.note, recurring_transactions.frequency, recurring_transactions.next_run_date, recurring_transactions.is_active 
FROM recurring_transactions 
WHERE recurring_transactions.id = 500 AND recurring_transactions.household_id = 10
```

**Plan:**

```
Index Scan using pk_recurring_transactions on recurring_transactions  (cost=0.27..8.29 rows=1 width=68) (actual time=0.010..0.010 rows=1 loops=1)
  Index Cond: (id = 500)
  Filter: (household_id = 10)
  Buffers: shared hit=3
Planning Time: 0.017 ms
Execution Time: 0.019 ms
```


## get_report_job_by_id


### `job_id=1`

**SQL:**

```sql
SELECT report_jobs.id, report_jobs.household_id, report_jobs.requested_by, report_jobs.status, report_jobs.file_path, report_jobs.error_message, report_jobs.created_at, report_jobs.completed_at, report_jobs.filters 
FROM report_jobs 
WHERE report_jobs.id = 1
```

**Plan:**

```
Index Scan using pk_report_jobs on report_jobs  (cost=0.28..8.29 rows=1 width=175) (actual time=0.014..0.015 rows=1 loops=1)
  Index Cond: (id = 1)
  Buffers: shared hit=3
Planning:
  Buffers: shared hit=43
Planning Time: 0.176 ms
Execution Time: 0.033 ms
```


### `job_id=500`

**SQL:**

```sql
SELECT report_jobs.id, report_jobs.household_id, report_jobs.requested_by, report_jobs.status, report_jobs.file_path, report_jobs.error_message, report_jobs.created_at, report_jobs.completed_at, report_jobs.filters 
FROM report_jobs 
WHERE report_jobs.id = 500
```

**Plan:**

```
Index Scan using pk_report_jobs on report_jobs  (cost=0.28..8.29 rows=1 width=175) (actual time=0.012..0.012 rows=1 loops=1)
  Index Cond: (id = 500)
  Buffers: shared hit=3
Planning Time: 0.016 ms
Execution Time: 0.021 ms
```


### `job_id=1000`

**SQL:**

```sql
SELECT report_jobs.id, report_jobs.household_id, report_jobs.requested_by, report_jobs.status, report_jobs.file_path, report_jobs.error_message, report_jobs.created_at, report_jobs.completed_at, report_jobs.filters 
FROM report_jobs 
WHERE report_jobs.id = 1000
```

**Plan:**

```
Index Scan using pk_report_jobs on report_jobs  (cost=0.28..8.29 rows=1 width=175) (actual time=0.014..0.014 rows=1 loops=1)
  Index Cond: (id = 1000)
  Buffers: shared hit=3
Planning Time: 0.014 ms
Execution Time: 0.022 ms
```


## get_transaction_for_report (no filters)


### `household_id=1`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1, users_1.id AS id_2, users_1.name AS name_1, users_1.email, users_1.password_hash, users_1.is_active, users_1.created_at 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id LEFT OUTER JOIN users AS users_1 ON users_1.id = transactions.created_by 
WHERE transactions.household_id = 1 ORDER BY transactions.date DESC
```

**Plan:**

```
Sort  (cost=1936.80..1961.15 rows=9740 width=209) (actual time=10.530..11.801 rows=9918 loops=1)
  Sort Key: transactions.date DESC
  Sort Method: quicksort  Memory: 2603kB
  Buffers: shared hit=1002
  ->  Hash Left Join  (cost=128.48..1291.54 rows=9740 width=209) (actual time=0.629..6.919 rows=9918 loops=1)
        Hash Cond: (transactions.created_by = users_1.id)
        Buffers: shared hit=999
        ->  Hash Left Join  (cost=127.03..1259.10 rows=9740 width=69) (actual time=0.614..5.225 rows=9918 loops=1)
              Hash Cond: (transactions.category_id = categories_1.id)
              Buffers: shared hit=998
              ->  Bitmap Heap Scan on transactions  (cost=123.78..1229.53 rows=9740 width=53) (actual time=0.581..3.229 rows=9918 loops=1)
                    Recheck Cond: (household_id = 1)
                    Heap Blocks: exact=984
                    Buffers: shared hit=997
                    ->  Bitmap Index Scan on ix_transaction_household_id_date_desc  (cost=0.00..121.34 rows=9740 width=0) (actual time=0.447..0.448 rows=9918 loops=1)
                          Index Cond: (household_id = 1)
                          Buffers: shared hit=13
              ->  Hash  (cost=2.00..2.00 rows=100 width=16) (actual time=0.025..0.025 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 13kB
                    Buffers: shared hit=1
                    ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.003..0.009 rows=100 loops=1)
                          Buffers: shared hit=1
        ->  Hash  (cost=1.20..1.20 rows=20 width=140) (actual time=0.010..0.010 rows=20 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 12kB
              Buffers: shared hit=1
              ->  Seq Scan on users users_1  (cost=0.00..1.20 rows=20 width=140) (actual time=0.001..0.003 rows=20 loops=1)
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=62
Planning Time: 0.358 ms
Execution Time: 12.298 ms
```


### `household_id=5`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1, users_1.id AS id_2, users_1.name AS name_1, users_1.email, users_1.password_hash, users_1.is_active, users_1.created_at 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id LEFT OUTER JOIN users AS users_1 ON users_1.id = transactions.created_by 
WHERE transactions.household_id = 5 ORDER BY transactions.date DESC
```

**Plan:**

```
Sort  (cost=1953.45..1978.21 rows=9907 width=209) (actual time=10.392..11.498 rows=10146 loops=1)
  Sort Key: transactions.date DESC
  Sort Method: quicksort  Memory: 2673kB
  Buffers: shared hit=1000
  ->  Hash Left Join  (cost=129.77..1295.91 rows=9907 width=209) (actual time=0.580..6.910 rows=10146 loops=1)
        Hash Cond: (transactions.created_by = users_1.id)
        Buffers: shared hit=1000
        ->  Hash Left Join  (cost=128.32..1262.94 rows=9907 width=69) (actual time=0.567..4.776 rows=10146 loops=1)
              Hash Cond: (transactions.category_id = categories_1.id)
              Buffers: shared hit=999
              ->  Bitmap Heap Scan on transactions  (cost=125.07..1232.91 rows=9907 width=53) (actual time=0.539..2.822 rows=10146 loops=1)
                    Recheck Cond: (household_id = 5)
                    Heap Blocks: exact=984
                    Buffers: shared hit=998
                    ->  Bitmap Index Scan on ix_transaction_household_id_date_desc  (cost=0.00..122.59 rows=9907 width=0) (actual time=0.427..0.427 rows=10146 loops=1)
                          Index Cond: (household_id = 5)
                          Buffers: shared hit=14
              ->  Hash  (cost=2.00..2.00 rows=100 width=16) (actual time=0.022..0.022 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 13kB
                    Buffers: shared hit=1
                    ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.002..0.007 rows=100 loops=1)
                          Buffers: shared hit=1
        ->  Hash  (cost=1.20..1.20 rows=20 width=140) (actual time=0.008..0.008 rows=20 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 12kB
              Buffers: shared hit=1
              ->  Seq Scan on users users_1  (cost=0.00..1.20 rows=20 width=140) (actual time=0.001..0.002 rows=20 loops=1)
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.206 ms
Execution Time: 11.995 ms
```


### `household_id=10`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1, users_1.id AS id_2, users_1.name AS name_1, users_1.email, users_1.password_hash, users_1.is_active, users_1.created_at 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id LEFT OUTER JOIN users AS users_1 ON users_1.id = transactions.created_by 
WHERE transactions.household_id = 10 ORDER BY transactions.date DESC
```

**Plan:**

```
Sort  (cost=1961.73..1986.70 rows=9990 width=209) (actual time=10.342..11.420 rows=9836 loops=1)
  Sort Key: transactions.date DESC
  Sort Method: quicksort  Memory: 2621kB
  Buffers: shared hit=999
  ->  Hash Left Join  (cost=130.41..1298.08 rows=9990 width=209) (actual time=0.555..6.922 rows=9836 loops=1)
        Hash Cond: (transactions.created_by = users_1.id)
        Buffers: shared hit=999
        ->  Hash Left Join  (cost=128.97..1264.84 rows=9990 width=69) (actual time=0.541..5.264 rows=9836 loops=1)
              Hash Cond: (transactions.category_id = categories_1.id)
              Buffers: shared hit=998
              ->  Bitmap Heap Scan on transactions  (cost=125.72..1234.59 rows=9990 width=53) (actual time=0.513..3.186 rows=9836 loops=1)
                    Recheck Cond: (household_id = 10)
                    Heap Blocks: exact=984
                    Buffers: shared hit=997
                    ->  Bitmap Index Scan on ix_transaction_household_id_date_desc  (cost=0.00..123.22 rows=9990 width=0) (actual time=0.399..0.399 rows=9836 loops=1)
                          Index Cond: (household_id = 10)
                          Buffers: shared hit=13
              ->  Hash  (cost=2.00..2.00 rows=100 width=16) (actual time=0.022..0.023 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 13kB
                    Buffers: shared hit=1
                    ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.003..0.009 rows=100 loops=1)
                          Buffers: shared hit=1
        ->  Hash  (cost=1.20..1.20 rows=20 width=140) (actual time=0.008..0.008 rows=20 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 12kB
              Buffers: shared hit=1
              ->  Seq Scan on users users_1  (cost=0.00..1.20 rows=20 width=140) (actual time=0.001..0.003 rows=20 loops=1)
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.226 ms
Execution Time: 11.895 ms
```


## get_transaction_for_report (with filters)


### `household_id=1, start_date=2025-01-01 00:00:00+00:00, end_date=2026-01-01 00:00:00+00:00, category_id=1`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1, users_1.id AS id_2, users_1.name AS name_1, users_1.email, users_1.password_hash, users_1.is_active, users_1.created_at 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id LEFT OUTER JOIN users AS users_1 ON users_1.id = transactions.created_by 
WHERE transactions.household_id = 1 AND transactions.date >= '2025-01-01 00:00:00+00:00' AND transactions.date <= '2026-01-01 00:00:00+00:00' AND transactions.type = 'expense' AND transactions.category_id = 1 ORDER BY transactions.date DESC
```

**Plan:**

```
Sort  (cost=183.14..183.20 rows=26 width=209) (actual time=1.184..1.202 rows=349 loops=1)
  Sort Key: transactions.date DESC
  Sort Method: quicksort  Memory: 104kB
  Buffers: shared hit=508
  ->  Hash Left Join  (cost=6.54..182.52 rows=26 width=209) (actual time=0.195..1.041 rows=349 loops=1)
        Hash Cond: (transactions.created_by = users_1.id)
        Buffers: shared hit=508
        ->  Nested Loop Left Join  (cost=5.09..180.99 rows=26 width=69) (actual time=0.178..0.961 rows=349 loops=1)
              Buffers: shared hit=507
              ->  Bitmap Heap Scan on transactions  (cost=5.09..178.42 rows=26 width=53) (actual time=0.170..0.868 rows=349 loops=1)
                    Recheck Cond: ((household_id = 1) AND (category_id = 1) AND (type = 'expense'::transaction_type))
                    Filter: ((date >= '2025-01-01 00:00:00+00'::timestamp with time zone) AND (date <= '2026-01-01 00:00:00+00'::timestamp with time zone))
                    Rows Removed by Filter: 359
                    Heap Blocks: exact=500
                    Buffers: shared hit=506
                    ->  Bitmap Index Scan on ix_transactions_household_id_category_id_type_amount  (cost=0.00..5.08 rows=53 width=0) (actual time=0.110..0.110 rows=708 loops=1)
                          Index Cond: ((household_id = 1) AND (category_id = 1) AND (type = 'expense'::transaction_type))
                          Buffers: shared hit=6
              ->  Materialize  (cost=0.00..2.25 rows=1 width=16) (actual time=0.000..0.000 rows=1 loops=349)
                    Buffers: shared hit=1
                    ->  Seq Scan on categories categories_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.004..0.004 rows=1 loops=1)
                          Filter: (id = 1)
                          Buffers: shared hit=1
        ->  Hash  (cost=1.20..1.20 rows=20 width=140) (actual time=0.010..0.010 rows=20 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 12kB
              Buffers: shared hit=1
              ->  Seq Scan on users users_1  (cost=0.00..1.20 rows=20 width=140) (actual time=0.002..0.003 rows=20 loops=1)
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=15
Planning Time: 0.295 ms
Execution Time: 1.280 ms
```


### `household_id=5, start_date=2024-06-01 00:00:00+00:00, end_date=2025-06-01 00:00:00+00:00, category_id=50`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1, users_1.id AS id_2, users_1.name AS name_1, users_1.email, users_1.password_hash, users_1.is_active, users_1.created_at 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id LEFT OUTER JOIN users AS users_1 ON users_1.id = transactions.created_by 
WHERE transactions.household_id = 5 AND transactions.date >= '2024-06-01 00:00:00+00:00' AND transactions.date <= '2025-06-01 00:00:00+00:00' AND transactions.type = 'expense' AND transactions.category_id = 50 ORDER BY transactions.date DESC
```

**Plan:**

```
Sort  (cost=179.64..179.68 rows=15 width=209) (actual time=0.847..0.859 rows=219 loops=1)
  Sort Key: transactions.date DESC
  Sort Method: quicksort  Memory: 75kB
  Buffers: shared hit=521
  ->  Hash Left Join  (cost=6.52..179.35 rows=15 width=209) (actual time=0.176..0.764 rows=219 loops=1)
        Hash Cond: (transactions.created_by = users_1.id)
        Buffers: shared hit=521
        ->  Nested Loop Left Join  (cost=5.07..177.85 rows=15 width=69) (actual time=0.165..0.713 rows=219 loops=1)
              Buffers: shared hit=520
              ->  Bitmap Heap Scan on transactions  (cost=5.07..175.41 rows=15 width=53) (actual time=0.157..0.649 rows=219 loops=1)
                    Recheck Cond: ((household_id = 5) AND (category_id = 50) AND (type = 'expense'::transaction_type))
                    Filter: ((date >= '2024-06-01 00:00:00+00'::timestamp with time zone) AND (date <= '2025-06-01 00:00:00+00'::timestamp with time zone))
                    Rows Removed by Filter: 493
                    Heap Blocks: exact=513
                    Buffers: shared hit=519
                    ->  Bitmap Index Scan on ix_transactions_household_id_category_id_type_amount  (cost=0.00..5.07 rows=52 width=0) (actual time=0.097..0.097 rows=712 loops=1)
                          Index Cond: ((household_id = 5) AND (category_id = 50) AND (type = 'expense'::transaction_type))
                          Buffers: shared hit=6
              ->  Materialize  (cost=0.00..2.25 rows=1 width=16) (actual time=0.000..0.000 rows=1 loops=219)
                    Buffers: shared hit=1
                    ->  Seq Scan on categories categories_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.005..0.005 rows=1 loops=1)
                          Filter: (id = 50)
                          Rows Removed by Filter: 49
                          Buffers: shared hit=1
        ->  Hash  (cost=1.20..1.20 rows=20 width=140) (actual time=0.007..0.008 rows=20 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 12kB
              Buffers: shared hit=1
              ->  Seq Scan on users users_1  (cost=0.00..1.20 rows=20 width=140) (actual time=0.001..0.002 rows=20 loops=1)
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.156 ms
Execution Time: 0.916 ms
```


### `household_id=10, start_date=2025-03-01 00:00:00+00:00, end_date=2026-03-01 00:00:00+00:00, category_id=100`

**SQL:**

```sql
SELECT transactions.id, transactions.amount, transactions.type, transactions.currency, transactions.date, transactions.note, transactions.category_id, transactions.household_id, transactions.created_by, categories_1.id AS id_1, categories_1.name, categories_1.household_id AS household_id_1, users_1.id AS id_2, users_1.name AS name_1, users_1.email, users_1.password_hash, users_1.is_active, users_1.created_at 
FROM transactions LEFT OUTER JOIN categories AS categories_1 ON categories_1.id = transactions.category_id LEFT OUTER JOIN users AS users_1 ON users_1.id = transactions.created_by 
WHERE transactions.household_id = 10 AND transactions.date >= '2025-03-01 00:00:00+00:00' AND transactions.date <= '2026-03-01 00:00:00+00:00' AND transactions.type = 'expense' AND transactions.category_id = 100 ORDER BY transactions.date DESC
```

**Plan:**

```
Sort  (cost=195.20..195.27 rows=29 width=209) (actual time=1.017..1.036 rows=395 loops=1)
  Sort Key: transactions.date DESC
  Sort Method: quicksort  Memory: 115kB
  Buffers: shared hit=541
  ->  Hash Left Join  (cost=6.59..194.49 rows=29 width=209) (actual time=0.192..0.865 rows=395 loops=1)
        Hash Cond: (transactions.created_by = users_1.id)
        Buffers: shared hit=541
        ->  Nested Loop Left Join  (cost=5.14..192.96 rows=29 width=69) (actual time=0.179..0.762 rows=395 loops=1)
              Buffers: shared hit=540
              ->  Bitmap Heap Scan on transactions  (cost=5.14..190.34 rows=29 width=53) (actual time=0.170..0.644 rows=395 loops=1)
                    Recheck Cond: ((household_id = 10) AND (category_id = 100) AND (type = 'expense'::transaction_type))
                    Filter: ((date >= '2025-03-01 00:00:00+00'::timestamp with time zone) AND (date <= '2026-03-01 00:00:00+00'::timestamp with time zone))
                    Rows Removed by Filter: 366
                    Heap Blocks: exact=533
                    Buffers: shared hit=539
                    ->  Bitmap Index Scan on ix_transactions_household_id_category_id_type_amount  (cost=0.00..5.13 rows=57 width=0) (actual time=0.107..0.107 rows=761 loops=1)
                          Index Cond: ((household_id = 10) AND (category_id = 100) AND (type = 'expense'::transaction_type))
                          Buffers: shared hit=6
              ->  Materialize  (cost=0.00..2.25 rows=1 width=16) (actual time=0.000..0.000 rows=1 loops=395)
                    Buffers: shared hit=1
                    ->  Seq Scan on categories categories_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.006..0.006 rows=1 loops=1)
                          Filter: (id = 100)
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
        ->  Hash  (cost=1.20..1.20 rows=20 width=140) (actual time=0.008..0.008 rows=20 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 12kB
              Buffers: shared hit=1
              ->  Seq Scan on users users_1  (cost=0.00..1.20 rows=20 width=140) (actual time=0.001..0.002 rows=20 loops=1)
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.187 ms
Execution Time: 1.103 ms
```
