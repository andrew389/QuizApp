import json
from unittest.mock import patch, AsyncMock
from fastapi.responses import StreamingResponse
import pytest
from app.services.data_export import DataExportService


@pytest.mark.asyncio
async def test_read_data_by_user_id(mock_redis):
    mock_redis.keys.return_value = ["answered_quiz_1_1_1"]
    mock_redis.get.return_value = json.dumps({"key": "value"})

    with patch(
        "app.services.data_export.DataExportService.export_data_as_csv", new=AsyncMock()
    ) as mock_export_csv:
        with patch(
            "app.services.data_export.DataExportService.export_data_as_json",
            new=AsyncMock(),
        ) as mock_export_json:
            mock_export_csv.return_value = StreamingResponse(
                iter([]), media_type="text/csv"
            )
            mock_export_json.return_value = StreamingResponse(
                iter([]), media_type="application/json"
            )

            response = await DataExportService.read_data_by_user_id(
                is_csv=True, current_user_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_csv.assert_called_once()

            response = await DataExportService.read_data_by_user_id(
                is_csv=False, current_user_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_json.assert_called_once()


@pytest.mark.asyncio
async def test_read_data_by_user_id_and_company_id(
    mock_redis, mock_member_management, mock_uow
):
    mock_redis.keys.return_value = ["answered_quiz_1_1_1"]
    mock_redis.get.return_value = json.dumps({"key": "value"})
    mock_member_management.check_is_user_have_permission.return_value = None

    with patch(
        "app.services.data_export.DataExportService.export_data_as_csv", new=AsyncMock()
    ) as mock_export_csv:
        with patch(
            "app.services.data_export.DataExportService.export_data_as_json",
            new=AsyncMock(),
        ) as mock_export_json:
            mock_export_csv.return_value = StreamingResponse(
                iter([]), media_type="text/csv"
            )
            mock_export_json.return_value = StreamingResponse(
                iter([]), media_type="application/json"
            )

            response = await DataExportService.read_data_by_user_id_and_company_id(
                uow=mock_uow, is_csv=True, current_user_id=1, user_id=1, company_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_csv.assert_called_once()

            response = await DataExportService.read_data_by_user_id_and_company_id(
                uow=mock_uow, is_csv=False, current_user_id=1, user_id=1, company_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_json.assert_called_once()


@pytest.mark.asyncio
async def test_read_data_by_company_id(mock_redis, mock_member_management, mock_uow):
    # Mock data
    mock_redis.keys.return_value = ["answered_quiz_1_1_1"]
    mock_redis.get.return_value = json.dumps({"key": "value"})
    mock_member_management.check_is_user_have_permission.return_value = None

    with patch(
        "app.services.data_export.DataExportService.export_data_as_csv", new=AsyncMock()
    ) as mock_export_csv:
        with patch(
            "app.services.data_export.DataExportService.export_data_as_json",
            new=AsyncMock(),
        ) as mock_export_json:
            mock_export_csv.return_value = StreamingResponse(
                iter([]), media_type="text/csv"
            )
            mock_export_json.return_value = StreamingResponse(
                iter([]), media_type="application/json"
            )

            response = await DataExportService.read_data_by_company_id(
                uow=mock_uow, is_csv=True, current_user_id=1, company_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_csv.assert_called_once()

            response = await DataExportService.read_data_by_company_id(
                uow=mock_uow, is_csv=False, current_user_id=1, company_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_json.assert_called_once()


@pytest.mark.asyncio
async def test_read_data_by_company_id_and_quiz_id(
    mock_redis, mock_member_management, mock_uow
):
    # Mock data
    mock_redis.keys.return_value = ["answered_quiz_1_1_1"]
    mock_redis.get.return_value = json.dumps({"key": "value"})
    mock_member_management.check_is_user_have_permission.return_value = None

    with patch(
        "app.services.data_export.DataExportService.export_data_as_csv", new=AsyncMock()
    ) as mock_export_csv:
        with patch(
            "app.services.data_export.DataExportService.export_data_as_json",
            new=AsyncMock(),
        ) as mock_export_json:
            mock_export_csv.return_value = StreamingResponse(
                iter([]), media_type="text/csv"
            )
            mock_export_json.return_value = StreamingResponse(
                iter([]), media_type="application/json"
            )

            response = await DataExportService.read_data_by_company_id_and_quiz_id(
                uow=mock_uow, is_csv=True, current_user_id=1, company_id=1, quiz_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_csv.assert_called_once()

            response = await DataExportService.read_data_by_company_id_and_quiz_id(
                uow=mock_uow, is_csv=False, current_user_id=1, company_id=1, quiz_id=1
            )
            assert isinstance(response, StreamingResponse)
            mock_export_json.assert_called_once()
