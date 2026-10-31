from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import (
    Budget,
    Category,
    Household,
    HouseholdMember,
    HouseholdRole,
    JobStatus,
    ReportJob,
    User,
)
from app.security import create_access_token, hash_password
from app.worker import process_report_actor


@pytest.fixture
async def report_endpoint_env(db_session: AsyncSession) -> dict:
    owner = User(
        email="report_ep_owner@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Report Endpoint Owner",
        is_active=True,
    )
    member = User(
        email="report_ep_member@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Report Endpoint Member",
        is_active=True,
    )
    viewer = User(
        email="report_ep_viewer@example.com",
        password_hash=hash_password("StrongPassword123!"),
        name="Report Endpoint Viewer",
        is_active=True,
    )
    db_session.add_all([owner, member, viewer])
    await db_session.commit()
    await db_session.refresh(owner)
    await db_session.refresh(member)
    await db_session.refresh(viewer)

    household_main = Household(name="Report Main Household")
    household_foreign = Household(name="Report Foreign Household")
    db_session.add_all([household_main, household_foreign])
    await db_session.commit()
    await db_session.refresh(household_main)
    await db_session.refresh(household_foreign)

    db_session.add_all(
        [
            HouseholdMember(
                user_id=owner.id,
                household_id=household_main.id,
                role=HouseholdRole.OWNER,
            ),
            HouseholdMember(
                user_id=member.id,
                household_id=household_main.id,
                role=HouseholdRole.MEMBER,
            ),
            HouseholdMember(
                user_id=viewer.id,
                household_id=household_main.id,
                role=HouseholdRole.VIEWER,
            ),
        ]
    )

    category = Category(
        name="Utilities",
        budget=Budget(goal=2000000),
        household_id=household_main.id,
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    pending_job = ReportJob(
        household_id=household_main.id,
        requested_by=owner.id,
        status=JobStatus.PENDING,
        filters=None,
    )
    db_session.add(pending_job)
    await db_session.commit()
    await db_session.refresh(pending_job)

    return {
        "owner_token": create_access_token(subject=str(owner.id)),
        "member_token": create_access_token(subject=str(member.id)),
        "viewer_token": create_access_token(subject=str(viewer.id)),
        "household_id": household_main.id,
        "foreign_household_id": household_foreign.id,
        "category_id": category.id,
        "pending_job_id": pending_job.id,
    }


@pytest.mark.asyncio
class TestReportEndpoints:
    async def test_post_report_accepted(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['owner_token']}"}
        payload = {
            "filters": {
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "type": "expense",
                "category_id": report_endpoint_env["category_id"],
            }
        }

        with patch.object(process_report_actor, "send") as mock_send:
            response = await async_client_with_redis.post(
                f"/api/v1/households/{report_endpoint_env['household_id']}/reports/",
                json=payload,
                headers=headers,
            )

            assert response.status_code == 202
            data = response.json()
            assert "id" in data
            assert data["status"] == "pending"
            assert mock_send.called
            mock_send.assert_called_once_with(data["id"])

    async def test_post_report_invalid_date_range(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['owner_token']}"}
        payload = {
            "filters": {
                "start_date": "2026-12-31",
                "end_date": "2026-01-01",
            }
        }

        response = await async_client_with_redis.post(
            f"/api/v1/households/{report_endpoint_env['household_id']}/reports/",
            json=payload,
            headers=headers,
        )

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] in ("VALIDATION_ERROR", "INVALID_DATE_RANGE")

    async def test_post_report_viewer_role(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['viewer_token']}"}
        payload = {"filters": {"type": "expense"}}

        with patch.object(process_report_actor, "send"):
            response = await async_client_with_redis.post(
                f"/api/v1/households/{report_endpoint_env['household_id']}/reports/",
                json=payload,
                headers=headers,
            )

        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "pending"

    async def test_get_report_status_success(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['owner_token']}"}
        job_id = report_endpoint_env["pending_job_id"]

        response = await async_client_with_redis.get(
            f"/api/v1/households/{report_endpoint_env['household_id']}/reports/{job_id}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
        assert data["status"] == "pending"

    async def test_get_report_status_cross_user_forbidden(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['member_token']}"}
        job_id = report_endpoint_env["pending_job_id"]

        response = await async_client_with_redis.get(
            f"/api/v1/households/{report_endpoint_env['household_id']}/reports/{job_id}",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "REPORT_NOT_FOUND"

    async def test_get_report_status_forbidden_other_household(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['owner_token']}"}
        job_id = report_endpoint_env["pending_job_id"]

        response = await async_client_with_redis.get(
            f"/api/v1/households/{report_endpoint_env['foreign_household_id']}/reports/{job_id}",
            headers=headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error_code"] == "HOUSEHOLD_NOT_FOUND"

    async def test_get_report_status_file_path_is_null(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['owner_token']}"}
        job_id = report_endpoint_env["pending_job_id"]

        response = await async_client_with_redis.get(
            f"/api/v1/households/{report_endpoint_env['household_id']}/reports/{job_id}",
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_path"] is None
        assert data["status"] == "pending"

    async def test_report_endpoints_unauthorized(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
    ) -> None:
        job_id = report_endpoint_env["pending_job_id"]
        hh_id = report_endpoint_env["household_id"]

        res_post = await async_client_with_redis.post(
            f"/api/v1/households/{hh_id}/reports/",
            json={"filters": {"type": "expense"}},
        )
        assert res_post.status_code == 401
        assert res_post.headers.get("WWW-Authenticate") == "Bearer"

        res_get = await async_client_with_redis.get(
            f"/api/v1/households/{hh_id}/reports/{job_id}",
        )
        assert res_get.status_code == 401
        assert res_get.headers.get("WWW-Authenticate") == "Bearer"

    @pytest.mark.parametrize("invalid_id", [0, -1, -5])
    async def test_report_endpoints_invalid_path_params(
        self,
        async_client_with_redis: AsyncClient,
        report_endpoint_env: dict,
        invalid_id: int,
    ) -> None:
        headers = {"Authorization": f"Bearer {report_endpoint_env['owner_token']}"}
        hh_id = report_endpoint_env["household_id"]
        job_id = report_endpoint_env["pending_job_id"]

        res_post = await async_client_with_redis.post(
            f"/api/v1/households/{invalid_id}/reports/",
            json={"filters": {"type": "expense"}},
            headers=headers,
        )
        assert res_post.status_code == 422
        assert res_post.json()["error_code"] == "VALIDATION_ERROR"

        res_get_hh = await async_client_with_redis.get(
            f"/api/v1/households/{invalid_id}/reports/{job_id}",
            headers=headers,
        )
        assert res_get_hh.status_code == 422
        assert res_get_hh.json()["error_code"] == "VALIDATION_ERROR"

        res_get_job = await async_client_with_redis.get(
            f"/api/v1/households/{hh_id}/reports/{invalid_id}",
            headers=headers,
        )
        assert res_get_job.status_code == 422
        assert res_get_job.json()["error_code"] == "VALIDATION_ERROR"
