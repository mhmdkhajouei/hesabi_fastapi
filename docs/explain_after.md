# EXPLAIN After Indexes

Generated: 2026-10-17T08:40:24.443037+00:00

Dataset: 10 households, 100 categories, 100,000 transactions

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
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.050..0.073 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.002..0.009 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.025..0.025 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.010..0.017 rows=10 loops=1)
                    Filter: (household_id = 1)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=161 read=8 dirtied=1
Planning Time: 2.830 ms
Execution Time: 0.197 ms
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
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.087..0.089 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=2
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.062..0.078 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.002..0.010 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.020..0.020 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.008..0.013 rows=10 loops=1)
                    Filter: (household_id = 5)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.163 ms
Execution Time: 0.124 ms
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
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.057..0.058 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=2
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.042..0.049 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.002..0.009 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.017..0.017 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.010..0.011 rows=10 loops=1)
                    Filter: (household_id = 10)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.126 ms
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
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.007..0.014 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.004..0.010 rows=1 loops=1)
        Filter: ((id = 1) AND (household_id = 1))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.002..0.002 rows=1 loops=1)
        Filter: (category_id = 1)
        Buffers: shared hit=1
Planning Time: 0.066 ms
Execution Time: 0.022 ms
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
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.014..0.018 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.008..0.011 rows=1 loops=1)
        Filter: ((id = 50) AND (household_id = 5))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.005..0.005 rows=1 loops=1)
        Filter: (category_id = 50)
        Rows Removed by Filter: 49
        Buffers: shared hit=1
Planning Time: 0.060 ms
Execution Time: 0.026 ms
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
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.022..0.023 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.012..0.012 rows=1 loops=1)
        Filter: ((id = 100) AND (household_id = 10))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.009..0.009 rows=1 loops=1)
        Filter: (category_id = 100)
        Rows Removed by Filter: 99
        Buffers: shared hit=1
Planning Time: 0.061 ms
Execution Time: 0.032 ms
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
Sort  (cost=1945.35..1969.87 rows=9810 width=53) (actual time=7.062..7.561 rows=9918 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1121kB
  Buffers: shared hit=984 read=29
  ->  Bitmap Heap Scan on transactions  (cost=188.32..1294.94 rows=9810 width=53) (actual time=0.838..5.019 rows=9918 loops=1)
        Recheck Cond: (household_id = 1)
        Heap Blocks: exact=984
        Buffers: shared hit=984 read=29
        ->  Bitmap Index Scan on ix_transactions_household_id_id  (cost=0.00..185.87 rows=9810 width=0) (actual time=0.701..0.701 rows=9918 loops=1)
              Index Cond: (household_id = 1)
              Buffers: shared read=29
Planning:
  Buffers: shared hit=105 read=4 dirtied=1
Planning Time: 0.803 ms
Execution Time: 8.103 ms
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
Sort  (cost=1988.14..2013.69 rows=10223 width=53) (actual time=4.604..5.015 rows=10146 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1138kB
  Buffers: shared hit=985 read=29
  ->  Bitmap Heap Scan on transactions  (cost=195.52..1307.31 rows=10223 width=53) (actual time=0.961..3.162 rows=10146 loops=1)
        Recheck Cond: (household_id = 5)
        Heap Blocks: exact=984
        Buffers: shared hit=985 read=29
        ->  Bitmap Index Scan on ix_transactions_household_id_id  (cost=0.00..192.96 rows=10223 width=0) (actual time=0.852..0.853 rows=10146 loops=1)
              Index Cond: (household_id = 5)
              Buffers: shared hit=1 read=29
Planning Time: 0.058 ms
Execution Time: 5.438 ms
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
Sort  (cost=1930.10..1954.33 rows=9690 width=53) (actual time=2.433..2.761 rows=9836 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1115kB
  Buffers: shared hit=985 read=28
  ->  Bitmap Heap Scan on transactions  (cost=183.39..1288.52 rows=9690 width=53) (actual time=0.378..1.524 rows=9836 loops=1)
        Recheck Cond: (household_id = 10)
        Heap Blocks: exact=984
        Buffers: shared hit=985 read=28
        ->  Bitmap Index Scan on ix_transactions_household_id_id  (cost=0.00..180.97 rows=9690 width=0) (actual time=0.314..0.314 rows=9836 loops=1)
              Index Cond: (household_id = 10)
              Buffers: shared hit=1 read=28
Planning Time: 0.047 ms
Execution Time: 3.121 ms
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
Seq Scan on categories  (cost=0.03..2.52 rows=10 width=16) (actual time=0.003..0.007 rows=10 loops=1)
  Filter: (id = ANY ('{1,2,3,4,5,6,7,8,9,10}'::integer[]))
  Rows Removed by Filter: 90
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=3
Planning Time: 0.034 ms
Execution Time: 0.010 ms
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
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.008..0.008 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.004..0.005 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2
        ->  Index Scan using ix_transactions_household_id_id on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.004..0.004 rows=0 loops=1)
              Index Cond: ((household_id = 1) AND (id = 1))
              Buffers: shared hit=2
Planning:
  Buffers: shared hit=8
Planning Time: 0.075 ms
Execution Time: 0.019 ms
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
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.008..0.009 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.005..0.005 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2
        ->  Index Scan using ix_transactions_household_id_id on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.005..0.005 rows=0 loops=1)
              Index Cond: ((household_id = 5) AND (id = 50000))
              Buffers: shared hit=2
Planning:
  Buffers: shared hit=4
Planning Time: 0.062 ms
Execution Time: 0.024 ms
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
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.006..0.007 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.004..0.004 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2
        ->  Index Scan using ix_transactions_household_id_id on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.004..0.004 rows=0 loops=1)
              Index Cond: ((household_id = 10) AND (id = 100000))
              Buffers: shared hit=2
