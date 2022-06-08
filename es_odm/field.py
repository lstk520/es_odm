from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import (
    AbstractSet,
    Any,
    Dict,
    Mapping,
    Optional,
    Union,
)
from pydantic.fields import FieldInfo as PydanticFieldInfo
from pydantic.fields import Undefined, UndefinedType
from pydantic.typing import NoArgAnyCallable
from elasticsearch_dsl import (
    Boolean,
    Byte,
    Completion,
    Date,
    DateRange,
    DenseVector,
    Field as DSLField,
    Float,
    Integer,
    Keyword,
    Nested,
    Object,
    Text,
)

from pydantic import ValidationError
from pydantic.fields import ModelField
from typing import TypeVar, Generic


InnerESModelType = TypeVar('InnerESModelType')


# This is not a pydantic model, it's an arbitrary generic class
class InnerFieldModel(Generic[InnerESModelType]):
    def __init__(self, inner: Optional[InnerESModelType]):
        self.inner = inner

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    # You don't need to add the "ModelField", but it will help your
    # editor give you completion and catch errors
    def validate(cls, v, field: ModelField):
        if not isinstance(v, cls):
            # The value is not even a TastingModel
            raise TypeError('Invalid value')
        if not field.sub_fields:
            # Generic parameters were not provided so we don't try to validate
            # them and just return the value as is
            return v
        inner_f = field.sub_fields[0]
        errors = []
        # Here we don't need the validated value, but we want the errors
        valid_value, error = inner_f.validate(v.inner, {}, loc='inner')
        if error:
            errors.append(error)
        if errors:
            raise ValidationError(errors, cls)
        # Validation passed without errors, return the same instance received
        return v


class ObjectField(InnerFieldModel, Generic[InnerESModelType]):
    """elasticsearch_dsl Object type"""
    def __init__(self, inner: Optional[InnerESModelType]):
        super().__init__(inner)


class NestedField(InnerFieldModel, Generic[InnerESModelType]):
    """elasticsearch_dsl Nested type"""
    def __init__(self, inner: Optional[InnerESModelType]):
        super().__init__(inner)


class KeywordField(InnerFieldModel, Generic[InnerESModelType]):
    """elasticsearch_dsl Keyword type"""
    def __init__(self, inner: Optional[InnerESModelType]):
        super().__init__(inner)


class CommonField(InnerFieldModel, Generic[InnerESModelType]):
    """elasticsearch_dsl field type"""
    def __init__(self, inner: Optional[InnerESModelType]):
        super().__init__(inner)


class FieldInfo(PydanticFieldInfo):
    def __init__(self, default: Any = Undefined, **kwargs: Any) -> None:
        primary_key = kwargs.pop("primary_key", False)
        nullable = kwargs.pop("nullable", Undefined)
        foreign_key = kwargs.pop("foreign_key", Undefined)
        index = kwargs.pop("index", Undefined)
        sa_column = kwargs.pop("sa_column", Undefined)
        sa_column_args = kwargs.pop("sa_column_args", Undefined)
        sa_column_kwargs = kwargs.pop("sa_column_kwargs", Undefined)

        keyword = kwargs.pop('keyword', Undefined)
        fields = kwargs.pop('fields', Undefined)
        suggest = kwargs.pop('suggest', Undefined)

        if sa_column is not Undefined:
            if sa_column_args is not Undefined:
                raise RuntimeError(
                    "Passing sa_column_args is not supported when "
                    "also passing a sa_column"
                )
            if sa_column_kwargs is not Undefined:
                raise RuntimeError(
                    "Passing sa_column_kwargs is not supported when "
                    "also passing a sa_column"
                )
        super().__init__(default=default, **kwargs)
        self.primary_key = primary_key
        self.nullable = nullable
        self.foreign_key = foreign_key
        self.index = index
        self.sa_column = sa_column
        self.sa_column_args = sa_column_args
        self.sa_column_kwargs = sa_column_kwargs

        self.suggest = suggest
        self.keyword = keyword
        self.fields = fields

        self.extra = kwargs


