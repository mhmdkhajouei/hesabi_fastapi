import asyncio
import random
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import text

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    JobStatus,
    RecurringTransaction,
    ReportJob,
    Transaction,
    User,
    async_db_session,
    engine,
)

RANDOM_SEED = 42

N_HOUSEHOLDS = 10
N_USERS_PER_HOUSEHOLD = 2
N_CATEGORIES_PER_HOUSEHOLD = 10
N_TRANSACTIONS_PER_HOUSEHOLD = 10_000
N_RECURRING_PER_HOUSEHOLD = 50
N_REPORTS_PER_HOUSEHOLD = 100

EXPENSE_RATIO = 0.70

AMOUNT_BUCKETS = [
    (0.80, 10_000, 500_000),
    (0.15, 500_000, 2_000_000),
    (0.05, 2_000_000, 5_000_000),
]

DATE_WINDOW_DAYS = 730

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


async def truncate_all(session) -> None:
    await session.execute(
        text(
            f"""
            TRUNCATE TABLE
                {ReportJob.__tablename__},
                {RecurringTransaction.__tablename__},
                {Transaction.__tablename__},
                {Budget.__tablename__},
                {Category.__tablename__},
                {HouseholdMember.__tablename__},
                {Household.__tablename__},
                {User.__tablename__}
            RESTART IDENTITY CASCADE
            """
        )
    )
    await session.commit()
    print("[seed] truncated all tables")


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
            f"""
            INSERT INTO {Household.__tablename__} (id, name, is_personal)
            VALUES (:id, :name, :is_personal)
            """
        ),
        household_rows,
    )

    await session.execute(
        text(
            f"""
            INSERT INTO {User.__tablename__} (id, name, email, password_hash, is_active)
            VALUES (:id, :name, :email, :password_hash, :is_active)
            """
        ),
        user_rows,
    )

    await session.execute(
        text(
            f"""
            INSERT INTO {HouseholdMember.__tablename__} (user_id, household_id, role)
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
            f"""
            INSERT INTO {Category.__tablename__} (id, name, household_id)
            VALUES (:id, :name, :household_id)
            """
        ),
        category_rows,
    )

    await session.execute(
        text(
            f"""
            INSERT INTO {Budget.__tablename__} (id, goal, currency, category_id)
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

        r = random.random()
        cumulative = 0.0
        amount = 100_000
        for prob, lo, hi in AMOUNT_BUCKETS:
            cumulative += prob
            if r <= cumulative:
                amount = random.randint(lo, hi)
                break

        days_ago = random.randint(0, DATE_WINDOW_DAYS)
        tx_date = now - timedelta(days=days_ago)

        if is_expense:
            cat_index = random.randint(0, N_CATEGORIES_PER_HOUSEHOLD - 1)
            category_id = (
                (household_id - 1) * N_CATEGORIES_PER_HOUSEHOLD + cat_index + 1
            )
        else:
            category_id = None

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

    CHUNK = 5_000
    for i in range(0, len(rows), CHUNK):
        chunk = rows[i : i + CHUNK]
        await session.execute(
            text(
                f"""
                INSERT INTO {Transaction.__tablename__}
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


async def seed_recurring_transactions(session) -> None:
    now = datetime.now(UTC)
    frequencies = ["daily"]
    rows = []

    for h in range(1, N_HOUSEHOLDS + 1):
        for i in range(N_RECURRING_PER_HOUSEHOLD):
            is_expense = random.random() < EXPENSE_RATIO
            tx_type = "expense" if is_expense else "income"

            if is_expense:
                cat_index = random.randint(0, N_CATEGORIES_PER_HOUSEHOLD - 1)
                category_id = (h - 1) * N_CATEGORIES_PER_HOUSEHOLD + cat_index + 1
            else:
                category_id = None

            member_offset = random.randint(0, N_USERS_PER_HOUSEHOLD - 1)
            created_by = (h - 1) * N_USERS_PER_HOUSEHOLD + member_offset + 1

            days_offset = random.randint(-15, 45)
            next_run = now + timedelta(days=days_offset)

            rows.append(
                RecurringTransaction(
                    household_id=h,
                    created_by=created_by,
                    amount=random.randint(50_000, 2_000_000),
                    type=tx_type,
                    currency="TOMAN",
                    note=f"Recurring item {h}-{i}",
                    category_id=category_id,
                    frequency=random.choice(frequencies),
                    next_run_date=next_run,
                    is_active=random.random() > 0.15,
                )
            )

    session.add_all(rows)
    await session.commit()
    print(f"[seed] inserted {len(rows)} recurring transaction templates")


async def seed_report_jobs(session) -> None:
    now = datetime.now(UTC)
    statuses = [JobStatus.COMPLETED, JobStatus.PENDING, JobStatus.FAILED]
    rows = []

    for h in range(1, N_HOUSEHOLDS + 1):
        for i in range(N_REPORTS_PER_HOUSEHOLD):
            st = random.choices(statuses, weights=[0.75, 0.15, 0.10])[0]
            member_offset = random.randint(0, N_USERS_PER_HOUSEHOLD - 1)
            requested_by = (h - 1) * N_USERS_PER_HOUSEHOLD + member_offset + 1

            start_days = random.randint(60, 365)
            end_days = random.randint(0, 30)
            start_date = (now - timedelta(days=start_days)).date().isoformat()
            end_date = (now - timedelta(days=end_days)).date().isoformat()

            filters: dict[str, Any] = {
                "start_date": start_date,
                "end_date": end_date,
            }
            if random.random() < 0.6:
                filters["type"] = "expense" if random.random() < 0.8 else "income"
            if random.random() < 0.4:
                cat_index = random.randint(0, N_CATEGORIES_PER_HOUSEHOLD - 1)
                filters["category_id"] = (
                    (h - 1) * N_CATEGORIES_PER_HOUSEHOLD + cat_index + 1
                )

            file_path = (
                f"/tmp/reports/report_hh{h}_job{i}.csv"
                if st == JobStatus.COMPLETED
                else None
            )
            err_msg = "Worker timeout during export" if st == JobStatus.FAILED else None
            completed_at = (
                now - timedelta(minutes=random.randint(5, 1440))
                if st in (JobStatus.COMPLETED, JobStatus.FAILED)
                else None
            )

            rows.append(
                ReportJob(
                    household_id=h,
                    requested_by=requested_by,
                    status=st,
                    filters=filters,
                    file_path=file_path,
                    error_message=err_msg,
                    completed_at=completed_at,
                )
            )

    session.add_all(rows)
    await session.commit()
    print(f"[seed] inserted {len(rows)} report jobs")


async def analyze_all(session) -> None:
    await session.execute(text("ANALYZE"))
    await session.commit()
    print("[seed] ran ANALYZE on all tables")


async def print_summary(session) -> None:
    tables = [
        Household.__tablename__,
        User.__tablename__,
        HouseholdMember.__tablename__,
        Category.__tablename__,
        Budget.__tablename__,
        Transaction.__tablename__,
        RecurringTransaction.__tablename__,
        ReportJob.__tablename__,
    ]
    print("\n[seed] row counts:")
    for tbl in tables:
        count = await session.scalar(text(f"SELECT COUNT(*) FROM {tbl}"))
        print(f"  {tbl:<25} {count:>8}")


async def main() -> None:
    random.seed(RANDOM_SEED)

    async with async_db_session() as session:
        await truncate_all(session)
        await seed_households_and_users(session)
        await seed_categories_and_budgets(session)
        await seed_transactions(session)
        await seed_recurring_transactions(session)
        await seed_report_jobs(session)
        await analyze_all(session)
        await print_summary(session)

    await engine.dispose()
    print("\n[seed] done.")


if __name__ == "__main__":
    asyncio.run(main())
