import math
import pandas as pd
from db import supabase

def upload_data(file_path: str, table_name: str, chunk_size: int = 500,column_map=None,sheet_name=0 ):
    df=pd.read_excel(file_path, sheet_name=sheet_name)