from fastapi import Request

from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException, UpdatingException
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationsListResponse,
    NotificationBase,
    NotificationResponse,
)
from app.uow.unitofwork import UnitOfWork, IUnitOfWork
from app.utils.user import get_pagination_urls


class NotificationService:
    """
    Service for handling notifications within a company.

    This service provides functionalities for sending, receiving, and managing notifications for company members.
    It supports sending notifications to all members or individual members, marking notifications as read, and
    retrieving notifications with pagination.

    Methods:
        - send_notifications: Sends notifications to all members of the specified company.
        - send_one_notification: Sends a notification to a specific member of the company.
        - mark_as_read: Marks a specific notification as read.
        - mark_all_as_read: Marks all notifications for a specific user as read.
        - get_notifications: Retrieves a list of notifications for a specific user with pagination.
        - get_notification_by_id: Retrieves a specific notification by its ID for a specific user.
    """

    @staticmethod
    async def send_notifications(uow: UnitOfWork, company_id: int, message: str):
        """
        Sends notifications to all members of the specified company.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for database operations.
            company_id (int): The ID of the company to send notifications to.
            message (str): The message to send in the notifications.
        """
        members = await uow.member.find_all_by_company_and_role(
            company_id=company_id, role=3
        )

        notifications = [
            NotificationCreate(
                message=message,
                receiver_id=member.user_id,
                company_id=company_id,
                status="pending",
            )
            for member in members
        ]

        for notification in notifications:
            await uow.notification.add_one(notification.model_dump(exclude={"id"}))

    @staticmethod
    async def send_one_notification(
        uow: UnitOfWork, user_id: int, company_id: int, message: str
    ):
        """
        Sends a notification to a specific member of the company.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for database operations.
            user_id (int): The ID of the user to receive the notification.
            company_id (int): The ID of the company.
            message (str): The message to send in the notification.
        """
        notification = NotificationCreate(
            message=message,
            receiver_id=user_id,
            company_id=company_id,
            status="pending",
        )

        await uow.notification.add_one(notification.model_dump(exclude={"id"}))
        await uow.commit()

    @staticmethod
    async def mark_as_read(uow: UnitOfWork, user_id: int, notification_id: int) -> None:
        """
        Marks a specific notification as read.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for database operations.
            user_id (int): The ID of the user marking the notification as read.
            notification_id (int): The ID of the notification to mark as read.

        Raises:
            NotFoundException: If the notification is not found.
            UnAuthorizedException: If the user does not have permissions.
            UpdatingException: If the notification has already been marked as read.
        """
        notification = await NotificationService._validate_notification(
            uow, user_id, notification_id
        )
        await uow.notification.edit_one(notification.id, {"status": "read"})

    @staticmethod
    async def _validate_notification(
        uow: UnitOfWork, user_id: int, notification_id: int
    ) -> Notification:
        """
        Validates the existence and permissions for a notification.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for database operations.
            user_id (int): The ID of the user.
            notification_id (int): The ID of the notification to validate.

        Returns:
            Notification: The validated notification object.

        Raises:
            NotFoundException: If the notification is not found.
            UnAuthorizedException: If the user does not have permissions.
            UpdatingException: If the notification is already marked as read.
        """
        notification = await uow.notification.find_one(id=notification_id)

        if not notification:
            logger.error(f"Notification with ID {notification_id} not found.")
            raise NotFoundException()

        if notification.receiver_id != user_id:
            logger.error(f"You didn't have permissions for this notification.")
            raise UnAuthorizedException()

        if notification.status == "read":
            logger.error(f"You already marked this notification")
            raise UpdatingException()

        return notification

    @staticmethod
    async def mark_all_as_read(uow: UnitOfWork, user_id: int) -> None:
        """
        Marks all notifications for a specific user as read.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for database operations.
            user_id (int): The ID of the user whose notifications will be marked as read.
        """
        notifications = await uow.notification.find_all_by_receiver(receiver_id=user_id)

        for notification in notifications:
            await uow.notification.edit_one(notification.id, {"status": "read"})

    @staticmethod
    async def get_notifications(
        uow: IUnitOfWork, request: Request, user_id: int, skip: int = 0, limit: int = 10
    ) -> NotificationsListResponse:
        """
        Retrieves a list of notifications for a specific user with pagination.

        Args:
            uow (IUnitOfWork): The UnitOfWork instance for database operations.
            request (Request): The FastAPI request object for pagination.
            user_id (int): The ID of the user to retrieve notifications for.
            skip (int): The number of notifications to skip (pagination).
            limit (int): The maximum number of notifications to retrieve (pagination).

        Returns:
            NotificationsListResponse: The response containing the list of notifications and pagination links.
        """
        async with uow:
            notifications = await uow.notification.find_all_by_receiver(
                receiver_id=user_id, skip=skip, limit=limit
            )

            total_notifications = await uow.notification.count_all_by_receiver(
                receiver_id=user_id
            )
            links = get_pagination_urls(request, skip, limit, total_notifications)

            return NotificationsListResponse(
                links=links,
                notifications=[
                    NotificationBase(**notification.__dict__)
                    for notification in notifications
                ],
                total=total_notifications,
            )

    @staticmethod
    async def get_notification_by_id(
        uow: IUnitOfWork, user_id: int, notification_id: int
    ) -> NotificationResponse:
        """
        Retrieves a specific notification by its ID for a specific user.

        Args:
            uow (IUnitOfWork): The UnitOfWork instance for database operations.
            user_id (int): The ID of the user retrieving the notification.
            notification_id (int): The ID of the notification to retrieve.

        Returns:
            NotificationResponse: The response containing the notification details.

        Raises:
            NotFoundException: If the notification is not found or does not belong to the user.
        """
        async with uow:
            notification = await uow.notification.find_one(
                id=notification_id, receiver_id=user_id
            )

            if not notification:
                raise NotFoundException()

            return notification
