from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Depends, status, Query, Request

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
    Authenticate user and return an access token.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        form_data (SignInRequest): The email and password for authentication.
        auth_service (AuthServiceDep): Service for authentication operations.

    Returns:
        Token: An access token and its expiration details.

    Raises:
        AuthenticationException: If authentication fails.
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
    Retrieve the current user's information.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        UserResponse: The details of the current user.
    """
    return UserResponse(user=current_user)


@router.get("/invites", response_model=InvitationsListResponse)
async def get_new_invitations(
    uow: UOWDep,
    request: Request,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieve new invitations for the current user.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        request (Request): The HTTP request object.
        invitation_service (InvitationServiceDep): Service for invitation operations.
        current_user (User): The currently authenticated user.
        skip (int): Number of invitations to skip (default is 0).
        limit (int): Maximum number of invitations to return (default is 10).

    Returns:
        InvitationsListResponse: A list of new invitations.

    Raises:
        FetchingException: If an error occurs while fetching invitations.
    """
    try:
        invitations = await invitation_service.get_invitations(
            uow, current_user.id, request, skip=skip, limit=limit
        )
        return invitations
    except Exception as e:
        logger.error(f"Error fetching invitations: {e}")
        raise FetchingException()


@router.get("/requests", response_model=InvitationsListResponse)
async def get_sent_invitations(
    uow: UOWDep,
    request: Request,
    invitation_service: InvitationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieve sent invitations by the current user.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        request (Request): The HTTP request object.
        invitation_service (InvitationServiceDep): Service for invitation operations.
        current_user (User): The currently authenticated user.
        skip (int): Number of invitations to skip (default is 0).
        limit (int): Maximum number of invitations to return (default is 10).

    Returns:
        InvitationsListResponse: A list of sent invitations.

    Raises:
        FetchingException: If an error occurs while fetching sent invitations.
    """
    try:
        invitations = await invitation_service.get_sent_invitations(
            uow, current_user.id, request, skip=skip, limit=limit
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
    Retrieve the average score of the user across the system.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        analytics_service (AnalyticsServiceDep): Service for analytics operations.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A dictionary with the average score.

    Raises:
        CalculatingException: If an error occurs while calculating the average score.
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
    Retrieve quiz results for the current user for the last 48 hours.

    Args:
        data_export_service (DataExportServiceDep): Service for data export operations.
        current_user (User): The currently authenticated user.
        is_csv (bool): Whether to export results as a CSV file (default is False).

    Returns:
        Response: The quiz results in the requested format.

    Raises:
        FetchingException: If an error occurs while fetching quiz results.
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
    Retrieve timestamps of the last completion of quizzes by the current user.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        analytics_service (AnalyticsServiceDep): Service for analytics operations.
        current_user (User): The currently authenticated user.

    Returns:
        Dict[int, datetime]: A dictionary with quiz IDs and their last completion timestamps.

    Raises:
        FetchingException: If an error occurs while fetching completion timestamps.
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
    Retrieve average scores for each quiz taken by the current user within the specified time range.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        analytics_service (AnalyticsServiceDep): Service for analytics operations.
        current_user (User): The currently authenticated user.
        start_date (datetime): The start date of the time range.
        end_date (datetime): The end date of the time range.

    Returns:
        Dict[int, float]: A dictionary with quiz IDs and their average scores.

    Raises:
        CalculatingException: If an error occurs while calculating average scores.
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
    Mark a specific notification as read for the current user.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        notification_id (int): The ID of the notification to mark as read.
        notification_service (NotificationServiceDep): Service for notification operations.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A confirmation message.

    Raises:
        UpdatingException: If an error occurs while marking the notification as read.
    """
    try:
        await notification_service.mark_as_read(uow, current_user.id, notification_id)
        return {"msg": "Notification marked as read."}
    except Exception as e:
        logger.error(f"{e}")
        raise UpdatingException()


@router.post("/notifications/read")
async def mark_all_notifications_as_read(
    uow: UOWDep,
    notification_service: NotificationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Mark all notifications as read for the current user.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        notification_service (NotificationServiceDep): Service for notification operations.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A confirmation message.

    Raises:
        UpdatingException: If an error occurs while marking all notifications as read.
    """
    try:
        await notification_service.mark_all_as_read(uow, current_user.id)
        return {"msg": "Notifications marked as read."}
    except Exception as e:
        logger.error(f"{e}")
        raise UpdatingException()


@router.get("/notifications", response_model=NotificationsListResponse)
async def get_notifications(
    uow: UOWDep,
    request: Request,
    notification_service: NotificationServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieve a list of notifications for the current user.

    Args:
        uow (UOWDep): Unit of Work dependency for database operations.
        request (Request): The HTTP request object.
        notification_service (NotificationServiceDep): Service for notification operations.
        current_user (User): The currently authenticated user.
        skip (int): Number of notifications to skip (default is 0).
        limit (int): Maximum number of notifications to return (default is 10).

    Returns:
        NotificationsListResponse: A list of notifications.

    Raises:
        FetchingException: If an error occurs while fetching notifications.
    """
    try:
        return await notification_service.get_notifications(
            uow, request, current_user.id, skip, limit
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
    Retrieve a specific notification by its ID for the current user.

    Args:
        notification_id (int): The ID of the notification to retrieve.
        uow (UOWDep): Unit of Work dependency for database operations.
        notification_service (NotificationServiceDep): Service for notification operations.
        current_user (User): The currently authenticated user.

    Returns:
        NotificationResponse: The details of the notification.

    Raises:
        FetchingException: If an error occurs while fetching the notification.
    """
    try:
        notification = await notification_service.get_notification_by_id(
            uow, current_user.id, notification_id
        )
        return notification
    except Exception as e:
        logger.error(f"{e}")
        raise FetchingException()
