import os
from dotenv import load_dotenv
from querymate import QueryMate


load_dotenv()


query_mate = QueryMate(
    database_url = os.environ["DATABASE_URL"],
    db_type = "postgresql"
    )


result = query_mate.ask("list top five merchant who had the highest revenue? don't forget the currency is in naira")

print(result.answer)  
print("======================")

print(result.sql)     
print("======================")

print(result.rows)   
print("======================")

print(result.status)   
print("======================")


query_mate.disconnect()  