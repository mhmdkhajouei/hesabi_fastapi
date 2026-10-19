import asyncio
import random
from datetime import UTC, datetime, timedelta

from sqlalchemy import text

from app.db.database import async_db_session, engine

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RANDOM_SEED = 42

N_HOUSEHOLDS = 10
N_USERS_PER_HOUSEHOLD = 2
N_CATEGORIES_PER_HOUSEHOLD = 10
N_TRANSACTIONS_PER_HOUSEHOLD = 10_000

# Realistic distribution: 70% expense, 30% income
EXPENSE_RATIO = 0.70

# Amount buckets (IRR / TOMAN-scale values, similar to real usage)
AMOUNT_BUCKETS = [
    (0.80, 10_000, 500_000),  # 80% small
    (0.15, 500_000, 2_000_000),  # 15% medium
    (0.05, 2_000_000, 5_000_000),  # 5% large
]

# 24-month window for transaction dates
DATE_WINDOW_DAYS = 730

# Fake password hash (must be > 20 chars to satisfy CheckConstraint)
FAKE_PASSWORD_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=4$c2VlZF9vbmx5X25vdF9yZWFsX2hhc2g"
    "$ZmFrZV9mYWtlX2Zha2VfZmFrZV9mYWtlX2Zha2U"
)

CATEGORY_NAMES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Health",
    "Entertainment",
    "Education",
    "Clothing",
    "Savings",
    "Other",
]

# ---------------------------------------------------------------------------
# Truncate
# ---------------------------------------------------------------------------


async def truncate_all(session) -> None:
    await session.execute(
        text(
            """
            TRUNCATE TABLE
                transactions,
                budgets,
                categories,
                household_members,
                household,
                users
            RESTART IDENTITY CASCADE
            """
        )
    )
    await session.commit()
    print("[seed] truncated all tables")


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------


async def seed_households_and_users(session) -> None:
    household_rows = []
    for h in range(1, N_HOUSEHOLDS + 1):
        is_personal = h <= 5
        household_rows.append(
            {
                "id": h,
                "name": f"Household {h}",
                "is_personal": is_personal,
            }
        )

    user_rows = []
    for h in range(1, N_HOUSEHOLDS + 1):
        for u in range(N_USERS_PER_HOUSEHOLD):
            user_id = (h - 1) * N_USERS_PER_HOUSEHOLD + u + 1
            user_rows.append(
                {
                    "id": user_id,
                    "name": f"User {user_id}",
                    "email": f"user{user_id}@seed.local",
                    "password_hash": FAKE_PASSWORD_HASH,
                    "is_active": True,
                }
            )

    membership_rows = []
    for h in range(1, N_HOUSEHOLDS + 1):
        for u in range(N_USERS_PER_HOUSEHOLD):
            user_id = (h - 1) * N_USERS_PER_HOUSEHOLD + u + 1
            role = "OWNER" if u == 0 else "MEMBER"
            membership_rows.append(
                {
                    "user_id": user_id,
                    "household_id": h,
                    "role": role,
                }
            )

    await session.execute(
        text(
            """
            INSERT INTO household (id, name, is_personal)
            VALUES (:id, :name, :is_personal)
            """
        ),
        household_rows,
    )

    await session.execute(
        text(
            """
            INSERT INTO users (id, name, email, password_hash, is_active)
            VALUES (:id, :name, :email, :password_hash, :is_active)
            """
        ),
        user_rows,
    )

    await session.execute(
        text(
            """
            INSERT INTO household_members (user_id, household_id, role)
            VALUES (:user_id, :household_id, CAST(:role AS household_role_enum))
            """
        ),
        membership_rows,
    )

    await session.commit()
    print(
        f"[seed] inserted {len(household_rows)} households, "
        f"{len(user_rows)} users, {len(membership_rows)} memberships"
    )


