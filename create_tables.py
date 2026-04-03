from bot.db import engine, Base
from bot import models

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")