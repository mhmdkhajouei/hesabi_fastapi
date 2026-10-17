# EXPLAIN Baseline

Generated: 2026-10-15T15:54:03.831571+00:00

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
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.047..0.048 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=5
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.019..0.028 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.001..0.004 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.010..0.010 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.003..0.006 rows=10 loops=1)
                    Filter: (household_id = 1)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=137 read=27
Planning Time: 2.648 ms
Execution Time: 0.685 ms
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
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.024..0.024 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=2
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.015..0.021 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.001..0.004 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.006..0.007 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.003..0.004 rows=10 loops=1)
                    Filter: (household_id = 5)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.063 ms
Execution Time: 0.033 ms
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
Sort  (cost=4.81..4.84 rows=10 width=32) (actual time=0.028..0.028 rows=10 loops=1)
  Sort Key: categories.id
  Sort Method: quicksort  Memory: 25kB
  Buffers: shared hit=2
  ->  Hash Right Join  (cost=2.38..4.65 rows=10 width=32) (actual time=0.022..0.024 rows=10 loops=1)
        Hash Cond: (budgets_1.category_id = categories.id)
        Buffers: shared hit=2
        ->  Seq Scan on budgets budgets_1  (cost=0.00..2.00 rows=100 width=16) (actual time=0.001..0.004 rows=100 loops=1)
              Buffers: shared hit=1
        ->  Hash  (cost=2.25..2.25 rows=10 width=16) (actual time=0.009..0.009 rows=10 loops=1)
              Buckets: 1024  Batches: 1  Memory Usage: 9kB
              Buffers: shared hit=1
              ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=16) (actual time=0.004..0.005 rows=10 loops=1)
                    Filter: (household_id = 10)
                    Rows Removed by Filter: 90
                    Buffers: shared hit=1
Planning:
  Buffers: shared hit=8
Planning Time: 0.071 ms
Execution Time: 0.038 ms
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
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.004..0.006 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.002..0.004 rows=1 loops=1)
        Filter: ((id = 1) AND (household_id = 1))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.001..0.001 rows=1 loops=1)
        Filter: (category_id = 1)
        Buffers: shared hit=1
Planning Time: 0.024 ms
Execution Time: 0.009 ms
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
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.005..0.007 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.003..0.004 rows=1 loops=1)
        Filter: ((id = 50) AND (household_id = 5))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.002..0.002 rows=1 loops=1)
        Filter: (category_id = 50)
        Rows Removed by Filter: 49
        Buffers: shared hit=1
Planning Time: 0.025 ms
Execution Time: 0.010 ms
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
Nested Loop Left Join  (cost=0.00..4.76 rows=1 width=32) (actual time=0.007..0.007 rows=1 loops=1)
  Buffers: shared hit=2
  ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=16) (actual time=0.004..0.004 rows=1 loops=1)
        Filter: ((id = 100) AND (household_id = 10))
        Rows Removed by Filter: 99
        Buffers: shared hit=1
  ->  Seq Scan on budgets budgets_1  (cost=0.00..2.25 rows=1 width=16) (actual time=0.003..0.003 rows=1 loops=1)
        Filter: (category_id = 100)
        Rows Removed by Filter: 99
        Buffers: shared hit=1
Planning Time: 0.019 ms
Execution Time: 0.010 ms
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
Sort  (cost=2905.75..2931.00 rows=10100 width=53) (actual time=9.641..9.936 rows=9918 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1121kB
  Buffers: shared read=984
  ->  Seq Scan on transactions  (cost=0.00..2234.00 rows=10100 width=53) (actual time=0.149..8.750 rows=9918 loops=1)
        Filter: (household_id = 1)
        Rows Removed by Filter: 90082
        Buffers: shared read=984
Planning:
  Buffers: shared hit=42 read=1
Planning Time: 0.293 ms
Execution Time: 10.160 ms
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
Sort  (cost=2909.96..2935.35 rows=10157 width=53) (actual time=4.571..4.787 rows=10146 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1138kB
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2234.00 rows=10157 width=53) (actual time=0.005..3.895 rows=10146 loops=1)
        Filter: (household_id = 5)
        Rows Removed by Filter: 89854
        Buffers: shared hit=984
Planning Time: 0.051 ms
Execution Time: 4.999 ms
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
Sort  (cost=2903.54..2928.72 rows=10070 width=53) (actual time=4.430..4.636 rows=9836 loops=1)
  Sort Key: id
  Sort Method: quicksort  Memory: 1115kB
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2234.00 rows=10070 width=53) (actual time=0.002..3.801 rows=9836 loops=1)
        Filter: (household_id = 10)
        Rows Removed by Filter: 90164
        Buffers: shared hit=984
