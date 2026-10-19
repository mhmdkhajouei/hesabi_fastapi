import asyncio
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import and_, func, select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    Transaction,
    async_db_session,
    engine,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_PATH = Path("docs/explain_after.md")

# Representative parameter values, one from each part of the domain.
HID_VALUES = [1, 5, 10]  # households (first / middle / last)
CID_VALUES = [1, 50, 100]  # categories (first / middle / last)
TID_VALUES = [1, 50_000, 100_000]  # transactions (first / middle / last)
UID_VALUES = [1, 10, 20]  # users (first / middle / last)


# ---------------------------------------------------------------------------
# SQL builders (mirror crud.py exactly, including eager loading)
# ---------------------------------------------------------------------------


def _compile(stmt) -> str:
    return str(
        stmt.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True},
        )
    )


# ----- CategoryRepo -----


def get_all_categories_sql(household_id: int) -> str:
    stmt = (
        select(Category)
        .options(joinedload(Category.budget))
        .where(Category.household_id == household_id)
        .order_by(Category.id.asc())
    )
    return _compile(stmt)


def get_category_sql(household_id: int, category_id: int) -> str:
    stmt = (
        select(Category)
        .options(joinedload(Category.budget))
        .where(
            Category.id == category_id,
            Category.household_id == household_id,
        )
    )
    return _compile(stmt)


# ----- TransactionRepo -----


def get_all_transactions_sql(household_id: int) -> str:
    stmt = (
        select(Transaction)
        .where(Transaction.household_id == household_id)
        .order_by(Transaction.id.asc())
    )
    return _compile(stmt)


def get_all_transactions_child_sql(category_ids: list[int]) -> str:
    stmt = select(Category).where(Category.id.in_(category_ids))
    return _compile(stmt)


def get_transaction_sql(household_id: int, transaction_id: int) -> str:
    stmt = (
        select(Transaction)
        .options(joinedload(Transaction.category))
        .where(
            Transaction.id == transaction_id,
            Transaction.household_id == household_id,
        )
    )
    return _compile(stmt)


# ----- ComputeRepo -----


def get_total_amount_by_type_sql(household_id: int, transaction_type: str) -> str:
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.type == transaction_type,
        Transaction.household_id == household_id,
    )
    return _compile(stmt)


def get_category_balance_sql(household_id: int, category_id: int) -> str:
    stmt = (
        select(
            Category.name.label("category_name"),
            Budget.goal.label("budget_goal"),
            func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
        )
        .join(Budget, Category.id == Budget.category_id)
        .outerjoin(
            Transaction,
            and_(
                Category.id == Transaction.category_id,
                Transaction.type == "expense",
                Transaction.household_id == household_id,
            ),
        )
        .where(Category.id == category_id, Category.household_id == household_id)
        .group_by(Category.id, Category.name, Budget.goal)
    )
    return _compile(stmt)


def get_all_categories_balance_sql(household_id: int) -> str:
    stmt = (
        select(
            Category.name.label("category_name"),
            Budget.goal.label("budget_goal"),
            func.coalesce(func.sum(Transaction.amount), 0).label("spent"),
        )
        .join(Budget, Category.id == Budget.category_id)
        .outerjoin(
            Transaction,
            and_(
                Category.id == Transaction.category_id,
                Transaction.household_id == household_id,
                Transaction.type == "expense",
            ),
        )
        .where(Category.household_id == household_id)
        .group_by(Category.id, Category.name, Budget.goal)
        .order_by(Category.id.asc())
    )
    return _compile(stmt)


def get_category_total_spent_sql(household_id: int, category_id: int) -> str:
    stmt = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.category_id == category_id,
        Transaction.household_id == household_id,
        Transaction.type == "expense",
    )
    return _compile(stmt)


# ----- HouseholdRepo -----


def get_personal_household_id_sql(user_id: int) -> str:
    stmt = (
        select(Household.id)
        .join(HouseholdMember, Household.id == HouseholdMember.household_id)
        .where(
            HouseholdMember.user_id == user_id,
            Household.is_personal.is_(True),
        )
    )
    return _compile(stmt)


def get_user_role_sql(user_id: int, household_id: int) -> str:
    stmt = select(HouseholdMember.role).where(
        HouseholdMember.user_id == user_id,
        HouseholdMember.household_id == household_id,
    )
    return _compile(stmt)


# ----- BudgetRepo -----


def get_budget_by_category_id_sql(category_id: int) -> str:
    stmt = select(Budget).where(Budget.category_id == category_id)
    return _compile(stmt)


# ---------------------------------------------------------------------------
# Query inventory
# ---------------------------------------------------------------------------

