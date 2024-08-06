from datetime import datetime
from typing import Dict

from fastapi import APIRouter, Query, Request

from app.core.dependencies import (
    UOWDep,
    CompanyServiceDep,
    InvitationServiceDep,
    QuizServiceDep,
    MemberManagementDep,
    MemberRequestsDep,
    MemberQueriesDep,
    AnsweredQuestionServiceDep,
    DataExportServiceDep,
    AnalyticsServiceDep,
    CurrentUserDep,
)
from app.exceptions.base import (
    UpdatingException,
    DeletingException,
    FetchingException,
    CreatingException,
    CalculatingException,
)

from app.models.user import User
from app.schemas.answered_question import SendAnsweredQuiz
from app.schemas.company import (
    CompanyCreate,
    CompanyDetail,
    CompanyUpdate,
    CompaniesListResponse,
)
from app.core.logger import logger
from app.schemas.invitation import InvitationBase, SendInvitation
from app.schemas.member import (
    MemberBase,
    MembersListResponse,
    MemberRequest,
    AdminsListResponse,
)
from app.schemas.quiz import QuizzesListResponse

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyDetail)
async def add_company(
    company: CompanyCreate,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: CurrentUserDep,
):
    """
    Creates a new company.

    Args:
        company (CompanyCreate): The company data to create.
        uow (UOWDep): Unit of Work dependency.
        company_service (CompanyServiceDep): Company service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        CompanyDetail: The details of the newly created company.

    Raises:
        CreatingException: If there is an error during the creation process.
    """
    try:
        logger.info(f"Received company data: {company}")
        new_company = await company_service.add_company(
            uow, company, owner_id=current_user.id
        )

        logger.info(f"Company created with ID: {new_company.id}")
        return new_company
    except Exception as e:
        logger.error(f"Error creating company: {e}")
        raise CreatingException()


