from datetime import UTC, datetime

from app.db.crud import (
    CategoryRepo,
    ComputeRepo,
    HouseholdRepo,
    TransactionRepo,
    UserRepo,
)
from app.db.database import HouseholdRole
from app.domain_models import CategoryDomain, TransactionDomain
from app.errors.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    ForbiddenError,
    NotFoundError,
)
from app.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    Token,
    TokenRefreshRequest,
    TokenRefreshResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    UserCreateInternal,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.security import (
    DUMMY_PASSWORD_HASH,
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class CategoryService:
    def __init__(self, repo: CategoryRepo):

        self.repo = repo

    async def add_category(
        self, household_id: int, category: CategoryCreate
    ) -> CategoryResponse:
        cd = CategoryDomain(
            name=category.name,
            budget_goal=category.budget_goal,
            household_id=household_id,
        )

        cg = await self.repo.insert_category(category=cd)
        return CategoryResponse.model_validate(cg)

    async def edit_category(
        self, household_id: int, category_id: int, data: CategoryUpdate
    ) -> CategoryResponse:

        category = await self.repo.get_category(household_id, category_id)

        if not category:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )

        update_data = data.model_dump(exclude_unset=True)

        cd = CategoryDomain(
            name=update_data.get("name", category.name),
            budget_goal=update_data.get("budget_goal", category.budget_goal),
            household_id=household_id,
        )
        cg = await self.repo.update_category(category, cd)
        return CategoryResponse.model_validate(cg)

    async def delete_category(self, household_id: int, category_id: int) -> None:

        deleted = await self.repo.delete_category(household_id, category_id)

        if not deleted:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )

    async def get_category(
        self, household_id: int, category_id: int
    ) -> CategoryResponse:
        category = await self.repo.get_category(household_id, category_id)
        if not category:
            raise NotFoundError(
                message=f"Category with ID {category_id} not found",
                error_code="CATEGORY_NOT_FOUND",
            )
        return CategoryResponse.model_validate(category)

    async def get_all_categories(self, household_id: int) -> list[CategoryResponse]:
        result = await self.repo.get_all_categories(household_id)
        return [CategoryResponse.model_validate(obj) for obj in result]


class TransactionService:
    def __init__(self, repo: TransactionRepo, category_repo: CategoryRepo):

        self.repo = repo
        self.category_repo = category_repo

    async def add_transaction(
        self, household_id: int, user_id: int, data: TransactionCreate
    ) -> TransactionResponse:

        tx_date = data.date or datetime.now(UTC)

        tx = TransactionDomain(
            amount=data.amount,
            household_id=household_id,
            created_by=user_id,
            type=data.type,
            category_id=data.category_id,
            date=tx_date,
            note=data.note,
        )

        if tx.category_id is not None:
            exist = await self.category_repo.check_category(
                household_id, tx.category_id
            )
            if not exist:
                raise NotFoundError(
                    message=f"Category with ID {tx.category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )
        tn = await self.repo.insert_transaction(tx)
        return TransactionResponse.model_validate(tn)

    async def edit_transaction(
        self,
        household_id: int,
        transaction_id: int,
        user_id: int,
        user_role: HouseholdRole,
        data: TransactionUpdate,
    ) -> TransactionResponse:

        transaction = await self.repo.get_transaction(household_id, transaction_id)

        if not transaction:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )

        if user_role == HouseholdRole.MEMBER and transaction.created_by != user_id:
            raise ForbiddenError(
                message="You can only edit your own transaction",
                error_code="INSUFFICIENT_PERMISSIONS",
            )

        update_data = data.model_dump(exclude_unset=True)

        updated_amount = update_data.get("amount", transaction.amount)
        updated_type = update_data.get("type", transaction.type)

        updated_date = update_data.get("date", transaction.date)
        if updated_date.tzinfo is None:
            updated_date = updated_date.replace(tzinfo=UTC)

        if updated_type == "income":
            updated_category_id = None
        else:
            updated_category_id = update_data.get(
                "category_id", transaction.category_id
            )

        updated_note = update_data.get("note", transaction.note)

        if updated_category_id is not None:
            exist = await self.category_repo.check_category(
                household_id, updated_category_id
            )
            if not exist:
                raise NotFoundError(
                    message=f"Category with ID {updated_category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )

        tx = TransactionDomain(
            amount=updated_amount,
            household_id=household_id,
            created_by=transaction.created_by,
            type=updated_type,
            date=updated_date,
            category_id=updated_category_id,
            note=updated_note,
        )

        tn = await self.repo.update_transaction(transaction, tx)
        return TransactionResponse.model_validate(tn)

    async def delete_transaction(
        self,
        household_id: int,
        transaction_id: int,
        user_id: int,
        user_role: HouseholdRole,
    ) -> None:

        transaction = await self.repo.get_transaction(household_id, transaction_id)

        if not transaction:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )

        if user_role == HouseholdRole.MEMBER and transaction.created_by != user_id:
            raise ForbiddenError(
                message="You can only delete your own transaction",
                error_code="INSUFFICIENT_PERMISSIONS",
            )

        deleted = await self.repo.delete_transaction(household_id, transaction_id)

        if not deleted:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )

    async def get_transaction(
        self, household_id: int, transaction_id: int
    ) -> TransactionResponse:
        transaction = await self.repo.get_transaction(household_id, transaction_id)

        if not transaction:
            raise NotFoundError(
                message=f"Transaction with id {transaction_id} not found",
                error_code="TRANSACTION_NOT_FOUND",
            )
        return TransactionResponse.model_validate(transaction)

    async def get_all_transactions(
        self, household_id: int
    ) -> list[TransactionResponse]:
        result = await self.repo.get_all_transactions(household_id)
        return [TransactionResponse.model_validate(obj) for obj in result]


class ComputeService:
    def __init__(self, repo: ComputeRepo):
        self.repo = repo

    async def get_financial_summary(self, household_id: int) -> dict:
        income = await self.repo.get_total_amount_by_type(household_id, "income")
        expense = await self.repo.get_total_amount_by_type(household_id, "expense")

        return {"income": income, "expense": expense, "total": income - expense}

    async def category_balance(self, household_id: int, category_id: int) -> dict:
        row = await self.repo.get_category_balance(household_id, category_id)
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

    async def categories_balance(self, household_id: int) -> list[dict]:
        rows = await self.repo.get_all_categories_balance(household_id)
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

        password_hashed = hash_password(user_in.password)

        internal_user = UserCreateInternal(
            email=user_in.email,
            password_hash=password_hashed,
            name=user_in.name,
        )

        created_user = await self.repo.create_user(internal_user)
        return UserResponse.model_validate(created_user)


class AuthService:
    def __init__(self, repo: UserRepo):
        self.repo = repo

    async def authenticate_user(self, credentials: UserLogin) -> Token:

        user = await self.repo.get_user_by_email(credentials.email)
        user_hash = user.password_hash if user else DUMMY_PASSWORD_HASH
        password_valid = verify_password(credentials.password, user_hash)

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
            token_type=TokenType.BEARER,
        )

    async def request_refresh_token(
        self, refresh_in: TokenRefreshRequest
    ) -> TokenRefreshResponse:

        payload = decode_token(refresh_in.refresh_token)
        token_type = payload.type

        if token_type != TokenType.REFRESH:
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
            token_type=TokenType.BEARER,
        )


class HouseholdService:
    def __init__(self, repo: HouseholdRepo):
        self.repo = repo

    async def get_personal_household_id(self, user_id: int) -> int | None:
        return await self.repo.get_personal_household_id(user_id)
