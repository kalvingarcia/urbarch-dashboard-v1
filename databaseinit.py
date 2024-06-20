from api.database import Database

Database.connect("./sessions/database-env.json")
# Database.reset()
# Database.initialize()
Database.disconnect()