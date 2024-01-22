import json

async def aenumerate(asequence, start=0):
    """Asynchronously enumerate an async iterator from a given start value"""
    n = start
    async for elem in asequence:
        yield n, elem
        n += 1


def to_json_custom(x) -> str:
    if hasattr(x, 'to_json'):
        return json.loads(x.to_json())
    elif hasattr(x, 'to_dict'):
        return x.to_dict()
    else:
        try:
            json.dumps(x)
            return x
        except Exception:
            return str(x)