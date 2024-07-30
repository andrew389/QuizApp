import json
import csv
import os
import aiofiles
from fastapi.responses import StreamingResponse

from app.db.redis_db import redis_connection
from app.services.member_management import MemberManagement
from app.uow.unitofwork import UnitOfWork


class DataExportService:
    @staticmethod
    async def fetch_data(pattern: str) -> list:
        """
        Fetches data from Redis based on the given pattern using SCAN.

        Args:
            pattern (str): The pattern to match Redis keys.

        Returns:
            list: A list of data retrieved from Redis.
        """
        all_data = []
        cursor = 0
        while cursor != 0:
            cursor, keys = await redis_connection.redis.scan(match=pattern)
            for key in keys:
                data_json = await redis_connection.redis.get(key)
                if data_json:
                    data = json.loads(data_json)
                    all_data.append(data)
        return all_data

    @staticmethod
    async def _export_data(
        all_data: list, file_name: str, is_csv: bool
    ) -> StreamingResponse:
        """
        Exports the provided data to either a CSV or JSON file and returns a StreamingResponse.

        Args:
            all_data (list): The data to be exported.
            file_name (str): The name of the file to which the data will be exported.
            is_csv (bool): Flag indicating if the data should be exported as CSV or JSON.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        directory = "exported_data"
        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, file_name)

        if is_csv:
            return await DataExportService.export_data_as_csv(all_data, file_path)
        else:
            return await DataExportService.export_data_as_json(all_data, file_path)

    @staticmethod
    async def read_data_by_user_id(
        is_csv: bool, current_user_id: int
    ) -> StreamingResponse:
        """
        Reads data for a specific user and returns it as a CSV or JSON file.

        Args:
            is_csv (bool): Flag indicating if the data should be exported as CSV or JSON.
            current_user_id (int): The ID of the user whose data is being exported.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        pattern = f"answered_quiz_{current_user_id}_*_*"
        all_data = await DataExportService.fetch_data(pattern)
        return await DataExportService._export_data(
            all_data,
            (
                f"exported_data_by_user_{current_user_id}.csv"
                if is_csv
                else f"exported_data_by_user_{current_user_id}.json"
            ),
            is_csv,
        )

    @staticmethod
    async def read_data_by_user_id_and_company_id(
        uow: UnitOfWork,
        is_csv: bool,
        current_user_id: int,
        user_id: int,
        company_id: int,
    ) -> StreamingResponse:
        """
        Reads data for a specific user and company and returns it as a CSV or JSON file.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for permission checking.
            is_csv (bool): Flag indicating if the data should be exported as CSV or JSON.
            current_user_id (int): The ID of the current user.
            user_id (int): The ID of the user whose data is being exported.
            company_id (int): The ID of the company whose data is being exported.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        await MemberManagement.check_is_user_have_permission(
            uow, current_user_id, company_id
        )

        pattern = f"answered_quiz_{user_id}_{company_id}_*"
        all_data = await DataExportService.fetch_data(pattern)
        return await DataExportService._export_data(
            all_data,
            (
                f"exported_data_by_user_{user_id}_company_{company_id}.csv"
                if is_csv
                else f"exported_data_by_user_{user_id}_company_{company_id}.json"
            ),
            is_csv,
        )

    @staticmethod
    async def read_data_by_company_id(
        uow: UnitOfWork, is_csv: bool, current_user_id: int, company_id: int
    ) -> StreamingResponse:
        """
        Reads data for a specific company and returns it as a CSV or JSON file.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for permission checking.
            is_csv (bool): Flag indicating if the data should be exported as CSV or JSON.
            current_user_id (int): The ID of the current user.
            company_id (int): The ID of the company whose data is being exported.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        await MemberManagement.check_is_user_have_permission(
            uow, current_user_id, company_id
        )

        pattern = f"answered_quiz_*_{company_id}_*"
        all_data = await DataExportService.fetch_data(pattern)
        return await DataExportService._export_data(
            all_data,
            (
                f"exported_data_by_company_{company_id}.csv"
                if is_csv
                else f"exported_data_by_company_{company_id}.json"
            ),
            is_csv,
        )

    @staticmethod
    async def read_data_by_company_id_and_quiz_id(
        uow: UnitOfWork,
        is_csv: bool,
        current_user_id: int,
        company_id: int,
        quiz_id: int,
    ) -> StreamingResponse:
        """
        Reads data for a specific company and quiz and returns it as a CSV or JSON file.

        Args:
            uow (UnitOfWork): The UnitOfWork instance for permission checking.
            is_csv (bool): Flag indicating if the data should be exported as CSV or JSON.
            current_user_id (int): The ID of the current user.
            company_id (int): The ID of the company whose data is being exported.
            quiz_id (int): The ID of the quiz whose data is being exported.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        await MemberManagement.check_is_user_have_permission(
            uow, current_user_id, company_id
        )

        pattern = f"answered_quiz_*_{company_id}_{quiz_id}"
        all_data = await DataExportService.fetch_data(pattern)
        return await DataExportService._export_data(
            all_data,
            (
                f"exported_data_company_{company_id}_quiz_{quiz_id}.csv"
                if is_csv
                else f"exported_data_company_{company_id}_quiz_{quiz_id}.json"
            ),
            is_csv,
        )

    @staticmethod
    async def export_data_as_json(all_data: list, file_name: str) -> StreamingResponse:
        """
        Exports data as a JSON file and returns a StreamingResponse.

        Args:
            all_data (list): The data to be exported.
            file_name (str): The name of the file to which the data will be exported.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        json_data = json.dumps(all_data, indent=4)
        async with aiofiles.open(file_name, mode="w") as file:
            await file.write(json_data)

        async def file_iterator():
            async with aiofiles.open(file_name, mode="rb") as file:
                while chunk := await file.read(1024):
                    yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )

    @staticmethod
    async def export_data_as_csv(all_data: list, file_name: str) -> StreamingResponse:
        """
        Exports data as a CSV file and returns a StreamingResponse.

        Args:
            all_data (list): The data to be exported.
            file_name (str): The name of the file to which the data will be exported.

        Returns:
            StreamingResponse: A StreamingResponse containing the exported data.
        """
        headers = list(all_data[0].keys()) if all_data else []

        async with aiofiles.open(file_name, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            await file.write("\ufeff")  # Write BOM for UTF-8
            writer.writeheader()
            for row in all_data:
                writer.writerow(row)

        async def file_iterator():
            async with aiofiles.open(file_name, mode="rb") as file:
                while chunk := await file.read(1024):
                    yield chunk

        return StreamingResponse(
            file_iterator(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={file_name}"},
        )
