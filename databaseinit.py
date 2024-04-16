from api.database import Database

Database.connect("./sessions/database-env.json")
Database.reset()
Database.initialize()
# Database._pygres.add("product_variations", ("featured", "BOOL"))
# Database._complete_action()
# print(Database._pygres.columns("product_variations"))
Database.disconnect()