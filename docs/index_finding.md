## Query: get_all_transactions

### Query Shape
- **Table:** transactions
- **WHERE:** household_id = ?
- **Eager load:** selectinload(Transaction.category) — دو کوئری جدا
- **ORDER BY:** id ASC
- **Called by:** GET /transactions

### Selectivity Estimate
- household_id: متوسط. هر خانوار ~۱۰٪ جدول (~۱۰,۰۰۰ ردیف از ۱۰۰,۰۰۰).
- نکته: مقدار selectivity در اینجا خیلی مهم نیست، چون ایندکس `(household_id, id)` حتی اگه `household_id` selectivity پایینی داشته باشه، **Sort رو حذف می‌کنه** که خودش بزرگ‌ترین سودمه.

### Existing Indexes on Table
- `pk_transactions` → `(id)`

### Applicable Indexes (leftmost prefix)
- `pk_transactions (id)` → ❌ قابل استفاده نیست، چون `id` در WHERE نیست.
- هیچ ایندکس دیگه‌ای وجود ندارد.

### Candidate Index
- `(household_id, id)` — نه فقط `(household_id)`، چون `ORDER BY id` داریم و ایندکس مرکب Sort رو حذف می‌کنه.

### EXPLAIN Baseline (before index)
[پلن‌ها]

### Verdict
- **نیاز به ایندکس:** بله
- **ایندکس پیشنهادی:** `(household_id, id)`
- **دلیل:** Seq Scan کل جدول + Sort روی ۱۰,۰۰۰ ردیف. با ایندکس، هم WHERE بهینه می‌شه، هم Sort حذف می‌شه. انتظار: کاهش Buffer از ۹۸۴ به چند صفحه، حذف Sort، کاهش Execution Time از ~۵-۱۰ms به زیر ۱ms.




## Query: get_total_amount_by_type

### Query Shape
- **Table:** transactions
- **WHERE:** type = ?, household_id = ?
- **Aggregate:** SUM(amount)
- **Called by:** compute endpoint (get_financial_summary)

### Selectivity Estimate
- household_id: متوسط (~۱۰٪ جدول، چون ۱۰ خانوار داریم). **selective.**
- type: cardinality پایین (۲ مقدار). **غیر selective**، هر مقدار ~۵۰-۷۰٪ جدول.
- ترکیب: `WHERE household_id = ? AND type = ?` → ~۷٪ جدول (expense) یا ~۳٪ (income).

### Existing Indexes on Table
- `pk_transactions` → `(id)` از PK
- `household_id` → FK، **بدون ایندکس**
- `type` → **بدون ایندکس**
- `category_id` → FK، **بدون ایندکس**

### Applicable Indexes (leftmost prefix)
- `pk_transactions (id)` → ❌ `id` در WHERE نیست
- هیچ ایندکس قابل استفاده‌ای وجود ندارد.

### Candidate Index
- `(household_id, type, amount)`
  - `household_id` اول: selective، در WHERE.
  - `type` دوم: در WHERE.
  - `amount` آخر: برای `Index Only Scan` روی `SUM` (در WHERE نیست، فقط در SELECT).

### EXPLAIN Baseline (before index)
[پلن‌ها]

### Verdict
- **نیاز به ایندکس:** بله
- **ایندکس پیشنهادی:** `(household_id, type, amount)`
- **دلیل:** `Seq Scan` روی کل جدول + `Aggregate`. برای expense، ~۹۳,۰۰۰ ردیف دور ریخته می‌شه؛ برای income، ~۹۷,۰۰۰ ردیف. ۹۸۴ buffer read. با ایندکس `(household_id, type, amount)` و `Index Only Scan`، انتظار: buffer read از ۹۸۴ به زیر ۱۰، execution time از ~۴ms به زیر ۱ms.
- **نکته:** کوئری income از ایندکس سود بیشتری می‌بره، چون selectivity بالاتری داره (~۳٪ vs ~۷٪).


## Query: get_category_balance

### Query Shape
- **Tables:** categories, budgets, transactions
- **JOINs:**
  - `JOIN budgets ON categories.id = budgets.category_id`
  - `LEFT JOIN transactions ON categories.id = transactions.category_id
       AND transactions.type = 'expense'
       AND transactions.household_id = ?`
