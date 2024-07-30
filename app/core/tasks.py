import datetime

from app.services.data_export import DataExportService
from app.services.notification import NotificationService
from app.uow.unitofwork import UnitOfWork


async def notification_task():
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
    message = f"You didn't complete available quiz: {quiz_id}. Please complete it in next 24h!"

    await NotificationService.send_one_notification(uow, user_id, company_id, message)