Planning Time: 0.020 ms
Execution Time: 4.840 ms
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
Seq Scan on categories  (cost=0.03..2.52 rows=10 width=16) (actual time=0.003..0.006 rows=10 loops=1)
  Filter: (id = ANY ('{1,2,3,4,5,6,7,8,9,10}'::integer[]))
  Rows Removed by Filter: 90
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=2 read=1
Planning Time: 0.084 ms
Execution Time: 0.009 ms
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
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.213..0.214 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=1 read=2
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.209..0.209 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=1 read=2
        ->  Index Scan using pk_transactions on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.209..0.209 rows=0 loops=1)
              Index Cond: (id = 1)
              Filter: (household_id = 1)
              Rows Removed by Filter: 1
              Buffers: shared hit=1 read=2
Planning:
  Buffers: shared hit=8
Planning Time: 0.088 ms
Execution Time: 0.228 ms
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
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.168..0.168 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2 read=1
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.165..0.165 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2 read=1
        ->  Index Scan using pk_transactions on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.165..0.165 rows=0 loops=1)
              Index Cond: (id = 50000)
              Filter: (household_id = 5)
              Rows Removed by Filter: 1
              Buffers: shared hit=2 read=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.037 ms
Execution Time: 0.176 ms
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
Hash Right Join  (cost=8.32..10.60 rows=1 width=69) (actual time=0.057..0.058 rows=0 loops=1)
  Hash Cond: (categories_1.id = transactions.category_id)
  Buffers: shared hit=2 read=1
  ->  Seq Scan on categories categories_1  (cost=0.00..2.00 rows=100 width=16) (never executed)
  ->  Hash  (cost=8.31..8.31 rows=1 width=53) (actual time=0.054..0.054 rows=0 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 8kB
        Buffers: shared hit=2 read=1
        ->  Index Scan using pk_transactions on transactions  (cost=0.29..8.31 rows=1 width=53) (actual time=0.054..0.054 rows=0 loops=1)
              Index Cond: (id = 100000)
              Filter: (household_id = 10)
              Rows Removed by Filter: 1
              Buffers: shared hit=2 read=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.046 ms
Execution Time: 0.066 ms
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
Aggregate  (cost=2501.67..2501.68 rows=1 width=8) (actual time=4.137..4.137 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=7069 width=4) (actual time=0.003..3.942 rows=7013 loops=1)
        Filter: ((type = 'expense'::transaction_type) AND (household_id = 1))
        Rows Removed by Filter: 92987
        Buffers: shared hit=984
Planning:
  Buffers: shared hit=4 read=2
Planning Time: 0.253 ms
Execution Time: 4.148 ms
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
Aggregate  (cost=2501.77..2501.78 rows=1 width=8) (actual time=3.911..3.911 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=7109 width=4) (actual time=0.003..3.719 rows=7060 loops=1)
        Filter: ((type = 'expense'::transaction_type) AND (household_id = 5))
        Rows Removed by Filter: 92940
        Buffers: shared hit=984
Planning Time: 0.025 ms
Execution Time: 3.917 ms
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
Aggregate  (cost=2501.62..2501.63 rows=1 width=8) (actual time=3.817..3.817 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=7048 width=4) (actual time=0.002..3.632 rows=6920 loops=1)
        Filter: ((type = 'expense'::transaction_type) AND (household_id = 10))
        Rows Removed by Filter: 93080
        Buffers: shared hit=984
Planning Time: 0.017 ms
Execution Time: 3.821 ms
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
Aggregate  (cost=2491.58..2491.59 rows=1 width=8) (actual time=3.474..3.474 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=3031 width=4) (actual time=0.002..3.396 rows=2905 loops=1)
        Filter: ((type = 'income'::transaction_type) AND (household_id = 1))
        Rows Removed by Filter: 97095
        Buffers: shared hit=984
Planning Time: 0.016 ms
Execution Time: 3.478 ms
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
Aggregate  (cost=2491.62..2491.63 rows=1 width=8) (actual time=3.694..3.694 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=3048 width=4) (actual time=0.002..3.613 rows=3086 loops=1)
        Filter: ((type = 'income'::transaction_type) AND (household_id = 5))
        Rows Removed by Filter: 96914
        Buffers: shared hit=984
Planning Time: 0.020 ms
Execution Time: 3.699 ms
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
Aggregate  (cost=2491.55..2491.57 rows=1 width=8) (actual time=3.574..3.574 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=3022 width=4) (actual time=0.002..3.495 rows=2916 loops=1)
        Filter: ((type = 'income'::transaction_type) AND (household_id = 10))
        Rows Removed by Filter: 97084
        Buffers: shared hit=984
Planning Time: 0.017 ms
Execution Time: 3.578 ms
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
GroupAggregate  (cost=2740.81..2741.22 rows=1 width=24) (actual time=3.689..3.690 rows=1 loops=1)
  Group Key: budgets.goal
  Buffers: shared hit=986
  ->  Sort  (cost=2740.81..2740.94 rows=53 width=20) (actual time=3.643..3.660 rows=708 loops=1)
        Sort Key: budgets.goal
        Sort Method: quicksort  Memory: 58kB
        Buffers: shared hit=986
        ->  Nested Loop Left Join  (cost=0.00..2739.29 rows=53 width=20) (actual time=0.030..3.574 rows=708 loops=1)
              Buffers: shared hit=986
              ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.004..0.009 rows=1 loops=1)
                    Buffers: shared hit=2
                    ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.002..0.005 rows=1 loops=1)
                          Filter: ((id = 1) AND (household_id = 1))
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
                    ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.001..0.003 rows=1 loops=1)
                          Filter: (category_id = 1)
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
              ->  Seq Scan on transactions  (cost=0.00..2734.00 rows=53 width=8) (actual time=0.025..3.530 rows=708 loops=1)
                    Filter: ((type = 'expense'::transaction_type) AND (category_id = 1) AND (household_id = 1))
                    Rows Removed by Filter: 99292
                    Buffers: shared hit=984