Planning:
  Buffers: shared hit=4
Planning Time: 0.047 ms
Execution Time: 0.014 ms
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
Aggregate  (cost=262.14..262.15 rows=1 width=8) (actual time=0.797..0.797 rows=1 loops=1)
  Buffers: shared hit=1 read=29
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..245.06 rows=6832 width=4) (actual time=0.030..0.506 rows=7013 loops=1)
        Index Cond: ((household_id = 1) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=1 read=29
Planning:
  Buffers: shared hit=2 read=1
Planning Time: 0.252 ms
Execution Time: 0.810 ms
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
Aggregate  (cost=272.62..272.63 rows=1 width=8) (actual time=1.068..1.069 rows=1 loops=1)
  Buffers: shared hit=3 read=28
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..254.82 rows=7120 width=4) (actual time=0.019..0.775 rows=7060 loops=1)
        Index Cond: ((household_id = 5) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=3 read=28
Planning Time: 0.016 ms
Execution Time: 1.083 ms
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
Aggregate  (cost=260.27..260.28 rows=1 width=8) (actual time=0.721..0.721 rows=1 loops=1)
  Buffers: shared hit=2 read=29
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..243.40 rows=6749 width=4) (actual time=0.023..0.491 rows=6920 loops=1)
        Index Cond: ((household_id = 10) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=2 read=29
Planning Time: 0.013 ms
Execution Time: 0.727 ms
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
Aggregate  (cost=115.42..115.43 rows=1 width=8) (actual time=0.248..0.248 rows=1 loops=1)
  Buffers: shared hit=4 read=11
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..107.98 rows=2978 width=4) (actual time=0.008..0.165 rows=2905 loops=1)
        Index Cond: ((household_id = 1) AND (type = 'income'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=4 read=11
Planning Time: 0.022 ms
Execution Time: 0.253 ms
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
Aggregate  (cost=122.24..122.25 rows=1 width=8) (actual time=0.336..0.336 rows=1 loops=1)
  Buffers: shared hit=4 read=12
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..114.48 rows=3103 width=4) (actual time=0.008..0.221 rows=3086 loops=1)
        Index Cond: ((household_id = 5) AND (type = 'income'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=4 read=12
Planning Time: 0.015 ms
Execution Time: 0.342 ms
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
Aggregate  (cost=114.59..114.60 rows=1 width=8) (actual time=0.286..0.286 rows=1 loops=1)
  Buffers: shared hit=4 read=11
  ->  Index Only Scan using ix_transactions_household_id_type_amount on transactions  (cost=0.42..107.24 rows=2941 width=4) (actual time=0.009..0.209 rows=2916 loops=1)
        Index Cond: ((household_id = 10) AND (type = 'income'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=4 read=11
Planning Time: 0.017 ms
Execution Time: 0.292 ms
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
HashAggregate  (cost=10.98..10.99 rows=1 width=24) (actual time=0.151..0.151 rows=1 loops=1)
  Group Key: budgets.goal
  Batches: 1  Memory Usage: 24kB
  Buffers: shared hit=3 read=5
  ->  Nested Loop Left Join  (cost=0.42..10.74 rows=48 width=20) (actual time=0.025..0.106 rows=708 loops=1)
        Buffers: shared hit=3 read=5
        ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.004..0.009 rows=1 loops=1)
              Buffers: shared hit=2
              ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.003..0.005 rows=1 loops=1)
                    Filter: ((id = 1) AND (household_id = 1))
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
              ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.001..0.004 rows=1 loops=1)
                    Filter: (category_id = 1)
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
        ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.50 rows=48 width=8) (actual time=0.020..0.057 rows=708 loops=1)
              Index Cond: ((household_id = 1) AND (category_id = 1) AND (type = 'expense'::transaction_type))
              Heap Fetches: 0
              Buffers: shared hit=1 read=5
Planning:
  Buffers: shared hit=3
Planning Time: 0.071 ms
Execution Time: 0.165 ms
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
HashAggregate  (cost=11.16..11.17 rows=1 width=24) (actual time=0.146..0.146 rows=1 loops=1)
  Group Key: budgets.goal
  Batches: 1  Memory Usage: 24kB
  Buffers: shared hit=4 read=5
  ->  Nested Loop Left Join  (cost=0.42..10.90 rows=53 width=20) (actual time=0.017..0.103 rows=712 loops=1)
        Buffers: shared hit=4 read=5
        ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.006..0.008 rows=1 loops=1)
              Buffers: shared hit=2
              ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.003..0.004 rows=1 loops=1)
                    Filter: ((id = 50) AND (household_id = 5))
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
              ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.002..0.003 rows=1 loops=1)
                    Filter: (category_id = 50)
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
        ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.61 rows=53 width=8) (actual time=0.010..0.057 rows=712 loops=1)
              Index Cond: ((household_id = 5) AND (category_id = 50) AND (type = 'expense'::transaction_type))
              Heap Fetches: 0
              Buffers: shared hit=2 read=5
