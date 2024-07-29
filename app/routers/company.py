from fastapi import APIRouter, Query, Depends, Request

from app.core.dependencies import (
    UOWDep,
    CompanyServiceDep,
    AuthServiceDep,
    InvitationServiceDep,
    QuizServiceDep,
    MemberManagementDep,
    MemberRequestsDep,
    MemberQueriesDep,
    AnsweredQuestionServiceDep,
    DataExportServiceDep,
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

router = APIRouter(prefix="/companies", tags=["Company"])


@router.post("/", response_model=CompanyDetail)
async def add_company(
    company: CompanyCreate,
    uow: UOWDep,
    company_service: CompanyServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Adds a new company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of companies.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Updates a company by its ID.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Deletes a company by its ID.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Appoints a member as an admin in a company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Removes a member's admin status in a company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Changes the visibility of a company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Requests to join a company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Sends an invitation to a user to join a company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
):
    """
    Retrieves a list of quizzes for a company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Submit answers for quiz
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Get quiz results for a specific user and company.
    """
    try:
        return await data_export_service.read_data_by_user_id_and_company_id(
            uow, is_csv, current_user.id, user_id, company_id
        )
    except Exception as e:
        logger.error(f"Error fetching results for company: {e}")
        raise FetchingException()


@router.get("/{company_id/results/{quiz_id}")
async def get_results_by_company_id_quiz_id(
    company_id: int,
    quiz_id: int,
    is_csv: bool,
    data_export_service: DataExportServiceDep,
    uow: UOWDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Get quiz results for a specific company and quiz.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Export quiz results for a specific company.
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
    answered_question_service: AnsweredQuestionServiceDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Get average score of user within company
    """
    try:
        avg_score = (
            await answered_question_service.calculate_average_score_within_company(
                uow, current_user.id, company_id
            )
        )
        return {"average_score": avg_score}
    except Exception:
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
    """
    return await member_service.get_admins(uow, company_id, request, skip, limit)


@router.post("/{member_id}/remove", response_model=MemberBase)
async def remove_member(
    member_id: int,
    uow: UOWDep,
    member_service: MemberManagementDep,
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Removes a member from the company.
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
    current_user: User = Depends(AuthServiceDep.get_current_user),
):
    """
    Allows a member to leave a company.
    """
    try:
        result = await member_service.leave_company(uow, current_user.id, company_id)
        return result
    except Exception as e:
        logger.error(f"Error leaving company: {e}")
        raise DeletingException()