- **WHERE:** categories.id = ?, categories.household_id = ?
- **GROUP BY:** categories.id, categories.name, budgets.goal
- **Called by:** GET /compute/{category_id}

### Selectivity Estimate
- categories.id: بالا (PK، ~۱٪).
- categories.household_id: متوسط (~۱۰٪).
- transactions.category_id: بالا (~۱٪).
- transactions.household_id: متوسط (~۱۰٪).
- transactions.type: پایین (cardinality ۲، ~۷۰٪ برای expense).
- **ترکیب هر سه با AND:** ~۰.۷٪ → **خیلی selective**.
- **نکته:** selectivity نهایی خوبه، ولی چون ایندکس مناسب نداریم، planner مجبوره Seq Scan بزنه.

### Existing Indexes on Table
**categories:**
- `pk_categories (id)`
- `uq_categories_name_household_id (name, household_id)`

**budgets:**
- `pk_budgets (id)`
- `uq_budgets_category_id (category_id)`

**transactions:**
- `pk_transactions (id)`
- `category_id` → FK، **بدون ایندکس**
- `household_id` → FK، **بدون ایندکس**
- `type` → **بدون ایندکس**

### Applicable Indexes (leftmost prefix)
- `pk_categories (id)` → قابل استفاده ولی planner انتخاب نکرد (جدول کوچیک).
- `uq_budgets_category_id` → قابل استفاده ولی planner انتخاب نکرد (جدول کوچیک).
- برای `transactions`: **هیچ ایندکس قابل استفاده‌ای نیست**.

### Candidate Index
- `transactions (category_id, household_id, type, amount)`
  - `category_id` اول: selective‌تر.
  - `household_id` دوم: تأیید.
  - `type` سوم: تأیید.
  - `amount` آخر: برای `Index Only Scan` روی `SUM(amount)`.

### EXPLAIN Baseline (before index)
[پلن‌ها]

### Verdict
- **نیاز به ایندکس:** بله
- **ایندکس پیشنهادی:** `transactions (category_id, household_id, type, amount)`
- **دلیل:** Seq Scan روی کل transactions (۹۸۴ buffer). `Rows Removed by Filter: 99,292` = ۹۹.۳٪ کار بیهوده. با ایندکس، انتظار: buffer از ۹۸۴ به چند صفحه، execution time از ~۴ms به زیر ۰.۵ms.
- **نکته:** تخمین planner اشتباهه (`rows=53` تخمین vs `rows=708` واقعی). ایندکس آمار بهتر هم می‌ده.



## Query: get_all_categories_balance

### Query Shape
- **Tables:** categories, budgets, transactions
- **JOINs:**
  - `JOIN budgets ON categories.id = budgets.category_id`
  - `LEFT JOIN transactions ON categories.id = transactions.category_id
       AND transactions.household_id = ?
       AND transactions.type = 'expense'`
- **WHERE:** categories.household_id = ?
- **GROUP BY:** categories.id, categories.name, budgets.goal
- **ORDER BY:** categories.id ASC
- **Called by:** GET /compute/categories

### Selectivity Estimate
- categories.household_id: متوسط (~۱۰٪، ۱۰ از ۱۰۰).
- transactions.category_id: بالا (~۱٪).
- transactions.household_id: متوسط (~۱۰٪).
- transactions.type: پایین (~۷۰٪ برای expense).
- **ترکیب سه شرط LEFT JOIN:** ~۰.۷٪.
- **نکته:** این کوئری همه‌ی categoryهای یه خانوار رو برمی‌گردونه (۱۰ ردیف)، نه یکی.

### Existing Indexes on Table
**categories:**
- `pk_categories (id)`
- `uq_categories_name_household_id (name, household_id)`

**budgets:**
- `pk_budgets (id)`
- `uq_budgets_category_id (category_id)`

**transactions:**
- `pk_transactions (id)`
- `category_id` → FK، **بدون ایندکس**
- `household_id` → FK، **بدون ایندکس**
- `type` → **بدون ایندکس**

