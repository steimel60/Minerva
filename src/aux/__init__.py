def get_fields(_dict: dict, fields: list[str]) -> tuple:
    return tuple([_dict.get(f, None) for f in fields])


def csv_transform(x):
    return ",".join(map(str, x)) + "\n"
