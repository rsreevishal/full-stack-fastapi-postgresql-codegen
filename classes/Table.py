import re
from . import Column as columnClass
from . import FileHandler as file_handler

file = file_handler.FileHandler
INDENT_SPACE = 4


class Table:
    def __init__(self, _table_name, _file_content):
        self.table_name = _table_name
        self.columns = self.addColumnFromSqlAlchemy(_file_content)

    @staticmethod
    def addColumnFromSqlAlchemy(file_content):
        columns = re.findall(r".*Column.*", file_content)
        result = []
        for column in columns:
            nullable = True
            primary = False
            audit = False
            filtered = column.strip()
            col_name = filtered[0:filtered.index("=")].strip()
            audit_fields = ["deleted", "created_on", "created_by", "last_modified_on", "last_modified_by", "deleted_on",
                            "deleted_by"]
            if col_name in audit_fields:
                audit = True
            col_params = re.findall(r"Column\((.+?)\)$", filtered)[0].split(",")
            col_type = col_params[0]
            for param in col_params:
                if "primary" in param.strip():
                    primary = True
                if "nullable" in param.strip():
                    value = param[param.index("=") + 1:].strip()
                    if value == "False":
                        nullable = False
            col_obj = columnClass.Column(col_name, col_type, nullable, primary, audit)
            result.append(col_obj)
        return result

    def to_pydantic(self):
        imports = file.get_body("template/imports.txt", "{pydantic}", "{/pydantic}", True)
        base_template = [f"class {self.table_name}Base(BaseModel):"]
        create_template = [f"class {self.table_name}Create(BaseModel):"]
        update_template = [f"class {self.table_name}Update(BaseModel):"]
        indent = " " * INDENT_SPACE
        for column in self.columns:
            base_template.append(indent + column.to_pydantic(True))
            if not column.primary and not column.audit:
                create_template.append(indent + column.to_pydantic(column.nullable))
            if not column.audit:
                if column.primary:
                    update_template.append(indent + column.to_pydantic(False))
                else:
                    update_template.append(indent + column.to_pydantic(True))
        result = base_template + create_template + update_template
        file.writeTo(f"./output/{self.table_name}/pydantic_{self.table_name}.py", imports + "\n" + "\n".join(result))

    def to_crud_api(self, template_path, file_path):
        template = open(template_path, "r").read()
        template = template.replace("{table}", self.table_name)
        template = template.replace("{table_name}", self.table_name.lower())
        uid = ""
        for col in self.columns:
            if col.primary:
                uid = col.column_name
        template = template.replace("{uid}", uid)
        template = template.replace("{model_base}", f"{self.table_name}Base")
        template = template.replace("{model_create}", f"{self.table_name}Create")
        template = template.replace("{model_update}", f"{self.table_name}Update")
        template = template.replace("{orm_import}", f"from . import {self.table_name}")
        template = template.replace("{pydantic_import}",
                                    f"from . import {self.table_name}Base, {self.table_name}Create, {self.table_name}Update")
        template = template.replace("{crud_import}", f"from . import {self.table_name} as db_{self.table_name.lower()}")
        file.writeTo(file_path, template)

    def generate(self):
        self.to_pydantic()
        self.to_crud_api("template/crud_template.txt", f"./output/{self.table_name}/crud_{self.table_name}.py")
        self.to_crud_api("template/api_template.txt", f"./output/{self.table_name}/api_{self.table_name}.py")
