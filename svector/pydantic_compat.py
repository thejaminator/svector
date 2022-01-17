from typing import Sequence, Generic, TYPE_CHECKING, cast

from svector import Svector
from svector.type_definitions import A_co

if TYPE_CHECKING:
    SvectorPydantic = Svector
else:
    class SvectorPydanticImpl(Generic[A_co]):
        """Experimental pydantic compat
        Unforunately can't subclass Svector directly otheriwse pydantic gets confused
        """

        @classmethod
        def __get_validators__(cls):
            yield cls.validate

        @classmethod
        def validate(cls, v, field):  # field: ModelField
            subfield = field.sub_fields[0]  # e.g. the int type in Svector[int]
            if not isinstance(v, Sequence):
                raise TypeError(f"Sequence required to instantiate a Svector, got {v} of type {type(v)}")
            validated_values = []
            for idx, item in enumerate(v):
                valid_value, error = subfield.validate(item, {}, loc=str(idx))
                if error is not None:
                    raise ValueError(f"Error validating {item}, Error: {error}")

                validated_values.append(valid_value)
            return Svector.of(validated_values)


    # Pycharm doesn't check if TYPE_CHECKING so we do this hack
    SvectorPydantic = cast(Svector, SvectorPydanticImpl)


