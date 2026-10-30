from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import FileResponse

from app.dependencies import CurrentUser, RequireRole, get_report_service
from app.schemas import ReportExportRequest, ReportJobResponse
from app.service import ReportJobsService
from app.worker import process_report_actor

router = APIRouter()


@router.post(
    "/",
    summary="Request a new report",
    description="Enqueue a background job to generate a CSV report for a household.",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(RequireRole())],
)
async def create_report(
    household_id: Annotated[int, Path(gt=0)],
    request: ReportExportRequest,
    current_user: CurrentUser,
    service: Annotated[ReportJobsService, Depends(get_report_service)],
) -> ReportJobResponse:
    response = await service.create_job(
        household_id=household_id,
        user_id=current_user.id,
        filters=request.filters,
    )
    process_report_actor.send(response.id)
    return response


@router.get(
    "/{job_id}",
    summary="Get report status",
    description="Poll the status of a report generation job.",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(RequireRole())],
)
async def get_report_status(
    household_id: Annotated[int, Path(gt=0)],
    job_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: Annotated[ReportJobsService, Depends(get_report_service)],
) -> ReportJobResponse:
    return await service.get_job_status(
        household_id=household_id,
        job_id=job_id,
        user_id=current_user.id,
    )


@router.get(
    "/{job_id}/download",
    summary="Download report file",
    description="Downlaod the generated CSV report file. Only the requester can download",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
)
async def downaload_report(
    household_id: Annotated[int, Path(gt=0)],
    job_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    service: Annotated[ReportJobResponse, Depends(get_report_service)],
):
    file_path = await service.get_report_file_path(
        household_id=household_id,
        job_id=job_id,
        user_id=current_user.id,
    )
    return FileResponse(
        path=file_path,
        filename=f"report_{job_id}.csv",
        media_type="text/csv",
    )