Planning:
  Buffers: shared hit=3
Planning Time: 0.054 ms
Execution Time: 0.158 ms
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
HashAggregate  (cost=11.05..11.06 rows=1 width=24) (actual time=0.169..0.169 rows=1 loops=1)
  Group Key: budgets.goal
  Batches: 1  Memory Usage: 24kB
  Buffers: shared hit=4 read=5
  ->  Nested Loop Left Join  (cost=0.42..10.80 rows=50 width=20) (actual time=0.029..0.123 rows=761 loops=1)
        Buffers: shared hit=4 read=5
        ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.007..0.007 rows=1 loops=1)
              Buffers: shared hit=2
              ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.004..0.004 rows=1 loops=1)
                    Filter: ((id = 100) AND (household_id = 10))
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
              ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.003..0.003 rows=1 loops=1)
                    Filter: (category_id = 100)
                    Rows Removed by Filter: 99
                    Buffers: shared hit=1
        ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.54 rows=50 width=8) (actual time=0.021..0.075 rows=761 loops=1)
              Index Cond: ((household_id = 10) AND (category_id = 100) AND (type = 'expense'::transaction_type))
              Heap Fetches: 0
              Buffers: shared hit=2 read=5
Planning:
  Buffers: shared hit=3
Planning Time: 0.043 ms
Execution Time: 0.179 ms
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
GroupAggregate  (cost=16.24..109.66 rows=683 width=24) (actual time=0.369..3.288 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=35 read=24
  ->  Incremental Sort  (cost=16.24..97.71 rows=683 width=20) (actual time=0.169..2.664 rows=7013 loops=1)
        Sort Key: categories.id, budgets.goal
        Presorted Key: categories.id
        Full-sort Groups: 10  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        Pre-sorted Groups: 10  Sort Method: quicksort  Average Memory: 58kB  Peak Memory: 58kB
        Buffers: shared hit=35 read=24
        ->  Nested Loop Left Join  (cost=8.16..68.16 rows=683 width=20) (actual time=0.034..1.507 rows=7013 loops=1)
              Buffers: shared hit=35 read=24
              ->  Merge Join  (cost=7.74..8.39 rows=10 width=16) (actual time=0.024..0.031 rows=10 loops=1)
                    Merge Cond: (categories.id = budgets.category_id)
                    Buffers: shared hit=2
                    ->  Sort  (cost=2.42..2.44 rows=10 width=12) (actual time=0.009..0.011 rows=10 loops=1)
                          Sort Key: categories.id
                          Sort Method: quicksort  Memory: 25kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.002..0.004 rows=10 loops=1)
                                Filter: (household_id = 1)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
                    ->  Sort  (cost=5.32..5.57 rows=100 width=8) (actual time=0.013..0.015 rows=10 loops=1)
                          Sort Key: budgets.category_id
                          Sort Method: quicksort  Memory: 28kB
                          Buffers: shared hit=1
                          ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.001..0.005 rows=100 loops=1)
                                Buffers: shared hit=1
              ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.50 rows=48 width=8) (actual time=0.006..0.082 rows=701 loops=10)
                    Index Cond: ((household_id = 1) AND (category_id = categories.id) AND (type = 'expense'::transaction_type))
                    Heap Fetches: 0
                    Buffers: shared hit=33 read=24
