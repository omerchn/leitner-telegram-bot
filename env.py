import os
import dotenv

dotenv.load_dotenv()

mongo_uri = os.environ.get("MONGO_URI")