Planning:
  Buffers: shared hit=3
Planning Time: 0.069 ms
Execution Time: 3.710 ms
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
GroupAggregate  (cost=2740.76..2741.16 rows=1 width=24) (actual time=4.133..4.133 rows=1 loops=1)
  Group Key: budgets.goal
  Buffers: shared hit=986
  ->  Sort  (cost=2740.76..2740.89 rows=52 width=20) (actual time=4.086..4.102 rows=712 loops=1)
        Sort Key: budgets.goal
        Sort Method: quicksort  Memory: 58kB
        Buffers: shared hit=986
        ->  Nested Loop Left Join  (cost=0.00..2739.28 rows=52 width=20) (actual time=0.052..3.991 rows=712 loops=1)
              Buffers: shared hit=986
              ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.022..0.026 rows=1 loops=1)
                    Buffers: shared hit=2
                    ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.015..0.016 rows=1 loops=1)
                          Filter: ((id = 50) AND (household_id = 5))
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
                    ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.006..0.008 rows=1 loops=1)
                          Filter: (category_id = 50)
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
              ->  Seq Scan on transactions  (cost=0.00..2734.00 rows=52 width=8) (actual time=0.028..3.926 rows=712 loops=1)
                    Filter: ((type = 'expense'::transaction_type) AND (household_id = 5) AND (category_id = 50))
                    Rows Removed by Filter: 99288
                    Buffers: shared hit=984