### Applicable Indexes (leftmost prefix)
- `pk_categories (id)` → ❌ قابل استفاده نیست (`categories.id` در WHERE نیست).
- `uq_categories_name_household_id (name, household_id)` → ❌ قابل استفاده نیست (`name` در WHERE نیست).
- `uq_budgets_category_id (category_id)` → ✅ قابل استفاده (در JOIN ON)، ولی planner Seq Scan انتخاب کرد (جدول کوچیک).
- برای `transactions`: **هیچ ایندکس قابل استفاده‌ای نیست**.

### Candidate Index
- `transactions (category_id, household_id, type, amount)`
  - `category_id` اول: selective‌تر.
  - `household_id` دوم: تأیید.
  - `type` سوم: تأیید.
  - `amount` آخر: برای `Index Only Scan` روی `SUM(amount)`.
- **نکته:** `categories (household_id, id)` هم می‌تونه Sort رو حذف کنه، ولی چون جدول ۱۰۰ ردیفه، تأثیرش ناچیزه → توصیه نمی‌شه.

### EXPLAIN Baseline (before index)
[پلن‌ها]

### Verdict
- **نیاز به ایندکس:** بله (فقط برای transactions)
- **ایندکس پیشنهادی:** `transactions (category_id, household_id, type, amount)`
- **دلیل:** Seq Scan روی کل transactions (۹۸۴ buffer)، ~۹۳,۰۰۰ ردیف دور ریخته می‌شه. با ایندکس، انتظار: buffer از ۹۸۴ به چند صفحه، execution time از ~۵-۶ms به زیر ۱ms.
- **نکته‌ی ظریف:** `GROUP BY` روی `categories.id` + `ORDER BY categories.id` → Sort روی ۱۰ ردیف. چون categories کوچیکه، Sort هزینه‌ی ناچیزی داره. ایندکس جدید روی categories لازم نیست.


## Query: get_category_total_spent
### Query Shape
- **Tables:** transactions
- **JOINs:** —
- **WHERE:** category_id = ?, household_id = ?, type = ?
- **Aggregate:** SUM(amount)
- **Called by:** TransactionService.add_transaction, TransactionService.edit_transaction
### Selectivity Estimate
- transactions.category_id: بالا (~۱٪). selective.
- transactions.household_id: متوسط (~۱۰٪).
- transactions.type: پایین (~۷۰٪ برای expense). غیر selective.
- **ترکیب سه شرط:** ~۰.۷٪ → خیلی selective.
- **نکته:** selectivity نهایی خوبه، ولی چون ایندکس مناسب نداریم، planner مجبوره Seq Scan بزنه.
### Existing Indexes on Table
- `pk_transactions (id)`
- `category_id` → FK، **بدون ایندکس**
- `household_id` → FK، **بدون ایندکس**
- `type` → **بدون ایندکس**
### Applicable Indexes (leftmost prefix)
- `pk_transactions (id)` → ❌ قابل استفاده نیست (`id` در WHERE نیست).
- برای `transactions`: **هیچ ایندکس قابل استفاده‌ای نیست**.
### Candidate Index
- `transactions (category_id, household_id, type, amount)`
  - `category_id` اول: selective‌تر.
  - `household_id` دوم: تأیید.
  - `type` سوم: تأیید.
  - `amount` آخر: برای `Index Only Scan` روی `SUM(amount)`.
### EXPLAIN Baseline (before index)

### Verdict

- **نیاز به ایندکس:** بله
    
- **ایندکس پیشنهادی:** `transactions (category_id, household_id, type, amount)`
    
- **دلیل:** Seq Scan روی کل transactions (۹۸۴ buffer). `Rows Removed by Filter: 99,292` = ۹۹.۳٪ کار بیهوده. با ایندکس `(category_id, household_id, type, amount)` و `Index Only Scan` (چون تمام ستون‌های WHERE + SELECT داخل ایندکسن)، انتظار: buffer از ۹۸۴ به زیر ۵، execution time از ~۳.۵ms به زیر ۰.۲ms.
    
- **نکته:** تخمین planner اشتباهه (`rows=53` تخمین vs `rows=708` واقعی). ایندکس مرکب، هم پلن رو بهتر می‌کنه و هم آمار دقیق‌تری برای planner فراهم می‌کنه.
