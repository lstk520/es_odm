import typing

from es_odm import InnerESModel, ESModel, Field, ObjectField


class UserProfileODM(InnerESModel):
    """user profile document"""
    user_id: int = Field(None, description="user id")
    nickname: str = Field(None, description="user nickname", keyword=True, fields={
        "pinyin": {
            "type": "text",
            "store": False,
            "term_vector": "with_offsets",
            "analyzer": "pinyin_analyzer",
            "boost": 10
        }
    })
    avatar_url: str = Field(None, description="user avatar url", keyword=True)
    gender: int = Field(None, description="gender")
    address: str = Field(None, description="address", keyword=True)


class UserODM(ESModel):
    """user document"""
    id: int = Field(None, primary_key=True, description="ID")
    username: str = Field(None, description="login name", keyword=True)

    profile: typing.Union[ObjectField[UserProfileODM], dict] = Field(
        None,
        description="user profile",
    )

    class Config:
        """pydantic BaseModel Config"""
        arbitrary_types_allowed = True

    class Index:
        """elasticsearch_dsl Document Index config"""
        name = 'test-index-name'
        settings = {
            "number_of_shards": 1,
        }


def test_odm_doc():
    doc_example = {
        "id": 1,
        "username": "test_username",
        "profile": {
            "user_id": 100,
            "nickname": "test_nickname",
            "gender": 1,
            "address": "test address"
        }
    }
    doc = UserODM(**doc_example)
    assert doc_example == doc.to_dict()


def test_odm_mapping():
    cls = UserODM
    cls_mapping = cls._index.to_dict()

    es_mapping = {
        "settings": {
            "number_of_shards": 1
        },
        "mappings": {
            "properties": {
                "id": {
                    "type": "integer"
                },
                "username": {
                    "fields": {"keyword": {"type": "keyword"}},
                    "type": "text"
                },
                "profile": {
                    "properties": {
                        "user_id": {
                            "type": "integer"
                        },
                        "nickname": {
                            "fields": {
                                "pinyin": {
                                    'store': False,
                                    'term_vector': 'with_offsets',
                                    'analyzer': 'pinyin_analyzer',
                                    'boost': 10,
                                    'type': 'text'
                                },
                                "keyword": {
                                    "type": "keyword"
                                }
                            },
                            "type": "text"
                        },
                        "avatar_url": {
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            },
                            "type": "text"
                        },
                        "gender": {
                            "type": "integer"
                        },
                        "address": {
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            },
                            "type": "text"
                        }
                    },
                    "type": "object"
                }
            }
        }
    }
    assert es_mapping == cls_mapping