Planning:
  Buffers: shared hit=3
Planning Time: 0.082 ms
Execution Time: 4.182 ms
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
GroupAggregate  (cost=2740.85..2741.27 rows=1 width=24) (actual time=3.758..3.759 rows=1 loops=1)
  Group Key: budgets.goal
  Buffers: shared hit=986
  ->  Sort  (cost=2740.85..2740.99 rows=54 width=20) (actual time=3.710..3.726 rows=761 loops=1)
        Sort Key: budgets.goal
        Sort Method: quicksort  Memory: 60kB
        Buffers: shared hit=986
        ->  Nested Loop Left Join  (cost=0.00..2739.30 rows=54 width=20) (actual time=0.015..3.655 rows=761 loops=1)
              Buffers: shared hit=986
              ->  Nested Loop  (cost=0.00..4.76 rows=1 width=16) (actual time=0.008..0.008 rows=1 loops=1)
                    Buffers: shared hit=2
                    ->  Seq Scan on categories  (cost=0.00..2.50 rows=1 width=12) (actual time=0.004..0.004 rows=1 loops=1)
                          Filter: ((id = 100) AND (household_id = 10))
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
                    ->  Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=8) (actual time=0.003..0.003 rows=1 loops=1)
                          Filter: (category_id = 100)
                          Rows Removed by Filter: 99
                          Buffers: shared hit=1
              ->  Seq Scan on transactions  (cost=0.00..2734.00 rows=54 width=8) (actual time=0.007..3.608 rows=761 loops=1)
                    Filter: ((type = 'expense'::transaction_type) AND (household_id = 10) AND (category_id = 100))
                    Rows Removed by Filter: 99239
                    Buffers: shared hit=984
Planning:
  Buffers: shared hit=3
Planning Time: 0.065 ms
Execution Time: 3.773 ms
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
GroupAggregate  (cost=2544.12..2558.26 rows=707 width=24) (actual time=5.327..5.742 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=986
  ->  Sort  (cost=2544.12..2545.89 rows=707 width=20) (actual time=5.278..5.449 rows=7013 loops=1)
        Sort Key: categories.id, budgets.goal
        Sort Method: quicksort  Memory: 527kB
        Buffers: shared hit=986
        ->  Hash Join  (cost=5.62..2510.66 rows=707 width=20) (actual time=0.041..4.645 rows=7013 loops=1)
              Hash Cond: (categories.id = budgets.category_id)
              Buffers: shared hit=986
              ->  Hash Right Join  (cost=2.38..2505.48 rows=707 width=16) (actual time=0.016..4.136 rows=7013 loops=1)
                    Hash Cond: (transactions.category_id = categories.id)
                    Buffers: shared hit=985
                    ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=7069 width=8) (actual time=0.001..3.633 rows=7013 loops=1)
                          Filter: ((household_id = 1) AND (type = 'expense'::transaction_type))
                          Rows Removed by Filter: 92987
                          Buffers: shared hit=984
                    ->  Hash  (cost=2.25..2.25 rows=10 width=12) (actual time=0.007..0.008 rows=10 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 9kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.001..0.003 rows=10 loops=1)
                                Filter: (household_id = 1)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
              ->  Hash  (cost=2.00..2.00 rows=100 width=8) (actual time=0.013..0.014 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 12kB
                    Buffers: shared hit=1
                    ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.002..0.005 rows=100 loops=1)
                          Buffers: shared hit=1
Planning:
  Buffers: shared hit=15
