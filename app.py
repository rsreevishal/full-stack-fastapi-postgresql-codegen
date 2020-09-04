import re
import os
from classes import Table as tableClass
from classes import FileHandler as file_handler

file = file_handler.FileHandler
FILE_PATH = "/home/sree/SREEVISHAL/Project/ohr/backend/app/models.py"
table_name = input("Enter the sql alchemy model class name:")
sql_alchemy_file = open(FILE_PATH, "r").read()
tables = re.findall(r"class (.+?)\(Base\):", sql_alchemy_file)
if table_name in tables:
    if not os.path.exists(f"./output/{table_name}"):
        os.makedirs(f"./output/{table_name}")
    sql_alchemy_model = file.get_body(FILE_PATH, f"class {table_name}(Base):",
                                      f"class {tables[tables.index(table_name) + 1]}(Base):")
    imports = file.get_body("./template/imports.txt", "{sql_alchemy}", "{/sql_alchemy}", True)
    result = imports + "\n" + sql_alchemy_model
    file.writeTo(f"./output/{table_name}/db_model_{table_name}.py", result)
    table_obj = tableClass.Table(table_name, sql_alchemy_model)
    table_obj.generate()
else:
    print("Table not found!")
