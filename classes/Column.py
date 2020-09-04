class Column:
    def __init__(self, column_name, type_name, nullable, primary, audit):
        self.column_name = column_name
        self.type_name = type_name
        self.nullable = nullable
        self.primary = primary
        self.audit = audit

    @staticmethod
    def mapType(type_name):
        mapper = {"Integer": "int", "String": "str", "Boolean": "bool", "DateTime": "datetime", "Date": "date",
                  "Text": "str", "ForeignKey": "int"}
        for t in list(mapper.keys()):
            if t in type_name:
                return mapper[t]
        return "None"

    def to_pydantic(self, is_null):
        if is_null:
            return f"{self.column_name}: Optional[{self.mapType(self.type_name)}]"
        else:
            return f"{self.column_name}: {self.mapType(self.type_name)}"