@router.get("/", response_model=CompaniesListResponse)
async def get_companies(
    uow: UOWDep,
    request: Request,
    company_service: CompanyServiceDep,
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of companies.

    Args:
        uow (UOWDep): Unit of Work dependency.
        request (Request): Request to get base URL.
        company_service (CompanyServiceDep): Company service dependency.
        current_user (User): The currently authenticated user.
        skip (int): The number of items to skip (pagination).
        limit (int): The maximum number of items to return.

    Returns:
        CompaniesListResponse: The list of companies.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        companies = await company_service.get_companies(
            uow,
            current_user_id=current_user.id,
            request=request,
            skip=skip,
            limit=limit,
        )
        return companies
    except Exception as e:
        logger.error(f"Error fetching companies: {e}")
        raise FetchingException()


@router.get("/{company_id}", response_model=CompanyDetail)
async def get_company_by_id(
    company_id: int,
    uow: UOWDep,
    company_service: CompanyServiceDep,
):
    """
    Retrieves a company by its ID.

    Args:
        company_id (int): The ID of the company to retrieve.
        uow (UOWDep): Unit of Work dependency.
        company_service (CompanyServiceDep): Company service dependency.

    Returns:
        CompanyDetail: The details of the retrieved company.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """

    try:
        company = await company_service.get_company_by_id(uow, company_id)
        logger.info(f"Fetched company with ID: {company_id}")
        return company
    except Exception as e:
        logger.error(f"Error fetching company by ID {company_id}: {e}")
        raise FetchingException()


@router.put("/{company_id}", response_model=CompanyDetail)
async def update_company(
    company_id: int,
    company_update: CompanyUpdate,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: CurrentUserDep,
):
    """
    Updates a company by its ID.

    Args:
        company_id (int): The ID of the company to update.
        company_update (CompanyUpdate): The updated company data.
        uow (UOWDep): Unit of Work dependency.
        company_service (CompanyServiceDep): Company service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        CompanyDetail: The updated company details.

    Raises:
        UpdatingException: If there is an error during the update process.
    """
    try:
        updated_company = await company_service.update_company(
            uow, company_id, current_user.id, company_update
        )
        logger.info(f"Updated company with ID: {company_id}")
        return updated_company
    except Exception as e:
        logger.error(f"Error updating company with ID {company_id}: {e}")
        raise UpdatingException()


@router.delete("/{company_id}", response_model=dict)
async def delete_company(
    company_id: int,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: CurrentUserDep,
):
    """
    Deletes a company by its ID.

    Args:
        company_id (int): The ID of the company to delete.
        uow (UOWDep): Unit of Work dependency.
        company_service (CompanyServiceDep): Company service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A dictionary with a status code indicating success.

    Raises:
        DeletingException: If there is an error during the deletion process.
    """
    try:
        deleted_company_id = await company_service.delete_company(
            uow, company_id, current_user.id
        )
        logger.info(f"Deleted company with ID: {deleted_company_id}")
        return {"status_code": 200}
    except Exception as e:
        logger.error(f"Error deleting company with ID {company_id}: {e}")
        raise DeletingException()


@router.post("/{company_id}/admin/{member_id}", response_model=MemberBase)
async def appoint_admin(
    company_id: int,
    member_id: int,
    uow: UOWDep,
    member_service: MemberManagementDep,
    current_user: CurrentUserDep,
):
    """
    Appoints a member as an admin in a company.

    Args:
        company_id (int): The ID of the company where the admin is to be appointed.
        member_id (int): The ID of the member to be appointed as an admin.
        uow (UOWDep): Unit of Work dependency.
        member_service (MemberManagementDep): Member management service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        MemberBase: The details of the appointed admin.

    Raises:
        CreatingException: If there is an error during the appointment process.
    """
    return await member_service.appoint_admin(
        uow, current_user.id, company_id, member_id
    )


@router.put("/{company_id}/admin/{member_id}", response_model=MemberBase)
async def remove_admin(
    company_id: int,
    member_id: int,
    uow: UOWDep,
    member_service: MemberManagementDep,
    current_user: CurrentUserDep,
):
    """
    Removes a member's admin status in a company.

    Args:
        company_id (int): The ID of the company where the admin status is to be removed.
        member_id (int): The ID of the member whose admin status is to be removed.
        uow (UOWDep): Unit of Work dependency.
        member_service (MemberManagementDep): Member management service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        MemberBase: The details of the member after removing admin status.

    Raises:
        UpdatingException: If there is an error during the removal process.
    """
    return await member_service.remove_admin(
        uow, current_user.id, company_id, member_id
    )


@router.put("/{company_id}/visibility", response_model=CompanyDetail)
async def change_company_visibility(
    company_id: int,
    is_visible: bool,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: CurrentUserDep,
):
    """
    Changes the visibility of a company.

    Args:
        company_id (int): The ID of the company whose visibility is to be changed.
        is_visible (bool): The new visibility status of the company.
        uow (UOWDep): Unit of Work dependency.
        company_service (CompanyServiceDep): Company service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        CompanyDetail: The updated company details.

    Raises:
        UpdatingException: If there is an error during the visibility change process.
    """
    try:
        updated_company = await company_service.change_company_visibility(
            uow, company_id, current_user.id, is_visible
        )
        logger.info(f"Changed visibility for company with ID: {company_id}")
        return updated_company
    except Exception as e:
        logger.error(f"Error changing visibility for company with ID {company_id}: {e}")
        raise UpdatingException()


@router.post("/{company_id}/join", response_model=InvitationBase)
async def request_to_join_company_to_owner(
    company_id: int,
    request: MemberRequest,
    uow: UOWDep,
    member_service: MemberRequestsDep,
    current_user: CurrentUserDep,
):
    """
    Requests to join a company.

    Args:
        company_id (int): The ID of the company to join.
        request (MemberRequest): The details of the member request.
        uow (UOWDep): Unit of Work dependency.
        member_service (MemberRequestsDep): Member requests service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        InvitationBase: The details of the created invitation.

    Raises:
        CreatingException: If there is an error during the request process.
    """
    try:
        invitation = await member_service.request_to_join_company(
            uow, current_user.id, request, company_id
        )
        return invitation
    except Exception as e:
        logger.error(f"Error requesting to join company: {e}")
        raise CreatingException()


@router.post("/{company_id}/invite", response_model=InvitationBase)
async def send_invitation_to_user(
    company_id: int,
    uow: UOWDep,
    invitation_data: SendInvitation,
    invitation_service: InvitationServiceDep,
    current_user: CurrentUserDep,
):
    """
    Sends an invitation to a user to join a company.

    Args:
        company_id (int): The ID of the company sending the invitation.
        invitation_data (SendInvitation): The details of the invitation.
        uow (UOWDep): Unit of Work dependency.
        invitation_service (InvitationServiceDep): Invitation service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        InvitationBase: The details of the sent invitation.

    Raises:
        CreatingException: If there is an error during the invitation process.
    """
    try:
        invitation = await invitation_service.send_invitation(
            uow, invitation_data, current_user.id, company_id
        )
        return invitation
    except Exception as e:
        logger.error(f"{e}")
        raise CreatingException()


@router.get("/{company_id}/members", response_model=MembersListResponse)
async def get_members(
    company_id: int,
    uow: UOWDep,
    request: Request,
    member_service: MemberQueriesDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of members in a company.

    Args:
        company_id (int): The ID of the company whose members are to be retrieved.
        uow (UOWDep): Unit of Work dependency.
        request (Request): The HTTP request object to get base URL.
        member_service (MemberQueriesDep): Member queries service dependency.
        skip (int): The number of items to skip (pagination).
        limit (int): The maximum number of items to return.

    Returns:
        MembersListResponse: The list of members in the company.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        members = await member_service.get_members(
            uow, company_id=company_id, request=request, skip=skip, limit=limit
        )
        return members
    except Exception as e:
        logger.error(f"Error fetching members: {e}")
        raise FetchingException()


@router.get("/{company_id}/members/{member_id}", response_model=MemberBase)
async def get_member_by_id(
    company_id: int,
    member_id: int,
    uow: UOWDep,
    member_service: MemberQueriesDep,
):
    """
    Retrieves a member by their ID.

    Args:
        company_id (int): The ID of the company the member belongs to.
        member_id (int): The ID of the member to retrieve.
        uow (UOWDep): Unit of Work dependency.
        member_service (MemberQueriesDep): Member queries service dependency.

    Returns:
        MemberBase: The details of the member.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        member = await member_service.get_member_by_id(
            uow, member_id=member_id, company_id=company_id
        )
        return member
    except Exception as e:
        logger.error(f"Error fetching members: {e}")
        raise FetchingException()


@router.get("/{company_id}/quizzes", response_model=QuizzesListResponse)
async def get_quizzes(
    company_id: int,
    uow: UOWDep,
    request: Request,
    quiz_service: QuizServiceDep,
    current_user: CurrentUserDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of quizzes for a company.

    Args:
        company_id (int): The ID of the company whose quizzes are to be retrieved.
        uow (UOWDep): Unit of Work dependency.
        request (Request): The HTTP request object to get base URL.
        quiz_service (QuizServiceDep): Quiz service dependency.
        current_user (User): The currently authenticated user.
        skip (int): The number of items to skip (pagination).
        limit (int): The maximum number of items to return.

    Returns:
        QuizzesListResponse: The list of quizzes for the company.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        quizzes_list = await quiz_service.get_quizzes(
            uow,
            company_id=company_id,
            current_user_id=current_user.id,
            request=request,
            skip=skip,
            limit=limit,
        )
        return quizzes_list
    except Exception as e:
        logger.error(f"Error fetching quizzes: {e}")
        raise FetchingException()


@router.post(
    "/{company_id}/quizzes/{quiz_id}/answer", status_code=200, response_model=dict
)
async def submit_quiz_answers(
    quiz_id: int,
    quiz_data: SendAnsweredQuiz,
    uow: UOWDep,
    answered_question_service: AnsweredQuestionServiceDep,
    current_user: CurrentUserDep,
):
    """
    Submits answers for a quiz.

    Args:
        quiz_id (int): The ID of the quiz for which answers are being submitted.
        quiz_data (SendAnsweredQuiz): The submitted quiz answers.
        uow (UOWDep): Unit of Work dependency.
        answered_question_service (AnsweredQuestionServiceDep): Answered question service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A message indicating the successful saving of answers.

    Raises:
        CreatingException: If there is an error during the answer submission process.
    """
    await answered_question_service.save_answered_quiz(
        uow, quiz_data, user_id=current_user.id, quiz_id=quiz_id
    )
    return {"msg": "Answers saved successfully"}


@router.get("/{company_id}/results/{user_id}")
async def get_quiz_results_by_user_id_company_id(
    user_id: int,
    company_id: int,
    is_csv: bool,
    data_export_service: DataExportServiceDep,
    uow: UOWDep,
    current_user: CurrentUserDep,
):
    """
    Get quiz results for a specific user and company.

    Args:
        user_id (int): The ID of the user whose results are to be retrieved.
        company_id (int): The ID of the company where the quiz results are recorded.
        is_csv (bool): Flag indicating whether the results should be exported as a CSV file.
        data_export_service (DataExportServiceDep): Data export service dependency.
        uow (UOWDep): Unit of Work dependency.
        current_user (User): The currently authenticated user.

    Returns:
        The quiz results for the specified user and company, either as JSON or CSV.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        return await data_export_service.read_data_by_user_id_and_company_id(
            uow, is_csv, current_user.id, user_id, company_id
        )
    except Exception as e:
        logger.error(f"Error fetching results for company: {e}")
        raise FetchingException()


@router.get("/{company_id}/results/{quiz_id}")
async def get_results_by_company_id_quiz_id(
    company_id: int,
    quiz_id: int,
    is_csv: bool,
    data_export_service: DataExportServiceDep,
    uow: UOWDep,
    current_user: CurrentUserDep,
):
    """
    Get quiz results for a specific company and quiz.

    Args:
        company_id (int): The ID of the company where the quiz results are recorded.
        quiz_id (int): The ID of the quiz whose results are to be retrieved.
        is_csv (bool): Flag indicating whether the results should be exported as a CSV file.
        data_export_service (DataExportServiceDep): Data export service dependency.
        uow (UOWDep): Unit of Work dependency.
        current_user (User): The currently authenticated user.

    Returns:
        The quiz results for the specified company and quiz, either as JSON or CSV.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        return await data_export_service.read_data_by_company_id_and_quiz_id(
            uow, is_csv, current_user.id, company_id, quiz_id
        )
    except Exception as e:
        logger.error(f"Error fetching results for company: {e}")
        raise FetchingException()


@router.get("/{company_id}/results")
async def get_results_by_company_id(
    company_id: int,
    is_csv: bool,
    data_export_service: DataExportServiceDep,
    uow: UOWDep,
    current_user: CurrentUserDep,
):
    """
    Export quiz results for a specific company.

    Args:
        company_id (int): The ID of the company whose quiz results are to be exported.
        is_csv (bool): Flag indicating whether the results should be exported as a CSV file.
        data_export_service (DataExportServiceDep): Data export service dependency.
        uow (UOWDep): Unit of Work dependency.
        current_user (User): The currently authenticated user.

    Returns:
        The quiz results for the specified company, either as JSON or CSV.

    Raises:
        FetchingException: If there is an error during the export process.
    """
    try:
        return await data_export_service.read_data_by_company_id(
            uow, is_csv, current_user.id, company_id
        )
    except Exception as e:
        logger.error(f"Error fetching results for company: {e}")
        raise FetchingException()


@router.get("/{company_id}/quizzes/score", status_code=200, response_model=dict)
async def get_avg_score_within_company(
    company_id: int,
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    current_user: CurrentUserDep,
):
    """
    Get average score of users within a company.

    Args:
        company_id (int): The ID of the company for which the average score is calculated.
        uow (UOWDep): Unit of Work dependency.
        analytics_service (AnalyticsServiceDep): Analytics service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        dict: A dictionary containing the average score of users within the company.

    Raises:
        CalculatingException: If there is an error during the calculation process.
    """
    try:
        avg_score = await analytics_service.calculate_average_score_within_company(
            uow, current_user.id, company_id
        )
        return {"average_score": avg_score}
    except Exception:
        raise CalculatingException()


@router.get("/{company_id}/quizzes/score/members", response_model=Dict[int, float])
async def get_company_members_average_scores(
    company_id: int,
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    current_user: CurrentUserDep,
    start_date: datetime = Query(..., alias="start_date"),
    end_date: datetime = Query(..., alias="end_date"),
):
    """
    Get average scores for all members of a specified company within the given time range.

    Args:
        company_id (int): The ID of the company for which member average scores are calculated.
        uow (UOWDep): Unit of Work dependency.
        analytics_service (AnalyticsServiceDep): Analytics service dependency.
        current_user (User): The currently authenticated user.
        start_date (datetime): The start date for the time range.
        end_date (datetime): The end date for the time range.

    Returns:
        Dict[int, float]: A dictionary where keys are member IDs and values are their average scores.

    Raises:
        CalculatingException: If there is an error during the calculation process.
    """
    try:
        average_scores = (
            await analytics_service.calculate_company_members_average_scores(
                uow, current_user.id, company_id, start_date, end_date
            )
        )
        return average_scores
    except Exception as e:
        logger.error(f"Error calculating average scores for company members: {e}")
        raise CalculatingException()


@router.get(
    "/{company_id}/quizzes/score/members/last-completion",
    response_model=Dict[int, datetime],
)
async def get_users_last_quiz_attempts(
    company_id: int,
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    current_user: CurrentUserDep,
):
    """
    List all users in a company with the timestamp of their last quiz attempt.

    Args:
        company_id (int): The ID of the company to fetch users' last quiz attempts for.
        uow (UOWDep): Unit of Work dependency.
        analytics_service (AnalyticsServiceDep): Analytics service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        Dict[int, datetime]: A dictionary where keys are user IDs and values are timestamps of their last quiz attempt.

    Raises:
        FetchingException: If there is an error during the retrieval process.
    """
    try:
        last_attempts = await analytics_service.list_users_last_quiz_attempts(
            uow, current_user.id, company_id
        )
        return last_attempts
    except Exception as e:
        logger.error(f"Error fetching users' last quiz attempts: {e}")
        raise FetchingException()


@router.get(
    "/{company_id}/quizzes/score/members/{member_id}", response_model=Dict[int, float]
)
async def get_detailed_average_scores(
    uow: UOWDep,
    analytics_service: AnalyticsServiceDep,
    member_id: int,
    company_id: int,
    current_user: CurrentUserDep,
    start_date: datetime = Query(..., alias="start_date"),
    end_date: datetime = Query(..., alias="end_date"),
):
    """
    Get detailed average scores for each quiz taken by the user within the specified time range.

    Args:
        member_id (int): The ID of the member whose detailed average scores are to be retrieved.
        company_id (int): The ID of the company for which the average scores are calculated.
        uow (UOWDep): Unit of Work dependency.
        analytics_service (AnalyticsServiceDep): Analytics service dependency.
        current_user (User): The currently authenticated user.
        start_date (datetime): The start date for the time range.
        end_date (datetime): The end date for the time range.

    Returns:
        Dict[int, float]: A dictionary where keys are quiz IDs and values are the average scores.

    Raises:
        CalculatingException: If there is an error during the calculation process.
    """
    try:
        detailed_average_scores = (
            await analytics_service.calculate_detailed_average_scores(
                uow, current_user.id, member_id, company_id, start_date, end_date
            )
        )
        return detailed_average_scores
    except Exception as e:
        logger.error(f"Error calculating detailed average scores: {e}")
        raise CalculatingException()


@router.get("/{company_id}/admins", response_model=AdminsListResponse)
async def get_admins(
    uow: UOWDep,
    request: Request,
    member_service: MemberQueriesDep,
    company_id: int,
    skip: int = 0,
    limit: int = 10,
):
    """
    Retrieves a list of admins for a company.

    Args:
        company_id (int): The ID of the company to retrieve admins for.
        uow (UOWDep): Unit of Work dependency.
        request (Request): The HTTP request object.
        member_service (MemberQueriesDep): Member queries service dependency.
        skip (int): Number of records to skip (for pagination).
        limit (int): Maximum number of records to return (for pagination).

    Returns:
        AdminsListResponse: A response object containing the list of admins.
    """
    return await member_service.get_admins(uow, company_id, request, skip, limit)


@router.post("/{member_id}/remove", response_model=MemberBase)
async def remove_member(
    member_id: int,
    uow: UOWDep,
    member_service: MemberManagementDep,
    current_user: CurrentUserDep,
):
    """
    Removes a member from the company.

    Args:
        member_id (int): The ID of the member to be removed.
        uow (UOWDep): Unit of Work dependency.
        member_service (MemberManagementDep): Member management service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        MemberBase: The details of the removed member.

    Raises:
        DeletingException: If there is an error during the removal process.
    """
    try:
        result = await member_service.remove_member(uow, current_user.id, member_id)
        return result
    except Exception as e:
        logger.error(f"Error removing member: {e}")
        raise DeletingException()


@router.post("/{company_id}/leave", response_model=MemberBase)
async def leave_company(
    company_id: int,
    uow: UOWDep,
    member_service: MemberManagementDep,
    current_user: CurrentUserDep,
):
    """
    Allows a member to leave a company.

    Args:
        company_id (int): The ID of the company from which the member wants to leave.
        uow (UOWDep): Unit of Work dependency.
        member_service (MemberManagementDep): Member management service dependency.
        current_user (User): The currently authenticated user.

    Returns:
        MemberBase: The details of the member leaving the company.

    Raises:
        DeletingException: If there is an error during the leaving process.
    """
    try:
        result = await member_service.leave_company(uow, current_user.id, company_id)
        return result
    except Exception as e:
        logger.error(f"Error leaving company: {e}")
        raise DeletingException()
