import pytest

from app.db.database import Category, Household
from app.dependencies import (
    get_category_repo,
    get_category_service,
)
from app.errors.exceptions import NotFoundError
from app.schemas import CategoryCreate, CategoryUpdate


@pytest.fixture
def category_service(db_session):
    repo = get_category_repo(db_session)
    return get_category_service(repo)


@pytest.fixture
async def seed_household(db_session) -> Household:
    household = Household(name="Our Family")
    db_session.add(household)
    await db_session.flush()
    return household


@pytest.fixture
async def seed_category(db_session, seed_household) -> Category:
    category = Category(
        name="Groceries",
        budget_goal=5000,
        household_id=seed_household.id,
    )
    db_session.add(category)
    await db_session.flush()
    return category


class TestCategoryService:
    async def test_create_category_success(self, category_service, seed_household):
        payload = CategoryCreate(name="Foods", budget_goal=5000)

        response = await category_service.add_category(
            household_id=seed_household.id,
            category=payload,
        )

        assert response.id is not None
        assert response.name == "Foods"
        assert response.budget_goal == 5000

    async def test_edit_category_full_update(self, category_service, seed_category):
        payload = CategoryUpdate(name="Clothes", budget_goal=4000)

        response = await category_service.edit_category(
            seed_category.household_id,
            seed_category.id,
            payload,
        )

        assert response.id == seed_category.id
        assert response.name == "Clothes"
        assert response.budget_goal == 4000

    async def test_edit_category_partial_update(self, category_service, seed_category):
        payload = CategoryUpdate(name="Clothes")

        response = await category_service.edit_category(
            seed_category.household_id,
            seed_category.id,
            payload,
        )

        assert response.id == seed_category.id
        assert response.name == "Clothes"

    async def test_edit_category_not_found(self, category_service, seed_category):

        payload = CategoryUpdate(name="Clothes")
        with pytest.raises(NotFoundError) as exc_info:
            await category_service.edit_category(
                seed_category.household_id,
                999_999,
                payload,
            )
        assert exc_info.value.error_code == "CATEGORY_NOT_FOUND"

    async def test_delete_category_success(
        self, category_service, seed_category, seed_household
    ):
        await category_service.delete_category(
            seed_category.household_id,
            seed_category.id,
        )

    async def test_delete_category_not_found(
        self, category_service, seed_category, seed_household
    ):
        await category_service.delete_category(
            seed_category.household_id,
            999_999,
        )

    async def test_get_category_success(self, category_service, seed_category):
        assert await category_service.get_category(
            seed_category.household_id,
            seed_category.id,
        )

    async def test_get_category_not_found(self, category_service, seed_category):
        assert await category_service.get_category(
            seed_category.household_id,
            999_999,
        )

    async def test_get_all_categories_success(
        self, category_service, seed_household, db_session
    ):

        cat_1 = Category(household_id=seed_household.id, name="Food", budget_goal=5000)
        cat_2 = Category(
            household_id=seed_household.id, name="Clothes", budget_goal=2000
        )

        db_session.add_all([cat_1, cat_2])
        await db_session.flush()

        results = await category_service.get_all_categories(seed_household.id)

        assert len(results) == 2
        category_ids = [c.id for c in results]
        assert cat_1.id in category_ids
        assert cat_2.id in category_ids