QUERIES = [
    {
        "name": "get_all_categories",
        "func": get_all_categories_sql,
        "params": [{"household_id": h} for h in HID_VALUES],
    },
    {
        "name": "get_category",
        "func": get_category_sql,
        "params": [
            {"household_id": 1, "category_id": 1},
            {"household_id": 5, "category_id": 50},
            {"household_id": 10, "category_id": 100},
        ],
    },
    {
        "name": "get_all_transactions (parent, selectinload)",
        "func": get_all_transactions_sql,
        "params": [{"household_id": h} for h in HID_VALUES],
    },
    {
        "name": "get_transaction",
        "func": get_transaction_sql,
        "params": [
            {"household_id": 1, "transaction_id": 1},
            {"household_id": 5, "transaction_id": 50_000},
            {"household_id": 10, "transaction_id": 100_000},
        ],
    },
    {
        "name": "get_total_amount_by_type (expense)",
        "func": get_total_amount_by_type_sql,
        "params": [
            {"household_id": h, "transaction_type": "expense"} for h in HID_VALUES
        ],
    },
    {
        "name": "get_total_amount_by_type (income)",
        "func": get_total_amount_by_type_sql,
        "params": [
            {"household_id": h, "transaction_type": "income"} for h in HID_VALUES
        ],
    },
    {
        "name": "get_category_balance",
        "func": get_category_balance_sql,
        "params": [
            {"household_id": 1, "category_id": 1},
            {"household_id": 5, "category_id": 50},
            {"household_id": 10, "category_id": 100},
        ],
    },
    {
        "name": "get_all_categories_balance",
        "func": get_all_categories_balance_sql,
        "params": [{"household_id": h} for h in HID_VALUES],
    },
    {
        "name": "get_category_total_spent",
        "func": get_category_total_spent_sql,
        "params": [
            {"household_id": 1, "category_id": 1},
            {"household_id": 5, "category_id": 50},
            {"household_id": 10, "category_id": 100},
        ],
    },
    {
        "name": "get_personal_household_id",
        "func": get_personal_household_id_sql,
        "params": [{"user_id": u} for u in UID_VALUES],
    },
    {
        "name": "get_user_role",
        "func": get_user_role_sql,
        "params": [
            {"user_id": 1, "household_id": 1},
            {"user_id": 10, "household_id": 5},
            {"user_id": 20, "household_id": 10},
        ],
    },
    {
        "name": "get_budget_by_category_id",
        "func": get_budget_by_category_id_sql,
        "params": [{"category_id": c} for c in CID_VALUES],
    },
]


# ---------------------------------------------------------------------------
# EXPLAIN execution
# ---------------------------------------------------------------------------


async def explain_query(session, sql: str) -> list[str]:
    explain_sql = f"EXPLAIN (ANALYZE, BUFFERS) {sql}"
    result = await session.execute(text(explain_sql))
    return [row[0] for row in result]


async def fetch_category_ids_for_household(session, household_id: int) -> list[int]:
    result = await session.execute(
        select(Category.id).where(Category.household_id == household_id)
    )
    return [row[0] for row in result]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    lines: list[str] = []
    lines.append("# EXPLAIN After Indexes\n")
    lines.append(f"Generated: {datetime.now(UTC).isoformat()}\n")
    lines.append("Dataset: 10 households, 100 categories, 100,000 transactions\n")
    lines.append(
        "All plans use `EXPLAIN (ANALYZE, BUFFERS)` with literal-bound parameters.\n"
    )
    lines.append("---\n")

    async with async_db_session() as session:
        for query in QUERIES:
            lines.append(f"\n## {query['name']}\n")

            for params in query["params"]:
                sql = query["func"](**params)
                plan = await explain_query(session, sql)

                params_str = ", ".join(f"{k}={v}" for k, v in params.items())
                lines.append(f"\n### `{params_str}`\n")
                lines.append("**SQL:**\n")
                lines.append("```sql")
                lines.append(sql.strip())
                lines.append("```\n")
                lines.append("**Plan:**\n")
                lines.append("```")
                lines.extend(plan)
                lines.append("```\n")

            # Special handling for get_all_transactions: also EXPLAIN the selectinload child query
            if query["name"].startswith("get_all_transactions"):
                lines.append("\n### selectinload child query (representative)\n")
                lines.append(
                    "The child query uses `WHERE categories.id IN (...)` with the ids of the\n"
                    "household's categories. We EXPLAIN it with the actual id list for household 1.\n"
                )
                cat_ids = await fetch_category_ids_for_household(session, 1)
                child_sql = get_all_transactions_child_sql(cat_ids)
                child_plan = await explain_query(session, child_sql)
                lines.append("**SQL:**\n")
                lines.append("```sql")
                lines.append(child_sql.strip())
                lines.append("```\n")
                lines.append("**Plan:**\n")
                lines.append("```")
                lines.extend(child_plan)
                lines.append("```\n")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines))
    print(f"[explain] wrote {OUTPUT_PATH}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
