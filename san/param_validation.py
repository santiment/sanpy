from san.api_config import ApiConfig
from san.error import SanError

_SUPPORTED_KWARGS = frozenset(
    {
        "slug",
        "slugs",
        "selector",
        "from_date",
        "to_date",
        "interval",
        "aggregation",
        "include_incomplete_data",
        "only_finalized_data",
        "transform",
        "version",
        "return_fields",
        "address",
        "transaction_type",
        "number_of_holders",
        "limit",
        "size",
        "social_volume_type",
        "source",
        "search_text",
        "idx",
    }
)

_PUBLIC_KWARGS = _SUPPORTED_KWARGS - {"idx"}


def validate_kwargs(func_name, kwargs):
    if not ApiConfig.strict_kwargs:
        return
    unsupported = sorted(set(kwargs) - _SUPPORTED_KWARGS)
    if not unsupported:
        return
    raise SanError(
        "{func}() received unsupported parameter(s): {bad}. "
        "Supported parameters: {ok}. "
        "If you expect a parameter to be supported, upgrade sanpy "
        "with `pip install --upgrade sanpy`.".format(
            func=func_name,
            bad=", ".join(unsupported),
            ok=", ".join(sorted(_PUBLIC_KWARGS)),
        )
    )
