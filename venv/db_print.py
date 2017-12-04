from sqlalchemy_declarative import App_Runs, Base, Event_Logs
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import json

engine = create_engine('sqlite:///logs.db')
Base.metadata.bind = engine
DBSession = sessionmaker()
DBSession.bind = engine
session = DBSession()
# Retrieve one Address whose person field is point to the person object
first = session.query(Event_Logs).first()
print(first.id)
logs = first.message
parsed_logs = json.loads(logs)
print(parsed_logs.get('message'))
