import env
import motor.motor_asyncio

db = motor.motor_asyncio.AsyncIOMotorClient(env.mongo_uri)["leitnerDB"]

users_collection = db["users"]