def Field(  # noqa
    default: Any = Undefined,
    *,
    default_factory: Optional[NoArgAnyCallable] = None,
    alias: str = None,
    title: str = None,
    description: str = None,
    exclude: Union[
        AbstractSet[Union[int, str]], Mapping[Union[int, str], Any], Any
    ] = None,
    include: Union[
        AbstractSet[Union[int, str]], Mapping[Union[int, str], Any], Any
    ] = None,
    const: bool = None,
    gt: float = None,
    ge: float = None,
    lt: float = None,
    le: float = None,
    multiple_of: float = None,
    min_items: int = None,
    max_items: int = None,
    min_length: int = None,
    max_length: int = None,
    allow_mutation: bool = True,
    regex: str = None,
    primary_key: bool = False,
    foreign_key: Optional[Any] = None,
    nullable: Union[bool, UndefinedType] = Undefined,
    index: Union[bool, UndefinedType] = Undefined,
    schema_extra: Optional[Dict[str, Any]] = None,

    keyword: bool = False,
    fields: dict = None,
    suggest: bool = False,

    **extra: Any,
) -> Any:
    current_schema_extra = schema_extra or {}
    field_info = FieldInfo(
        default,
        default_factory=default_factory,
        alias=alias,
        title=title,
        description=description,
        exclude=exclude,
        include=include,
        const=const,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        min_items=min_items,
        max_items=max_items,
        min_length=min_length,
        max_length=max_length,
        allow_mutation=allow_mutation,
        regex=regex,
        primary_key=primary_key,
        foreign_key=foreign_key,
        nullable=nullable,
        index=index,

        keyword=keyword,
        suggest=suggest,
        fields=fields,

        **current_schema_extra,
        **extra,
    )
    field_info._validate()  # noqa
    return field_info


def get_dsl_field(field: Field) -> DSLField:
    real_model = None
    if getattr(field, 'sub_fields') and len(field.sub_fields) > 1:
        field.type_ = field.sub_fields[0].type_
        real_model = field.sub_fields[0].sub_fields[0].type_

        # commonField use the 2nd type hit in typing.Union
        if issubclass(field.type_, CommonField):
            field.type_ = field.sub_fields[1].type_
            real_model = None

    if issubclass(field.type_, str):
        if hasattr(field.field_info, 'fields') and field.field_info.fields and isinstance(field.field_info.fields, dict):
            _fields = field.field_info.fields
            if hasattr(field.field_info, 'keyword') and field.field_info.keyword:
                _fields["keyword"] = Keyword()
            return Text(fields=_fields)
        elif hasattr(field.field_info, 'keyword') and field.field_info.keyword:
            return Text(fields={"keyword": Keyword()})
        return Text()
    if issubclass(field.type_, float):
        return Float()
    if issubclass(field.type_, bool):
        return Boolean()
    if issubclass(field.type_, int):
        return Integer()
    if issubclass(field.type_, datetime):
        return Date()
    if issubclass(field.type_, date):
        return Date()
    if issubclass(field.type_, timedelta):
        return Integer()
    if issubclass(field.type_, time):
        return Date()
    if issubclass(field.type_, Enum):
        return Keyword()
    if issubclass(field.type_, bytes):
        return Byte()
    if issubclass(field.type_, Decimal):
        return Float()
    if issubclass(field.type_, dict):
        return Object()

    # Object Nested Keyword
    if issubclass(field.type_, ObjectField):
        if real_model:
            return Object(real_model)
        if getattr(field, 'sub_fields'):
            return Object(field.sub_fields[0].type_)
        return Object()

    if issubclass(field.type_, NestedField):
        if real_model:
            return Nested(real_model)
        if getattr(field, 'sub_fields'):
            return Nested(field.sub_fields[0].type_)
        return Nested()

    if issubclass(field.type_, KeywordField):
        return Keyword()

    return Text()
