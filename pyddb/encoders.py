from datetime import datetime, timezone, date
from fastapi.encoders import jsonable_encoder


def as_dict(model, **kwargs):
    return jsonable_encoder(
        model,
        custom_encoder={
            datetime: lambda dt: (
                f"{dt.astimezone(tz=timezone.utc).isoformat(sep='T', timespec='milliseconds')[:-6]}"
                "Z"
            ),
            date: str
        },
        **kwargs
    )
