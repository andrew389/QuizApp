from app.core.logger import logger
from app.exceptions.auth import UnAuthorizedException
from app.exceptions.base import NotFoundException, UpdatingException
from app.schemas.notification import (
    NotificationCreate,
    NotificationsListResponse,
    NotificationBase,
    NotificationResponse,
)
from app.uow.unitofwork import UnitOfWork, IUnitOfWork


class NotificationService:
    @staticmethod
    async def send_notifications(uow: UnitOfWork, company_id: int, message: str):
        """
        Send notifications to all members of the specified company.
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
            await uow.notification.add_one(notification.dict(exclude={"id"}))
            await uow.commit()

    @staticmethod
    async def send_one_notification(
        uow: UnitOfWork, user_id: int, company_id: int, message: str
    ):
        """
        Send notification from to a specific member of the company.
        """

        notification = NotificationCreate(
            message=message,
            receiver_id=user_id,
            company_id=company_id,
            status="pending",
        )

        await uow.notification.add_one(notification.dict(exclude={"id"}))
        await uow.commit()

    @staticmethod
    async def mark_as_read(uow: UnitOfWork, user_id: int, notification_id: int) -> None:
        """
        Mark a notification as read.
        """
        notification = await uow.notification.find_one(id=notification_id)

        if notification.receiver_id != user_id:
            logger.error(f"You didn't have permissions for this notification.")
            raise UnAuthorizedException()

        if notification.status == "read":
            logger.error(f"You already marked this notification")
            raise UpdatingException()

        if not notification:
            logger.error(f"Notification with ID {notification_id} not found.")
            raise NotFoundException()

        await uow.notification.edit_one(notification_id, {"status": "read"})
        await uow.commit()

    @staticmethod
    async def get_notifications(
        uow: IUnitOfWork, user_id: int, skip: int = 0, limit: int = 10
    ) -> NotificationsListResponse:
        """
        Retrieves a list of notifications for a specific user with pagination.
        """
        async with uow:
            notifications = await uow.notification.find_all_by_receiver(
                receiver_id=user_id, skip=skip, limit=limit
            )
            return NotificationsListResponse(
                notifications=[
                    NotificationBase(**notification.__dict__)
                    for notification in notifications
                ],
                total=len(notifications),
            )

    @staticmethod
    async def get_notification_by_id(
        uow: IUnitOfWork, user_id: int, notification_id: int
    ) -> NotificationResponse:
        """
        Retrieves a specific notification by its ID for a specific user.
        """
        async with uow:
            notification = await uow.notification.find_one(
                id=notification_id, receiver_id=user_id
            )

            if not notification:
                raise NotFoundException()

            return notification
