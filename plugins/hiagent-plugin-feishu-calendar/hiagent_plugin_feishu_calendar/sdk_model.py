
from typing import TypeVar, Generic, Any, Type, Tuple, get_args, List, Optional, Dict, Set
from pydantic import BaseModel, create_model, Field
from lark_oapi.core.model import BaseResponse, Error # type: ignore
from lark_oapi.api.calendar.v4 import * # type: ignore
from lark_oapi.core.construct import type_of # type: ignore

T = TypeVar('T')

def convert_type(t: Type, visited: dict={}) -> Type:
    type_t = type_of(t)
    # print(f"convert {t} {t is List} {t is list} {isinstance(t, List)}")
    if type_t is str or type_t is int or type_t is float or type_t is bool or type_t is Any:
        return t
    if type_t is List or type_t is Set or type_t is tuple:
        sub_t = get_args(t)[0]
        m = convert_type(sub_t, visited)
        return List[m] # type: ignore
    if type_t is Optional:
        sub_t = get_args(t)[0]
        m = convert_type(sub_t, visited)
        return Optional[m] # type: ignore
    if type_t is Dict:
        k_t = get_args(t)[0]
        sub_t = get_args(t)[1]
        m = convert_type(sub_t, visited)
        return Dict[k_t, m] # type: ignore
    if hasattr(t, "_types"):
        if t in visited:
            return visited[t]
        if isinstance(t, type):
            name = t.__name__
        else:
            name = t.__class__.__name__
        # print(f"custom type: {t} {name} {t is Type} {t is object} {hasattr(t, '__dict__')} {hasattr(t, '__class__')} {isinstance(t, type)}")
        fields = {}
        for k, v in t._types.items():
            fields[k] = (convert_type(v, visited), None)
        m = create_model(name, **fields) # type: ignore
        visited[t] = m
        return m
    raise ValueError(f"unknown type: {t}")


ErrorModel = convert_type(Error)

ListCalendarResponseModel = convert_type(ListCalendarResponseBody) # type: ignore
CalendarEventModel = convert_type(CalendarEvent) # type: ignore
CreateCalendarEventResponseModel = convert_type(CreateCalendarEventResponseBody) # type: ignore
ListCalendarEventResponseBodyModel = convert_type(ListCalendarEventResponseBody) # type: ignore
PatchCalendarEventResponseBodyModel = convert_type(PatchCalendarEventResponseBody) # type: ignore
SearchCalendarEventResponseBodyModel = convert_type(SearchCalendarEventResponseBody) # type: ignore
EventSearchFilterModel = convert_type(EventSearchFilter) # type: ignore
CalendarEventAttendeeModel = convert_type(CalendarEventAttendee) # type: ignore
CreateCalendarEventAttendeeResponseBodyModel = convert_type(CreateCalendarEventAttendeeResponseBody) # type: ignore

class BaseRespModel(BaseModel, Generic[T]):
    code: int = 0
    msg: str = ""
    error: ErrorModel | None = None # type: ignore
    data: T | None = None
