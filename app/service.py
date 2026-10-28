import csv
import io
from datetime import UTC, datetime, timedelta
from pathlib import Path

import aiofiles
from redis.asyncio import Redis

from app.cache import (
    categories_key,
    category_key,
    deserialize,
    invalidate_compute_cache,
    serialize,
    summary_key,
)
from app.db.database import HouseholdRole, JobStatus
from app.db.uow import UnitOfWork
from app.domain_models import (
    CategoryDomain,
    RecurringTransactionDomain,
    ReportFiltersDomain,
    ReportJobDomain,
    TransactionDomain,
)
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
    RecurringTransactionResponse,
    RecurringTransactionUpdate,
    ReportFilters,
    ReportJobResponse,
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
    def __init__(self, uow: UnitOfWork, redis: Redis):
        self.uow = uow
        self.redis = redis

    async def add_category(
        self, household_id: int, category: CategoryCreate
    ) -> CategoryResponse:
        async with self.uow:
            cd = CategoryDomain(
                name=category.name,
                budget_goal=category.budget_goal,
                household_id=household_id,
            )

            cg = await self.uow.categories.insert_category(category=cd)
            response = CategoryResponse.model_validate(cg)

        await invalidate_compute_cache(self.redis, household_id)
        return response

    async def edit_category(
        self, household_id: int, category_id: int, data: CategoryUpdate
    ) -> CategoryResponse:
        async with self.uow:
            category = await self.uow.categories.get_category(household_id, category_id)

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
            cg = await self.uow.categories.update_category(category, cd)
            response = CategoryResponse.model_validate(cg)

        await invalidate_compute_cache(self.redis, household_id, [category_id])
        return response

    async def delete_category(self, household_id: int, category_id: int) -> None:
        async with self.uow:
            deleted = await self.uow.categories.delete_category(
                household_id, category_id
            )

            if not deleted:
                raise NotFoundError(
                    message=f"Category with ID {category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )
        await invalidate_compute_cache(self.redis, household_id, [category_id])

    async def get_category(
        self, household_id: int, category_id: int
    ) -> CategoryResponse:
        async with self.uow:
            category = await self.uow.categories.get_category(household_id, category_id)
            if not category:
                raise NotFoundError(
                    message=f"Category with ID {category_id} not found",
                    error_code="CATEGORY_NOT_FOUND",
                )
            return CategoryResponse.model_validate(category)

    async def get_all_categories(self, household_id: int) -> list[CategoryResponse]:
        async with self.uow:
            result = await self.uow.categories.get_all_categories(household_id)
            return [CategoryResponse.model_validate(obj) for obj in result]


class TransactionService:
    def __init__(self, uow: UnitOfWork, redis: Redis):
        self.uow = uow
        self.redis = redis

    async def add_transaction(
        self,
        household_id: int,
        user_id: int,
        data: TransactionCreate,
        user_role: HouseholdRole,
    ) -> TransactionResponse:

        async with self.uow:
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
                exist = await self.uow.categories.check_category(
                    household_id, tx.category_id
                )
                if not exist:
                    raise NotFoundError(
                        message=f"Category with ID {tx.category_id} not found",
                        error_code="CATEGORY_NOT_FOUND",
                    )
                if tx.type == "expense":
                    budget = await self.uow.budgets.get_budget_by_category_id(
                        category_id=tx.category_id, for_update=True
                    )

                    if budget:
                        current_spent = await self.uow.compute.get_category_total_spent(
                            household_id=tx.household_id,
                            category_id=tx.category_id,
                        )
                        if current_spent + tx.amount > budget.goal:
                            raise BusinessRuleError(
                                message="Transaction amount exceeds category budget goal",
                                error_code="BUDGET_LIMIT_EXCEEDED",
                            )
            tn = await self.uow.transactions.insert_transaction(tx)
            response = TransactionResponse.model_validate(tn)

            template_id = None
            delay_seconds = 0
            if data.frequency is not None:
                if user_role != HouseholdRole.OWNER:
                    raise ForbiddenError(
                        message="Only the household owner can create recurring transactions",
                        error_code="OWNER_PERMISSION_REQUIRED",
                    )
                next_run = tx_date + timedelta(days=1)

                template_domain = RecurringTransactionDomain(
                    household_id=household_id,
                    created_by=user_id,
                    amount=data.amount,
                    type=data.type,
                    category_id=data.category_id,
                    note=data.note,
                    frequency=data.frequency,
                    next_run_date=next_run,
                    is_active=True,
                )
                template = await self.uow.recurring_transactions.insert_template(
                    template_domain
                )
                template_id = template.id

                delay_seconds = (next_run - datetime.now(UTC)).total_seconds()

        await invalidate_compute_cache(self.redis, household_id, [tx.category_id])

        if template_id is not None:
            from app.worker import process_recurring_template_actor

            process_recurring_template_actor.send_with_options(
                args=(template_id,), delay=int(delay_seconds * 1000)
            )

        return response

    async def edit_transaction(
        self,
        household_id: int,
        transaction_id: int,
        user_id: int,
        user_role: HouseholdRole,
        data: TransactionUpdate,
    ) -> TransactionResponse:

        async with self.uow:
            transaction = await self.uow.transactions.get_transaction(
                household_id, transaction_id
            )

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
            old_category_id = transaction.category_id

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

            tx = TransactionDomain(
                amount=updated_amount,
                household_id=household_id,
                created_by=transaction.created_by,
                type=updated_type,
                date=updated_date,
                category_id=updated_category_id,
                note=updated_note,
            )

            if tx.category_id is not None:
                exist = await self.uow.categories.check_category(
                    household_id, tx.category_id
                )
                if not exist:
                    raise NotFoundError(
                        message=f"Category with ID {tx.category_id} not found",
                        error_code="CATEGORY_NOT_FOUND",
                    )
                if tx.type == "expense":
                    budget = await self.uow.budgets.get_budget_by_category_id(
                        category_id=tx.category_id, for_update=True
                    )

                    if budget:
                        current_spent = await self.uow.compute.get_category_total_spent(
                            household_id=tx.household_id,
                            category_id=tx.category_id,
                        )
                        if (
                            tx.category_id == transaction.category_id
                            and transaction.type == "expense"
                        ):
                            new_total = current_spent - transaction.amount + tx.amount
                        else:
                            new_total = current_spent + tx.amount

                        if new_total > budget.goal:
                            raise BusinessRuleError(
                                message="Transaction amount exceeds category budget goal",
                                error_code="BUDGET_LIMIT_EXCEEDED",
                            )

            tn = await self.uow.transactions.update_transaction(transaction, tx)
            response = TransactionResponse.model_validate(tn)

        await invalidate_compute_cache(
            self.redis, household_id, [old_category_id, tx.category_id]
        )
        return response

    async def delete_transaction(
        self,
        household_id: int,
        transaction_id: int,
        user_id: int,
        user_role: HouseholdRole,
    ) -> None:

        async with self.uow:
            transaction = await self.uow.transactions.get_transaction(
                household_id, transaction_id
            )

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
            category_id = transaction.category_id

            deleted = await self.uow.transactions.delete_transaction(
                household_id, transaction_id
            )

            if not deleted:
                raise NotFoundError(
                    message=f"Transaction with id {transaction_id} not found",
                    error_code="TRANSACTION_NOT_FOUND",
                )
        await invalidate_compute_cache(self.redis, household_id, [category_id])

    async def get_transaction(
        self, household_id: int, transaction_id: int
    ) -> TransactionResponse:
        async with self.uow:
            transaction = await self.uow.transactions.get_transaction(
                household_id, transaction_id
            )

            if not transaction:
                raise NotFoundError(
                    message=f"Transaction with id {transaction_id} not found",
                    error_code="TRANSACTION_NOT_FOUND",
                )
            return TransactionResponse.model_validate(transaction)

    async def get_all_transactions(
        self, household_id: int
    ) -> list[TransactionResponse]:
        async with self.uow:
            result = await self.uow.transactions.get_all_transactions(household_id)
            return [TransactionResponse.model_validate(obj) for obj in result]


class ComputeService:
    CACHE_TTL = 60

    def __init__(self, uow: UnitOfWork, redis: Redis):
        self.uow = uow
        self.redis = redis

    async def get_financial_summary(self, household_id: int) -> dict:
        cache_key = summary_key(household_id)
        cached = await self.redis.get(cache_key)
        if cached:
            return deserialize(cached)

        async with self.uow:
            income = await self.uow.compute.get_total_amount_by_type(
                household_id, "income"
            )
            expense = await self.uow.compute.get_total_amount_by_type(
                household_id, "expense"
            )

            result = {"income": income, "expense": expense, "total": income - expense}

        await self.redis.set(cache_key, serialize(result), ex=self.CACHE_TTL)
        return result

    async def category_balance(self, household_id: int, category_id: int) -> dict:
        cache_key = category_key(household_id, category_id)
        cached = await self.redis.get(cache_key)

        if cached:
            return deserialize(cached)

        async with self.uow:
            row = await self.uow.compute.get_category_balance(household_id, category_id)
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
        await self.redis.set(cache_key, serialize(result), ex=self.CACHE_TTL)
        return result

    async def categories_balance(self, household_id: int) -> list[dict]:
        cache_key = categories_key(household_id)
        cached = await self.redis.get(cache_key)
        if cached:
            return deserialize(cached)

        async with self.uow:
            rows = await self.uow.compute.get_all_categories_balance(household_id)
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
        await self.redis.set(cache_key, serialize(result), ex=self.CACHE_TTL)
        return result


class UserService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def user_register(self, user_in: UserRegister) -> UserResponse:
        async with self.uow:
            existing_user = await self.uow.user.get_user_by_email(user_in.email)

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

            created_user = await self.uow.user.create_user(internal_user)
            return UserResponse.model_validate(created_user)


class AuthService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def authenticate_user(self, credentials: UserLogin) -> Token:

        async with self.uow:
            user = await self.uow.user.get_user_by_email(credentials.email)
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
        async with self.uow:
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
            user = await self.uow.user.get_user_by_id(user_id)
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
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_personal_household_id(self, user_id: int) -> int | None:
        async with self.uow:
            return await self.uow.household.get_personal_household_id(user_id)


class ReportJobsService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_job(
        self, household_id: int, user_id: int, filters: ReportFilters | None
    ) -> ReportJobResponse:
        domain_filters = None
        if filters:
            domain_filters = ReportFiltersDomain(
                start_date=filters.start_date,
                end_date=filters.end_date,
                type=filters.type,
                category_id=filters.category_id,
            )

        async with self.uow:
            domain = ReportJobDomain(
                household_id=household_id,
                requested_by=user_id,
                filters=domain_filters,
            )
            job = await self.uow.reports.insert_report_job(domain)
            response = ReportJobResponse.model_validate(job)

        return response

    async def get_job_status(
        self, household_id: int, job_id: int, user_id: int
    ) -> ReportJobResponse:
        async with self.uow:
            job = await self.uow.reports.get_report_job_by_id(job_id=job_id)

            if (
                not job
                or job.household_id != household_id
                or job.requested_by != user_id
            ):
                raise NotFoundError(
                    message="Report job not found",
                    error_code="REPORT_NOT_FOUND",
                )

            return ReportJobResponse.model_validate(job)

    async def process_report(self, job_id: int) -> None:
        async with self.uow:
            job = await self.uow.reports.get_report_job_by_id(job_id=job_id)
            if not job:
                return

            await self.uow.reports.update_job_status(job_id, JobStatus.PROCESSING)
            await self.uow.session.commit()

            try:
                filters = ReportFiltersDomain.from_dict(job.filters)
                transactions = await self.uow.reports.get_transaction_for_report(
                    job.household_id, filters
                )

                reports_dir = Path("data/reports")
                reports_dir.mkdir(parents=True, exist_ok=True)
                file_path = reports_dir / f"report_{job_id}.csv"

                async with aiofiles.open(
                    file_path, mode="w", newline="", encoding="utf-8"
                ) as f:
                    output = io.StringIO()
                    writer = csv.writer(output)
                    writer.writerow(
                        ["ID", "Amount", "Type", "Category", "Creator", "Date", "Note"]
                    )
                    for tx in transactions:
                        writer.writerow(
                            [
                                tx.id,
                                tx.amount,
                                tx.type,
                                tx.category.name if tx.category else "N/A",
                                tx.creator.name if tx.creator else "N/A",
                                tx.date.isoformat(),
                                tx.note or "",
                            ]
                        )
                    await f.write(output.getvalue())

                await self.uow.reports.update_job_status(
                    job_id, JobStatus.COMPLETED, file_path=str(file_path)
                )

            except Exception as e:
                await self.uow.reports.update_job_status(
                    job_id, JobStatus.FAILED, error_message=str(e)
                )
                raise


class RecurringTransactionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_all_templates(
        self, household_id: int
    ) -> list[RecurringTransactionResponse]:
        async with self.uow:
            templates = await self.uow.recurring_transactions.get_all_templates(
                household_id
            )
            return [RecurringTransactionResponse.model_validate(t) for t in templates]

    async def update_template(
        self,
        household_id: int,
        template_id: int,
        user_id: int,
        user_role: HouseholdRole,
        data: RecurringTransactionUpdate,
    ) -> RecurringTransactionResponse:
        if user_role != HouseholdRole.OWNER:
            raise ForbiddenError(
                message="Only the household owner can update recurring templates",
                error_code="OWNER_PERMISSION_REQUIRED",
            )

        async with self.uow:
            template = await self.uow.recurring_transactions.get_template_by_id(
                household_id, template_id
            )
            if not template:
                raise NotFoundError(
                    message=f"Recurring template with ID {template_id} not found",
                    error_code="RECURRING_TEMPLATE_NOT_FOUND",
                )

            update_data = data.model_dump(exclude_unset=True)
            updated_amount = update_data.get("amount", template.amount)
            updated_type = update_data.get("type", template.type)
            updated_category_id = update_data.get("category_id", template.category_id)
            updated_note = update_data.get("note", template.note)
            updated_is_active = update_data.get("is_active", template.is_active)
            updated_next_run = update_data.get("next_run_date", template.next_run_date)

            updated_domain = RecurringTransactionDomain(
                household_id=household_id,
                created_by=template.created_by,
                amount=updated_amount,
                type=updated_type,
                category_id=updated_category_id,
                note=updated_note,
                frequency=template.frequency,
                next_run_date=updated_next_run,
                is_active=updated_is_active,
            )

            if updated_domain.category_id is not None:
                exist = await self.uow.categories.check_category(
                    household_id,
                    updated_domain.category_id,
                )
                if not exist:
                    raise NotFoundError(
                        message=f"Category with ID {updated_domain.category_id} not found",
                        error_code="CATEGORY_NOT_FOUND",
                    )
                if updated_domain.type == "expense":
                    budget = await self.uow.budgets.get_budget_by_category_id(
                        category_id=updated_domain.category_id,
                        for_update=True,
                    )
                    if budget and updated_domain.amount > budget.goal:
                        raise BusinessRuleError(
                            message="Template amount exceeds category budget goal",
                            error_code="BUDGET_LIMIT_EXCEEDED",
                        )
            template.amount = updated_domain.amount
            template.type = updated_domain.type
            template.category_id = updated_domain.category_id
            template.note = updated_domain.note
            template.next_run_date = updated_domain.next_run_date
            template.is_active = updated_domain.is_active

            await self.uow.session.flush()
            await self.uow.session.refresh(template)
            return RecurringTransactionResponse.model_validate(template)

    async def delete_template(
        self,
        household_id: int,
        template_id: int,
        user_id: int,
        user_role: HouseholdRole,
    ) -> None:
        if user_role != HouseholdRole.OWNER:
            raise ForbiddenError(
                message="Only the household owner can delete recurring templates",
                error_code="OWNER_PERMISSION_REQUIRED",
            )
        async with self.uow:
            deleted = await self.uow.recurring_transactions.delete_template(
                household_id, template_id
            )
            if not deleted:
                raise NotFoundError(
                    message=f"Recurring template with ID {template_id} not found",
                    error_code="RECURRING_TEMPLATE_NOT_FOUND",
                )

    async def process_single_template(self, template_id: int) -> None:
        next_date = None

        async with self.uow:
            template = await self.uow.recurring_transactions.get_by_id(template_id)

            if not template or not template.is_active:
                return

            now = datetime.now(UTC)
            if template.next_run_date > now:
                return

            tx_domain = TransactionDomain(
                amount=template.amount,
                household_id=template.household_id,
                created_by=template.created_by,
                type=template.type,
                category_id=template.category_id,
                note=template.note,
                date=template.next_run_date,
            )
            await self.uow.transactions.insert_transaction(tx_domain)

            next_date = template.next_run_date + timedelta(days=1)
            await self.uow.recurring_transactions.update_next_run_date(
                template, next_date
            )
        if next_date is not None:
            from app.worker import process_recurring_template_actor

            delay_seconds = (next_date - datetime.now(UTC)).total_seconds()
            process_recurring_template_actor.send_with_options(
                args=(template.id,), delay=int(delay_seconds * 1000)
            )