Planning:
  Buffers: shared hit=15
Planning Time: 0.103 ms
Execution Time: 3.316 ms
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
GroupAggregate  (cost=16.41..112.28 rows=712 width=24) (actual time=0.343..3.570 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=36 read=24
  ->  Incremental Sort  (cost=16.41..99.82 rows=712 width=20) (actual time=0.164..2.886 rows=7060 loops=1)
        Sort Key: categories.id, budgets.goal
        Presorted Key: categories.id
        Full-sort Groups: 10  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        Pre-sorted Groups: 10  Sort Method: quicksort  Average Memory: 58kB  Peak Memory: 58kB
        Buffers: shared hit=36 read=24
        ->  Nested Loop Left Join  (cost=8.16..68.81 rows=712 width=20) (actual time=0.030..1.609 rows=7060 loops=1)
              Buffers: shared hit=36 read=24
              ->  Merge Join  (cost=7.74..8.39 rows=10 width=16) (actual time=0.021..0.027 rows=10 loops=1)
                    Merge Cond: (categories.id = budgets.category_id)
                    Buffers: shared hit=2
                    ->  Sort  (cost=2.42..2.44 rows=10 width=12) (actual time=0.007..0.008 rows=10 loops=1)
                          Sort Key: categories.id
                          Sort Method: quicksort  Memory: 25kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.003..0.004 rows=10 loops=1)
                                Filter: (household_id = 5)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
                    ->  Sort  (cost=5.32..5.57 rows=100 width=8) (actual time=0.011..0.013 rows=50 loops=1)
                          Sort Key: budgets.category_id
                          Sort Method: quicksort  Memory: 28kB
                          Buffers: shared hit=1
                          ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.001..0.005 rows=100 loops=1)
                                Buffers: shared hit=1
              ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.54 rows=50 width=8) (actual time=0.005..0.087 rows=706 loops=10)
                    Index Cond: ((household_id = 5) AND (category_id = categories.id) AND (type = 'expense'::transaction_type))
                    Heap Fetches: 0
                    Buffers: shared hit=34 read=24
Planning:
  Buffers: shared hit=15
Planning Time: 0.090 ms
Execution Time: 3.608 ms
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
GroupAggregate  (cost=16.17..108.80 rows=675 width=24) (actual time=0.388..1.904 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=36 read=24
  ->  Incremental Sort  (cost=16.17..96.98 rows=675 width=20) (actual time=0.197..1.586 rows=6920 loops=1)
        Sort Key: categories.id, budgets.goal
        Presorted Key: categories.id
        Full-sort Groups: 10  Sort Method: quicksort  Average Memory: 28kB  Peak Memory: 28kB
        Pre-sorted Groups: 10  Sort Method: quicksort  Average Memory: 58kB  Peak Memory: 58kB
        Buffers: shared hit=36 read=24
        ->  Nested Loop Left Join  (cost=8.16..67.84 rows=675 width=20) (actual time=0.043..0.903 rows=6920 loops=1)
              Buffers: shared hit=36 read=24
              ->  Merge Join  (cost=7.74..8.39 rows=10 width=16) (actual time=0.029..0.034 rows=10 loops=1)
                    Merge Cond: (categories.id = budgets.category_id)
                    Buffers: shared hit=2
                    ->  Sort  (cost=2.42..2.44 rows=10 width=12) (actual time=0.006..0.007 rows=10 loops=1)
                          Sort Key: categories.id
                          Sort Method: quicksort  Memory: 25kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.003..0.004 rows=10 loops=1)
                                Filter: (household_id = 10)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
                    ->  Sort  (cost=5.32..5.57 rows=100 width=8) (actual time=0.011..0.015 rows=100 loops=1)
                          Sort Key: budgets.category_id
                          Sort Method: quicksort  Memory: 28kB
                          Buffers: shared hit=1
                          ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.001..0.005 rows=100 loops=1)
                                Buffers: shared hit=1
              ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.47 rows=47 width=8) (actual time=0.005..0.051 rows=692 loops=10)
                    Index Cond: ((household_id = 10) AND (category_id = categories.id) AND (type = 'expense'::transaction_type))
                    Heap Fetches: 0
                    Buffers: shared hit=34 read=24
