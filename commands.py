import datetime
from dataclasses import dataclass
import pyodbc
from config import SQL_SERVER

@dataclass
class Request:
    request_id: int
    sender: str
    text: str
    date: datetime.datetime


async def add_request(sender, text):
    with pyodbc.connect(SQL_SERVER) as db:
        cursor = db.cursor()
        cursor.execute(f"""
                    INSERT INTO Заявки
                       (Отправитель
                       ,Текст
                       ,Дата_отправки
                       )
                 VALUES
                       ('{sender}'
                       ,'{text}'
                       ,GETDATE()
                       )
                    """)
        cursor.commit()


async def finding_amb(text: str):
    with pyodbc.connect(SQL_SERVER) as db:
        amb = []
        cursor = db.cursor()
        with cursor.execute(f"""
                    SELECT * FROM Заявки WHERE Текст = '{text}'
                """) as row:
            for i in row:
                amb.append(Request(
                    request_id=i[0],
                    sender=i[1],
                    text = i[2]
                ))
        cursor.commit()
    return amb
