from dataclasses import asdict
from datetime import UTC, datetime

from app.db.crud import CategoryRepo, ComputeRepo, TransactionRepo, UserRepo
from app.domain_models import CategoryDomain, TransactionDomain
from app.errors.exceptions import AuthenticationError, BusinessRuleError, NotFoundError
from app.schemas import (
    Token,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserCreateInternal,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class CategoryService:
    def __init__(self, repo: CategoryRepo):

        self.repo = repo

    async def add_category(self, data: dict):

        cd = CategoryDomain(
            name=data["name"],
            budget_goal=data["budget_goal"],
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
        updated_budget = data.get("budget_goal", category.budget_goal)

        cd = CategoryDomain(name=updated_name, budget_goal=updated_budget)

        update_data = asdict(cd)

        return await self.repo.update_category(category, update_data)

    async def delete_category(self, category_id: int):

        deleted = await self.repo.delete_category(category_id)

        if not deleted:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )

        return True

    async def get_category(self, category_id: int):
        category = await self.repo.get_category(category_id)
        if not category:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )
        return category

    async def get_all_categories(self):
        return await self.repo.get_all_categories()


class TransactionService:
    def __init__(self, repo: TransactionRepo, category_repo: CategoryRepo):

        self.repo = repo
        self.category_repo = category_repo

    async def add_transaction(self, data: dict):

        tx_date = data.get("date") or datetime.now(UTC)

        tx = TransactionDomain(
            amount=data["amount"],
            type=data["type"],
            category_id=data.get("category_id"),
            date=tx_date,
            note=data.get("note"),
        )

        if tx.category_id is not None:
            exist = await self.category_repo.check_category(tx.category_id)
            if not exist:
                raise NotFoundError(
                    message=f"Category with ID {tx.category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
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
            amount=updated_amount,
            type=updated_type,
            date=updated_date,
            category_id=updated_category_id,
            note=updated_note,
        )

        updated_data = asdict(tx)

        return await self.repo.update_transaction(transaction, updated_data)

    async def delete_transaction(self, transaction_id: int):

        deleted = await self.repo.delete_transaction(transaction_id)

        if not deleted:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )

        return True

    async def get_transaction(self, transaction_id: int):
        transaction = await self.repo.get_transaction(transaction_id)

        if not transaction:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )
        return transaction

    async def get_all_transactions(self):
        return await self.repo.get_all_transactions()


class ComputeService:
    def __init__(self, repo: ComputeRepo):
        self.repo = repo

    async def get_financial_summary(self) -> dict:
        income = await self.repo.get_total_amount_by_type("income")
        expense = await self.repo.get_total_amount_by_type("expense")

        return {"income": income, "expense": expense, "total": income - expense}

    async def category_balance(self, category_id: int) -> dict:
        row = await self.repo.get_category_balance(category_id)
        if not row:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )

        result = {
            "name": row["category_name"],
            "budget_goal": row["budget_goal"],
            "spent": row["spent"],
            "remaining": row["budget_goal"] - row["spent"],
        }
        return result

    async def categories_balance(self) -> list[dict]:
        rows = await self.repo.get_all_categories_balance()
        result = []

        for row in rows:
            result.append(
                {
                    "name": row["category_name"],
                    "budget_goal": row["budget_goal"],
                    "spent": row["spent"],
                    "remaining": row["budget_goal"] - row["spent"],
                }
            )

        return result


class UserService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def user_register(self, user_in: UserRegister) -> UserResponse:
        existing_user = await self.repo.get_user_by_email(user_in.email)

        if existing_user:
            raise BusinessRuleError(
                message="A user with this email already exists",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        password_hashed = hash_password(user_in.plain_password)

        internal_user = UserCreateInternal(
            email=user_in.email,
            password_hash=password_hashed,
            name=user_in.name,
        )

        created_user = await self.repo.create_user(internal_user)
        return UserResponse.model_validate(created_user)

    async def authenticate_user(self, credentials: UserLogin) -> Token:

        user = await self.repo.get_user_by_email(credentials.email)
        user_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
        password_valid = verify_password(credentials.plain_password, user_hash)

        if not user or not password_valid:
            raise AuthenticationError(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        if not user.is_active:
            raise AuthenticationError(
                message="User account is deactivated",
                error_code="USER_DEACTIVATED",
            )

        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def request_refresh_token(
        self, refresh_in: TokenRefreshRequest
    ) -> TokenRefreshResponse:

        payload = decode_token(refresh_in.refresh_token)
        token_type = payload.type

        if token_type != "refresh":
            raise AuthenticationError(
                message="Invalid token type for refresh",
                error_code="INVALID_TOKEN_TYPE",
            )

        if not payload.sub.isdigit():
            raise AuthenticationError(
                message="Invalid token subject",
                error_code="INVALID_TOKEN_SUBJECT",
            )

        user_id = int(payload.sub)
        user = await self.repo.get_user_by_id(user_id)
        if not user:
            raise AuthenticationError(
                message="User not found",
                error_code="USER_NOT_FOUND",
            )

        if not user.is_active:
            raise AuthenticationError(
                message="User account is deactivated",
                error_code="USER_DEACTIVATED",
            )

        new_access_token = create_access_token(subject=str(user.id))

        return TokenRefreshResponse(
            access_token=new_access_token,
            token_type="bearer",
        )