async def seed_categories_and_budgets(session) -> None:
    category_rows = []
    budget_rows = []

    for h in range(1, N_HOUSEHOLDS + 1):
        for c in range(N_CATEGORIES_PER_HOUSEHOLD):
            category_id = (h - 1) * N_CATEGORIES_PER_HOUSEHOLD + c + 1
            category_rows.append(
                {
                    "id": category_id,
                    "name": CATEGORY_NAMES[c],
                    "household_id": h,
                }
            )
            budget_rows.append(
                {
                    "id": category_id,
                    "goal": random.randint(5_000_000, 20_000_000),
                    "currency": "TOMAN",
                    "category_id": category_id,
                }
            )

    await session.execute(
        text(
            """
            INSERT INTO categories (id, name, household_id)
            VALUES (:id, :name, :household_id)
            """
        ),
        category_rows,
    )

    await session.execute(
        text(
            """
            INSERT INTO budgets (id, goal, currency, category_id)
            VALUES (:id, :goal, CAST(:currency AS currency_type), :category_id)
            """
        ),
        budget_rows,
    )

    await session.commit()
    print(
        f"[seed] inserted {len(category_rows)} categories, {len(budget_rows)} budgets"
    )


async def seed_transactions(session) -> None:
    total = N_HOUSEHOLDS * N_TRANSACTIONS_PER_HOUSEHOLD
    now = datetime.now(UTC)

    rows = []
    for _ in range(total):
        household_id = random.randint(1, N_HOUSEHOLDS)

        is_expense = random.random() < EXPENSE_RATIO
        tx_type = "expense" if is_expense else "income"

        # Amount bucket selection
        r = random.random()
        cumulative = 0.0
        amount = 100_000  # fallback
        for prob, lo, hi in AMOUNT_BUCKETS:
            cumulative += prob
            if r <= cumulative:
                amount = random.randint(lo, hi)
                break

        # Date: uniform in the last DATE_WINDOW_DAYS
        days_ago = random.randint(0, DATE_WINDOW_DAYS)
        tx_date = now - timedelta(days=days_ago)

        # Category: expense gets a category from its own household; income gets NULL
        if is_expense:
            cat_index = random.randint(0, N_CATEGORIES_PER_HOUSEHOLD - 1)
            category_id = (
                (household_id - 1) * N_CATEGORIES_PER_HOUSEHOLD + cat_index + 1
            )
        else:
            category_id = None

        # created_by: one of the two members of the household
        member_offset = random.randint(0, N_USERS_PER_HOUSEHOLD - 1)
        created_by = (household_id - 1) * N_USERS_PER_HOUSEHOLD + member_offset + 1

        note = None if random.random() < 0.5 else "seed transaction"

        rows.append(
            {
                "amount": amount,
                "type": tx_type,
                "currency": "TOMAN",
                "date": tx_date,
                "note": note,
                "category_id": category_id,
                "household_id": household_id,
                "created_by": created_by,
            }
        )

    # Chunked insert to avoid one giant parameter list
    CHUNK = 5_000
    for i in range(0, len(rows), CHUNK):
        chunk = rows[i : i + CHUNK]
        await session.execute(
            text(
                """
                INSERT INTO transactions
                    (amount, type, currency, date, note,
                     category_id, household_id, created_by)
                VALUES
                    (:amount,
                     CAST(:type AS transaction_type),
                     CAST(:currency AS currency_type),
                     :date, :note, :category_id, :household_id, :created_by)
                """
            ),
            chunk,
        )

    await session.commit()
    print(f"[seed] inserted {len(rows)} transactions")


# ---------------------------------------------------------------------------
# Analyze
# ---------------------------------------------------------------------------


async def analyze_all(session) -> None:
    await session.execute(text("ANALYZE"))
    await session.commit()
    print("[seed] ran ANALYZE on all tables")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


async def print_summary(session) -> None:
    tables = [
        "household",
        "users",
        "household_members",
        "categories",
        "budgets",
        "transactions",
    ]
    print("\n[seed] row counts:")
    for tbl in tables:
        count = await session.scalar(text(f"SELECT COUNT(*) FROM {tbl}"))
        print(f"  {tbl:<20} {count:>8}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


async def main() -> None:
    random.seed(RANDOM_SEED)

    async with async_db_session() as session:
        await truncate_all(session)
        await seed_households_and_users(session)
        await seed_categories_and_budgets(session)
        await seed_transactions(session)
        await analyze_all(session)
        await print_summary(session)

    await engine.dispose()
    print("\n[seed] done.")


if __name__ == "__main__":
    asyncio.run(main())
