import asyncio

from app.db.database import Household, HouseholdMember, HouseholdRole, async_db_session


async def setup_shared_household() -> int:
    async with async_db_session() as session:
        shared_household = Household(
            name="Shared Family Household",
            is_personal=False,
        )
        session.add(shared_household)
        await session.flush()

        membership_user_1 = HouseholdMember(
            user_id=1,
            household_id=shared_household.id,
            role=HouseholdRole.OWNER,
        )

        membership_user_2 = HouseholdMember(
            user_id=2,
            household_id=shared_household.id,
            role=HouseholdRole.MEMBER,
        )

        session.add_all([membership_user_1, membership_user_2])
        await session.commit()

        print(f"Household ID: {shared_household.id}")
        print("User 1 Role: OWNER")
        print("User 2 Role: MEMBER")

        return shared_household.id


if __name__ == "__main__":
    asyncio.run(setup_shared_household())