Planning Time: 0.109 ms
Execution Time: 5.770 ms
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
GroupAggregate  (cost=2544.47..2558.69 rows=711 width=24) (actual time=5.348..5.769 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=986
  ->  Sort  (cost=2544.47..2546.24 rows=711 width=20) (actual time=5.300..5.470 rows=7060 loops=1)
        Sort Key: categories.id, budgets.goal
        Sort Method: quicksort  Memory: 529kB
        Buffers: shared hit=986
        ->  Hash Join  (cost=5.62..2510.79 rows=711 width=20) (actual time=0.023..4.713 rows=7060 loops=1)
              Hash Cond: (categories.id = budgets.category_id)
              Buffers: shared hit=986
              ->  Hash Right Join  (cost=2.38..2505.59 rows=711 width=16) (actual time=0.009..4.181 rows=7060 loops=1)
                    Hash Cond: (transactions.category_id = categories.id)
                    Buffers: shared hit=985
                    ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=7109 width=8) (actual time=0.002..3.675 rows=7060 loops=1)
                          Filter: ((household_id = 5) AND (type = 'expense'::transaction_type))
                          Rows Removed by Filter: 92940
                          Buffers: shared hit=984
                    ->  Hash  (cost=2.25..2.25 rows=10 width=12) (actual time=0.005..0.005 rows=10 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 9kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.002..0.003 rows=10 loops=1)
                                Filter: (household_id = 5)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
              ->  Hash  (cost=2.00..2.00 rows=100 width=8) (actual time=0.012..0.012 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 12kB
                    Buffers: shared hit=1
                    ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.002..0.005 rows=100 loops=1)
                          Buffers: shared hit=1
Planning:
  Buffers: shared hit=15
Planning Time: 0.155 ms
Execution Time: 5.799 ms
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
GroupAggregate  (cost=2543.95..2558.05 rows=705 width=24) (actual time=5.294..5.691 rows=10 loops=1)
  Group Key: categories.id, budgets.goal
  Buffers: shared hit=986
  ->  Sort  (cost=2543.95..2545.71 rows=705 width=20) (actual time=5.246..5.406 rows=6920 loops=1)
        Sort Key: categories.id, budgets.goal
        Sort Method: quicksort  Memory: 522kB
        Buffers: shared hit=986
        ->  Hash Join  (cost=5.62..2510.60 rows=705 width=20) (actual time=0.022..4.663 rows=6920 loops=1)
              Hash Cond: (categories.id = budgets.category_id)
              Buffers: shared hit=986
              ->  Hash Right Join  (cost=2.38..2505.42 rows=705 width=16) (actual time=0.008..4.176 rows=6920 loops=1)
                    Hash Cond: (transactions.category_id = categories.id)
                    Buffers: shared hit=985
                    ->  Seq Scan on transactions  (cost=0.00..2484.00 rows=7048 width=8) (actual time=0.001..3.687 rows=6920 loops=1)
                          Filter: ((household_id = 10) AND (type = 'expense'::transaction_type))
                          Rows Removed by Filter: 93080
                          Buffers: shared hit=984
                    ->  Hash  (cost=2.25..2.25 rows=10 width=12) (actual time=0.005..0.005 rows=10 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 9kB
                          Buffers: shared hit=1
                          ->  Seq Scan on categories  (cost=0.00..2.25 rows=10 width=12) (actual time=0.002..0.003 rows=10 loops=1)
                                Filter: (household_id = 10)
                                Rows Removed by Filter: 90
                                Buffers: shared hit=1
              ->  Hash  (cost=2.00..2.00 rows=100 width=8) (actual time=0.011..0.011 rows=100 loops=1)
                    Buckets: 1024  Batches: 1  Memory Usage: 12kB
                    Buffers: shared hit=1
                    ->  Seq Scan on budgets  (cost=0.00..2.00 rows=100 width=8) (actual time=0.001..0.005 rows=100 loops=1)
                          Buffers: shared hit=1
Planning:
  Buffers: shared hit=15
Planning Time: 0.099 ms
Execution Time: 5.718 ms
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
Aggregate  (cost=2734.13..2734.14 rows=1 width=8) (actual time=3.542..3.542 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2734.00 rows=53 width=4) (actual time=0.024..3.515 rows=708 loops=1)
        Filter: ((category_id = 1) AND (household_id = 1) AND (type = 'expense'::transaction_type))
        Rows Removed by Filter: 99292
        Buffers: shared hit=984
Planning Time: 0.016 ms
Execution Time: 3.549 ms
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
Aggregate  (cost=2734.13..2734.14 rows=1 width=8) (actual time=3.301..3.301 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2734.00 rows=52 width=4) (actual time=0.009..3.277 rows=712 loops=1)
        Filter: ((category_id = 50) AND (household_id = 5) AND (type = 'expense'::transaction_type))
        Rows Removed by Filter: 99288
        Buffers: shared hit=984
Planning Time: 0.027 ms
Execution Time: 3.307 ms
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
Aggregate  (cost=2734.14..2734.15 rows=1 width=8) (actual time=3.358..3.358 rows=1 loops=1)
  Buffers: shared hit=984
  ->  Seq Scan on transactions  (cost=0.00..2734.00 rows=54 width=4) (actual time=0.007..3.332 rows=761 loops=1)
        Filter: ((category_id = 100) AND (household_id = 10) AND (type = 'expense'::transaction_type))
        Rows Removed by Filter: 99239
        Buffers: shared hit=984
Planning Time: 0.017 ms
Execution Time: 3.363 ms
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
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.050..0.052 rows=1 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=1 read=1
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.002..0.002 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.045..0.045 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared read=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.041..0.041 rows=1 loops=1)
              Filter: (user_id = 1)
              Rows Removed by Filter: 19
              Buffers: shared read=1
