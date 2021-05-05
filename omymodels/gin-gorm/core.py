#### Dev
from omymodels import *
from icecream import ic

###Prod
from typing import Optional, List, Dict
from omymodels.pydantic import templates as pt
from omymodels.utils import create_class_name, type_not_found, enum_number_name_list
from omymodels.pydantic.types import types_mapping, datetime_types

ddl = """
CREATE table user_history (
     runid                 decimal(21) null
    ,job_id                decimal(21)  null
    ,id                    varchar(100) not null
    ,user              varchar(100) not null
    ,status                varchar(10) not null
    ,event_time            timestamp not null default now()
    ,comment           varchar(1000) not null default 'none'
    ) ;
"""
data = get_tables_information(ddl=ddl)
data = remove_quotes_from_strings(data)
ic(data)


## Prod


class ModelGenerator:
    def __init__(self):

        self.imports = set([pt.base_model])
        self.types_for_import = ["Json"]
        self.datetime_import = False
        self.typing_imports = set()
        self.enum_imports = set()
        self.custom_types = {}
        self.uuid_import = False

    def generate_attr(self, column: Dict, defaults_off: bool) -> str:
        if column["nullable"]:
            self.typing_imports.add("Optional")
            column_str = pt.pydantic_optional_attr
        else:
            column_str = pt.pydantic_attr

        if "." in column["type"]:
            _type = column["type"].split(".")[1]
        else:
            _type = column["type"].lower().split("[")[0]
        if self.custom_types:
            column_type = self.custom_types.get(_type, _type)
            if isinstance(column_type, tuple):
                _type = column_type[1]
                column_type = column_type[0]
            if column_type != type_not_found:
                column_type = f"{column_type}({_type})"
        if _type == _type:
            _type = types_mapping.get(_type, _type)
        if _type in self.types_for_import:
            self.imports.add(_type)
        elif "datetime" in _type:
            self.datetime_import = True
        elif "[" in column["type"]:
            self.typing_imports.add("List")
            _type = f"List[{_type}]"
        if _type == "UUID":
            self.uuid_import = True

        column_str = column_str.format(arg_name=column["name"], type=_type)
        if column["default"] and defaults_off is False:
            if column["type"].upper() in datetime_types:
                if "now" in column["default"]:
                    # todo: need to add other popular PostgreSQL & MySQL functions
                    column["default"] = "datetime.datetime.now()"
                elif "'" not in column["default"]:
                    column["default"] = f"'{column['default']}'"
            column_str += pt.pydantic_default_attr.format(default=column["default"])

        return column_str


##Dev
model_gen = ModelGenerator()
model_gen.generate_attr(data, 0)
