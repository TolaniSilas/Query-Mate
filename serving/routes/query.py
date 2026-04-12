from fastapi import APIRouter
from querymate import QueryMate
from serving.schemas.models import QueryRequest, QueryResponse
from querymate.core.logger import get_logger


router = APIRouter()

logger = get_logger(__name__)

_instances: dict[str, QueryMate] = {}

SUPPORTED_DBS = {"sqlite", "postgresql", "mysql"}


@router.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):

    if not (bool(request.database_url) ^ bool(request.sqlite_path)):
        
        error = (
            "Provide either database_url or sqlite_path - not both." 
            if request.database_url and request.sqlite_path
            else "Either database_url or sqlite_path must be provided."
        )
        
        return QueryResponse(
            status="error",
            answer=None, 
            error=error
            )
    
    if not request.db_type and not request.user_id:
        return QueryResponse(
            status="error",
            answer=None,
            error = "Can't process - user_id and type of database cannot be null."
        )
    

    if request.db_type and request.user_id:

        user_id = request.user_id.strip()
        db_type = request.db_type.strip()
        

        if db_type not in SUPPORTED_DBS:
            return QueryResponse(
            status="error",
            answer=None,
            error = "Enter the type of database; this field cannot be null."
        )
    

        if user_id not in _instances:
            logger.info("serving | query | new instance | user: %s | db_type: %s", user_id, request.db_type)

            try:
                _instances[user_id] = QueryMate(
                    user_id = user_id,
                    db_type = request.db_type,
                    database_url = request.database_url,
                    sqlite_path = request.sqlite_path,
                )

            except Exception as e:
                logger.error("serving | query | failed to initialise QueryMate | user: %s | error: %s", user_id, str(e))

                return QueryResponse(
                    status = "error",
                    answer = None,
                    error = str(e),
                )

        qm = _instances[user_id]

        logger.info("serving | query | user: %s | question: %s", user_id, request.question)

        try:
            result = qm.ask(request.question)

            return QueryResponse(
                status = result.status,
                answer = result.answer,
                error = result.error,
            )

        except RuntimeError as e:
            _instances.pop(user_id, None)
            
            logger.warning("serving | query | session expired, instance removed | user: %s | error: %s", user_id, str(e))
            
            return QueryResponse(
                status = "error",
                answer = None,
                error = str(e),
            )