Planning:
  Buffers: shared hit=51 read=4
Planning Time: 0.817 ms
Execution Time: 0.063 ms
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
Hash Join  (cost=1.26..2.38 rows=1 width=4) (actual time=0.006..0.007 rows=1 loops=1)
  Hash Cond: (household.id = household_members.household_id)
  Buffers: shared hit=2
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.001..0.001 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.003..0.003 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=1)
              Filter: (user_id = 10)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.037 ms
Execution Time: 0.014 ms
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
  ->  Seq Scan on household  (cost=0.00..1.10 rows=5 width=4) (actual time=0.001..0.002 rows=5 loops=1)
        Filter: (is_personal IS TRUE)
        Rows Removed by Filter: 5
        Buffers: shared hit=1
  ->  Hash  (cost=1.25..1.25 rows=1 width=4) (actual time=0.003..0.003 rows=1 loops=1)
        Buckets: 1024  Batches: 1  Memory Usage: 9kB
        Buffers: shared hit=1
        ->  Seq Scan on household_members  (cost=0.00..1.25 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=1)
              Filter: (user_id = 20)
              Rows Removed by Filter: 19
              Buffers: shared hit=1
Planning:
  Buffers: shared hit=4
Planning Time: 0.040 ms
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
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.001..0.002 rows=1 loops=1)
  Filter: ((user_id = 1) AND (household_id = 1))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning:
  Buffers: shared hit=3
Planning Time: 0.015 ms
Execution Time: 0.010 ms
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
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.001..0.002 rows=1 loops=1)
  Filter: ((user_id = 10) AND (household_id = 5))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning Time: 0.007 ms
Execution Time: 0.003 ms
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
Seq Scan on household_members  (cost=0.00..1.30 rows=1 width=4) (actual time=0.001..0.002 rows=1 loops=1)
  Filter: ((user_id = 20) AND (household_id = 10))
  Rows Removed by Filter: 19
  Buffers: shared hit=1
Planning Time: 0.006 ms
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
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.002..0.004 rows=1 loops=1)
  Filter: (category_id = 1)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.009 ms
Execution Time: 0.005 ms
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
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.002..0.003 rows=1 loops=1)
  Filter: (category_id = 50)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.006 ms
Execution Time: 0.004 ms
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
Seq Scan on budgets  (cost=0.00..2.25 rows=1 width=16) (actual time=0.003..0.003 rows=1 loops=1)
  Filter: (category_id = 100)
  Rows Removed by Filter: 99
  Buffers: shared hit=1
Planning Time: 0.006 ms
Execution Time: 0.004 ms
```
