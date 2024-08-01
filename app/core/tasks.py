import datetime

from app.services.data_export import DataExportService
from app.services.notification import NotificationService
from app.uow.unitofwork import UnitOfWork


async def notification_task():
    """
    Task to send notifications to users who haven't completed quizzes in the last 24 hours.

    This function retrieves all companies, and for each company, it finds users and quizzes.
    It then checks if the user has completed the quizzes by fetching relevant data.
    If no data is found or the data is outdated, a notification is sent to the user.
    """
    uow = UnitOfWork()
    async with uow:

        current_time = datetime.datetime.now()
        cutoff_time = current_time - datetime.timedelta(days=1)

        companies = await uow.company.find_all()

        for company in companies:
            company_id = company.id

            users = await uow.member.find_all_by_company(company_id=company_id)

            for user in users:
                user_id = user.user_id
                quizzes = await uow.quiz.find_all_by_company(company_id=company_id)

                for quiz in quizzes:
                    quiz_id = quiz.id
                    pattern = f"answered_quiz_{user_id}_{company_id}_{quiz_id}"

                    all_data = await DataExportService.fetch_data(pattern)

                    if not all_data:
                        await send_notification(uow, user_id, quiz_id, company_id)

                    for data in all_data:
                        timestamp = datetime.datetime.fromisoformat(data["timestamp"])

                        if timestamp >= cutoff_time:
                            await send_notification(uow, user_id, quiz_id, company_id)


async def send_notification(
    uow: UnitOfWork, user_id: int, quiz_id: int, company_id: int
):
    """
    Sends a notification to a user about an incomplete quiz.

    Args:
        uow (UnitOfWork): The unit of work instance used for database operations.
        user_id (int): The identifier of the user to notify.
        quiz_id (int): The identifier of the quiz related to the notification.
        company_id (int): The identifier of the company associated with the notification.
    """
    message = f"You didn't complete available quiz: {quiz_id}. Please complete it in next 24h!"

    await NotificationService.send_one_notification(uow, user_id, company_id, message)
