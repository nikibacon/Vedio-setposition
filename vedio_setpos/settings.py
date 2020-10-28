from dotenv import load_dotenv
import os
load_dotenv()

ACCOUNT_SID = os.getenv('ACCOUNT_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TOKEN = os.getenv('TOKEN')