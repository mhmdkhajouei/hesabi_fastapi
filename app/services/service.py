from dataclasses import asdict
from datetime import datetime, timezone
from app.db.crud import CategoryRepo, TransactionRepo, ComputeRepo
from app.domain.models import CategoryDomain, TransactionDomain
from app.errors.exceptions import NotFoundError

class CategoryService:

    def __init__(self, repo: CategoryRepo):

        self.repo = repo

    async def add_category(self, data:dict):

        cd = CategoryDomain(
            name= data.get("name"),
            budget_goal=data.get("budget_goal"),
        )

        insert_data = asdict(cd)

        return await self.repo.insert_category(insert_data)

    async def edit_category(self, category_id: int, data: dict):

        category = await self.repo.get_category(category_id)

        if not category:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )

        updated_name = data.get("name", category.name)
        updated_budget = data.get("budget_goal", category.budget.goal)

        cd = CategoryDomain(
            name=updated_name,
            budget_goal=updated_budget
        )

        update_data = asdict(cd)

        return await self.repo.update_category(category,update_data)

    async def delete_category(self, category_id: int):

        deleted = await self.repo.delete_category(category_id)

        if not deleted:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )

        return True

    async def get_all_categories(self):
        return await self.repo.get_all_categories()


class TransactionService:

    def __init__(self, repo: TransactionRepo, category_repo: CategoryRepo):

        self.repo = repo
        self.category_repo = category_repo

    async def add_transaction(self, data:dict):

        tx_date = data.get("date") or datetime.now(timezone.utc)

        tx = TransactionDomain(
            amount=data.get("amount"),
            type=data.get("type"),
            category_id=data.get("category_id"),
            date=tx_date,
            note=data.get("note")
        )

        if tx.category_id is not None:
            exist = await self.category_repo.check_category(tx.category_id)
            if not exist:
                raise NotFoundError(
                    message=f"Category with ID {tx.category_id} not found",
                    error_code="CATEGORY_NOT_FOUND"
                )

        insert_data = asdict(tx)

        return await self.repo.insert_transaction(insert_data)

    async def edit_transaction(self, transaction_id: int, data: dict):

        transaction = await self.repo.get_transaction(transaction_id)

        if not transaction:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )

        updated_amount = data.get("amount", transaction.amount)
        updated_type = data.get("type", transaction.type)
        updated_date = data.get("date", transaction.date)
        updated_category_id = data.get("category_id", transaction.category_id)
        updated_note = data.get("note", transaction.note)

        if updated_category_id is not None:
            exist = await self.category_repo.check_category(updated_category_id)
            if not exist:
                raise NotFoundError(
                    message=f"Category with ID {updated_category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )

        tx = TransactionDomain(
            amount= updated_amount,
            type= updated_type,
            date= updated_date,
            category_id= updated_category_id,
            note= updated_note,
        )

        updated_data = asdict(tx)

        return await self.repo.update_transaction(transaction,updated_data)

    async def delete_transaction(self, transaction_id:int):

        deleted= await self.repo.delete_transaction(transaction_id)

        if not deleted:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )

        return True

    async def get_all_transactions(self):
        return await self.repo.get_all_transactions()


class ComputeService:

    def __init__(self, repo: ComputeRepo):
        self.repo = repo

    async def income_balance(self) -> int:
        return await self.repo.get_total_amount_by_type("income")

    async def expense_balance(self) -> int:
        return await self.repo.get_total_amount_by_type("expense")

    async def total_balance(self) -> int:
        income = await self.repo.get_total_amount_by_type("income") or 0
        expense = await self.repo.get_total_amount_by_type("expense") or 0
        total = income - expense
        return total

    async def category_balance(self, category_id: int) -> dict:
        row = await self.repo.get_category_balance(category_id)
        if not row:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND"

            )

        result = {
            "name": row["category_name"],
            "budget": row["budget_goal"],
            "spent": row["spent"],
            "remaining": row["budget_goal"] - row["spent"]
        }
        return result

    async def categories_balance(self) -> list[dict]:
        rows = await self.repo.get_all_categories_balance()
        result = []

        for row in rows:
            result.append({
                "name": row["category_name"],
                "budget": row["budget_goal"],
                "spent": row["spent"],
                "remaining": row["budget_goal"] - row["spent"]
            })

        return result








