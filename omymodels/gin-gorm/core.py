#### Delete for development
from omymodels import common
from icecream import ic
from typing import Optional, List, Dict


from simple_ddl_parser import DDLParser, parse_from_file


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


def get_tables_information(
    ddl: Optional[str] = None, ddl_file: Optional[str] = None
) -> List[Dict]:
    if not ddl_file and not ddl:
        raise ValueError(
            "You need to provide one of above argument: ddl with string that "
            "contains ddl or ddl_file that contains path to ddl file to parse"
        )
    if ddl:
        tables = DDLParser(ddl).run(group_by_type=True)
    elif ddl_file:
        tables = parse_from_file(ddl_file, group_by_type=True)
    return tables


def remove_quotes_from_strings(item: Dict) -> Dict:
    for key, value in item.items():
        if key.lower() != "default":
            if isinstance(value, list):
                value = iterate_over_the_list(value)
                item[key] = value
            elif isinstance(value, str) and key != "default":
                item[key] = value.replace('"', "")
            elif isinstance(value, dict):
                value = remove_quotes_from_strings(value)
    return item


def iterate_over_the_list(items: List) -> str:
    """ simple ddl parser return " in strings if in DDL them was used, we need to remove them"""
    for item in items:
        if isinstance(item, dict):
            remove_quotes_from_strings(item)
        elif isinstance(item, str):
            new_item = item.replace('"', "")
            items.remove(item)
            items.append(new_item)
    return items


data = get_tables_information(ddl=ddl)
data = remove_quotes_from_strings(data)
ic(data)