Planning:
  Buffers: shared hit=15
Planning Time: 0.089 ms
Execution Time: 1.924 ms
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
Aggregate  (cost=5.62..5.63 rows=1 width=8) (actual time=0.067..0.067 rows=1 loops=1)
  Buffers: shared hit=6
  ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.50 rows=48 width=4) (actual time=0.008..0.045 rows=708 loops=1)
        Index Cond: ((household_id = 1) AND (category_id = 1) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=6
Planning Time: 0.018 ms
Execution Time: 0.072 ms
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
Aggregate  (cost=5.74..5.75 rows=1 width=8) (actual time=0.077..0.078 rows=1 loops=1)
  Buffers: shared hit=7
  ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.61 rows=53 width=4) (actual time=0.005..0.049 rows=712 loops=1)
        Index Cond: ((household_id = 5) AND (category_id = 50) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=7
Planning Time: 0.021 ms
Execution Time: 0.085 ms
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
Aggregate  (cost=5.67..5.68 rows=1 width=8) (actual time=0.075..0.075 rows=1 loops=1)
  Buffers: shared hit=7
  ->  Index Only Scan using ix_transactions_household_id_category_id_type_amount on transactions  (cost=0.42..5.54 rows=50 width=4) (actual time=0.008..0.051 rows=761 loops=1)
        Index Cond: ((household_id = 10) AND (category_id = 100) AND (type = 'expense'::transaction_type))
        Heap Fetches: 0
        Buffers: shared hit=7
Planning Time: 0.015 ms
Execution Time: 0.081 ms
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
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.103..0.106 rows=1 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=1 read=1
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.003..0.005 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.094..0.094 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared read=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.085..0.087 rows=1 loops=1)
              Filter: (user_id = 1)
              Rows Removed by Filter: 19
              Buffers: shared read=1
Planning:
  Buffers: shared hit=51 read=4
Planning Time: 1.000 ms
Execution Time: 0.134 ms
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
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.008..0.009 rows=1 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=2
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.001..0.002 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.004..0.004 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.001..0.002 rows=1 loops=1)
              Filter: (user_id = 10)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.041 ms
Execution Time: 0.018 ms
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
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.008..0.008 rows=0 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=2
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.001..0.001 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.004..0.004 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=1)
              Filter: (user_id = 20)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.036 ms
Execution Time: 0.016 ms
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
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.002..0.002 rows=1 loops=1)
  Filter: ((user_id = 1) AND (household_id = 1))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=3
Planning Time: 0.021 ms
Execution Time: 0.013 ms
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
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.002..0.002 rows=1 loops=1)
  Filter: ((user_id = 10) AND (household_id = 5))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning Time: 0.009 ms
Execution Time: 0.004 ms
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
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.002..0.002 rows=1 loops=1)
  Filter: ((user_id = 20) AND (household_id = 10))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning Time: 0.008 ms
Execution Time: 0.003 ms
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
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.002..0.005 rows=1 loops=1)
  Filter: (category_id = 1)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.008 ms
Execution Time: 0.006 ms
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
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.003..0.004 rows=1 loops=1)
  Filter: (category_id = 50)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.007 ms
Execution Time: 0.005 ms
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
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.004..0.004 rows=1 loops=1)
  Filter: (category_id = 100)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.006 ms
Execution Time: 0.005 ms
```
