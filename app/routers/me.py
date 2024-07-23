from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, status, Query

from app.core.dependencies import (
    UOWDep,
    AuthServiceDep,
    InvitationServiceDep,
    DataExportServiceDep,
    AnalyticsServiceDep,
    NotificationServiceDep,
)
from app.core.logger import logger
from app.exceptions.base import (
    FetchingException,
    CalculatingException,
    UpdatingException,
)
from app.models.user import User
from app.schemas.invitation import InvitationsListResponse
from app.schemas.notification import NotificationsListResponse, NotificationResponse
from app.schemas.token import Token
from app.schemas.user import UserResponse, SignInRequest
from app.exceptions.auth import AuthenticationException

router = APIRouter(prefix="/me", tags=["Me"])


@router.post("/login", response_model=Token)
async def login(uow: UOWDep, form_data: SignInRequest, auth_service: AuthServiceDep):
    """
    Authenticate user and return access token.
    """
    user = await auth_service.authenticate_user(
        uow, form_data.email, form_data.password
    )
    if not user:
        raise AuthenticationException()
    access_token, expiration = auth_service.create_access_token(
        data={"email": user.email}
    )
    return Token(access_token=access_token, token_type="bearer", expiration=expiration)


@router.get("/", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_info(current_user: User = Depends(AuthServiceDep.get_current_user)):
    """
    Get the current user's information.
    """
    return UserResponse(user=current_user)


@router.get("/invites", response_model=InvitationsListResponse)
async def get_new_invitations(
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Get new invitations for the current user.
    """
    try:
        invitations = await invitation_service.get_invitations(
            uow, current_user.id, skip=skip, limit=limit
        )
        return invitations
    except Exception as e:
        logger.error(f"Error fetching invitations: {e}")
        raise FetchingException()


@router.get("/requests", response_model=InvitationsListResponse)
async def get_sent_invitations(
    uow: UOWDep,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Get sent invitations by the current user.
    """
    try:
        invitations = await invitation_service.get_sent_invitations(
            uow, current_user.id, skip=skip, limit=limit
        )
        return invitations
    except Exception as e:
        logger.error(f"Error fetching invitations for owner: {e}")
        raise FetchingException()


@router.get("/quizzes/score/system", status_code=200, response_model=dict)
async def get_avg_score_across_system(
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Get average score of user across system
    """
    try:
        avg_score = await analytics_service.calculate_average_score_across_system(
            uow, current_user.id
        )
        return {"average_score": avg_score}
    except Exception:
        raise CalculatingException()


@router.get("/results")
async def get_quiz_results_for_last_48h(
    data_export_service: DataExportServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    is_csv: bool = Query(),
):
    """
    Get quiz results for the current user for the last 48 hours.
    """
    try:
        return await data_export_service.read_data_by_user_id(is_csv, current_user.id)
    except Exception as e:
        logger.error(f"Error fetching results for user: {e}")
        raise FetchingException()


@router.get("/quizzes/score/last-completion", response_model=Dict[int, datetime])
async def get_quiz_completion_timestamps(
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Get a list of quizzes with the timestamps of their last completion by the current user.
    """
    try:
        timestamps = await analytics_service.get_last_completion_timestamps(
            uow, current_user.id
        )
        return timestamps
    except Exception as e:
        logger.error(f"Error fetching quiz completion timestamps: {e}")
        raise FetchingException()


@router.get("/quizzes/score/all", response_model=Dict[int, float])
async def get_average_scores_by_quiz(
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    start_date: datetime = Query(..., alias="start_date"),
    end_date: datetime = Query(..., alias="end_date"),
):
    """
    Get average scores for each quiz taken by the current user within the specified time range.
    """
    try:
        average_scores = await analytics_service.calculate_average_scores_by_quiz(
            uow, current_user.id, start_date, end_date
        )
        return average_scores
    except Exception as e:
        logger.error(f"Error calculating average scores by quiz: {e}")
        raise CalculatingException()


@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    uow: UOWDep,
    notification_id: int,
    notification_service: NotificationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Marks a specific notification as read for the current user.
    """
    try:
        await notification_service.mark_as_read(uow, current_user.id, notification_id)
        return {"msg": "Notification marked as read."}
    except Exception as e:
        logger.error(f"{e}")
        raise UpdatingException()


@router.get("/notifications", response_model=NotificationsListResponse)
async def get_notifications(
    uow: UOWDep,
    notification_service: NotificationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieves a list of notifications for the current user.
    """
    try:
        return await notification_service.get_notifications(
            uow, current_user.id, skip, limit
        )
    except Exception as e:
        logger.error(f"{e}")
        raise FetchingException()


@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification_by_id(
    notification_id: int,
    uow: UOWDep,
    notification_service: NotificationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Retrieves a specific notification by its ID for the current user.
    """
    try:
        notification = await notification_service.get_notification_by_id(
            uow, current_user.id, notification_id
        )
        return notification
    except Exception as e:
        logger.error(f"{e}")
        raise FetchingException()
