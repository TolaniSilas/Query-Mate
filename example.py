import os
from dotenv import load_dotenv
from querymate import QueryMate


load_dotenv()


query_mate = QueryMate(
    database_url = os.environ["DATABASE_URL"],
    db_type = "postgresql"
    )


result = query_mate.ask("look at this database and tell me the type of questions that could be asked?")

print(result.answer)  
print("======================")

print(result.sql)     
print("======================")

print(result.rows)   
print("======================")

print(result.status)   
print("======================")


query_mate.disconnect()  