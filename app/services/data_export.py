import json
import csv
from typing import List, Optional
from io import StringIO
from fastapi.responses import StreamingResponse

from app.core.logger import logger
from app.db.redis_db import redis


class DataExportService:
    @staticmethod
    async def get_data(
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        quiz_id: Optional[int] = None,
    ) -> List[str]:
        return await redis.read_by_filters(
            user_id=user_id, company_id=company_id, quiz_id=quiz_id
        )

    @staticmethod
    async def export_to_json(
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        quiz_id: Optional[int] = None,
    ) -> StreamingResponse:
        data = await DataExportService.get_data(user_id, company_id, quiz_id)
        logger.info(f"{data}")
        json_data = json.dumps(data)

        return StreamingResponse(
            content=StringIO(json_data),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=data.json"},
        )

    @staticmethod
    async def export_to_csv(
        user_id: Optional[int] = None,
        company_id: Optional[int] = None,
        quiz_id: Optional[int] = None,
    ) -> StreamingResponse:
        data = await DataExportService.get_data(user_id, company_id, quiz_id)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["value"])  # Header
        for item in data:
            writer.writerow([item])

        output.seek(0)  # Move to the beginning of the file

        return StreamingResponse(
            content=output,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=data.csv"},
        )
