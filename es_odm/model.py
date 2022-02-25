from typing import (
    Any,
    ClassVar,
    Dict,
    Set,
    Type,
)

from pydantic.main import BaseModel
from pydantic.typing import resolve_annotations, update_model_forward_refs
from pydantic.main import BaseConfig, ModelMetaclass

from es_odm.document import ESIndexMeta, InnerESDocumentMeta


class ESModelMetaclass(ModelMetaclass, ESIndexMeta):
    __config__: Type[BaseConfig]
    __fields__: Dict[str, Any]

    # Replicate DSL
    def __setattr__(cls, name: str, value: Any) -> None:
        # Document.__setattr__(cls, name, value)
        super().__setattr__(name, value)

    def __delattr__(cls, name: str) -> None:
        # ESIndexMeta.__delattr__(cls, name)
        super().__delattr__(name)

    # From Pydantic
    def __new__(cls, name, bases, class_dict: dict, **kwargs) -> Any:
        dict_for_pydantic = {}
        original_annotations = resolve_annotations(
            class_dict.get("__annotations__", {}), class_dict.get("__module__", None)
        )
        pydantic_annotations = {}
        relationship_annotations = {}
        for k, v in class_dict.items():
            dict_for_pydantic[k] = v
        for k, v in original_annotations.items():
            pydantic_annotations[k] = v

        dict_used = {
            **dict_for_pydantic,
            # "__weakref__": None,
            "__annotations__": pydantic_annotations,
        }
        # Duplicate logic from Pydantic to filter config kwargs because if they are
        # passed directly including the registry Pydantic will pass them over to the
        # superclass causing an error
        allowed_config_kwargs: Set[str] = {
            key
            for key in dir(BaseConfig)
            if not (
                key.startswith("__") and key.endswith("__")
            )  # skip dunder methods and attributes
        }
        pydantic_kwargs = kwargs.copy()
        config_kwargs = {
            key: pydantic_kwargs.pop(key)
            for key in pydantic_kwargs.keys() & allowed_config_kwargs
        }

        if 'Config' not in dict_used:
            config_kwargs['arbitrary_types_allowed'] = True

        new_cls = super().__new__(cls, name, bases, dict_used, **config_kwargs)
        new_cls.__annotations__ = {
            **relationship_annotations,
            **pydantic_annotations,
            **new_cls.__annotations__,
        }

        return new_cls


class ESModel(BaseModel, metaclass=ESModelMetaclass):
    """pydantic document model"""
    __name__: ClassVar[str]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

    @classmethod
    def __try_update_forward_refs__(cls) -> None:
        """
        Same as update_forward_refs but will not raise exception
        when forward references are not defined.
        """
        update_model_forward_refs(cls, cls.__fields__.values(), cls.__config__.json_encoders, {}, (NameError,))


class InnerESModelMetaclass(ModelMetaclass, InnerESDocumentMeta):
    __config__: Type[BaseConfig]
    __fields__: Dict[str, Any]

    # Replicate DSL
    def __setattr__(cls, name: str, value: Any) -> None:
        super().__setattr__(name, value)

    def __delattr__(cls, name: str) -> None:
        super().__delattr__(name)

    # From Pydantic
    def __new__(cls, name, bases, class_dict: dict, **kwargs) -> Any:
        dict_for_pydantic = {}
        original_annotations = resolve_annotations(
            class_dict.get("__annotations__", {}), class_dict.get("__module__", None)
        )
        pydantic_annotations = {}
        relationship_annotations = {}
        for k, v in class_dict.items():
            dict_for_pydantic[k] = v
        for k, v in original_annotations.items():
            pydantic_annotations[k] = v

        dict_used = {
            **dict_for_pydantic,
            # "__weakref__": None,
            "__annotations__": pydantic_annotations,
        }
        # Duplicate logic from Pydantic to filter config kwargs because if they are
        # passed directly including the registry Pydantic will pass them over to the
        # superclass causing an error
        allowed_config_kwargs: Set[str] = {
            key
            for key in dir(BaseConfig)
            if not (
                key.startswith("__") and key.endswith("__")
            )  # skip dunder methods and attributes
        }
        pydantic_kwargs = kwargs.copy()
        config_kwargs = {
            key: pydantic_kwargs.pop(key)
            for key in pydantic_kwargs.keys() & allowed_config_kwargs
        }

        new_cls = super().__new__(cls, name, bases, dict_used, **config_kwargs)
        new_cls.__annotations__ = {
            **relationship_annotations,
            **pydantic_annotations,
            **new_cls.__annotations__,
        }

        # todo
        new_cls.__base_cls__ = bases

        return new_cls


class InnerESModel(BaseModel, metaclass=InnerESModelMetaclass):
    """pydantic inner document model"""
    __name__: ClassVar[str]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

    def model_print(self):
        print(self.__name__)

    @classmethod
    def __try_update_forward_refs__(cls) -> None:
        """
        Same as update_forward_refs but will not raise exception
        when forward references are not defined.
        """
        update_model_forward_refs(cls, cls.__fields__.values(), cls.__config__.json_encoders, {}, (NameError,))
