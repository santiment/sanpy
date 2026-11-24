import json

import san.sanbase_graphql_helper as sgh
from san.error import SanError
from san.graphql import execute_gql
from san.pandas_utils import convert_to_datetime_idx_df
from san.param_validation import validate_kwargs

_SIGNAL_RETURN_FIELDS = ["datetime", "value", "metadata"]
_RAW_SIGNAL_RETURN_FIELDS = ["datetime", "signal", "slug", "value", "metadata", "isHidden"]


def available_signals():
    return execute_gql("{ query_0: getAvailableSignals }")["query_0"]


def get_signal(signal, **kwargs):
    if not signal:
        raise SanError('"signal" must be provided as an argument!')

    validate_kwargs("san.get_signal", kwargs)
    idx = kwargs.pop("idx", 0)
    slug = kwargs.pop("slug", None)
    kwargs = _transform_query_args(_SIGNAL_RETURN_FIELDS, **kwargs)
    selector_or_slug = _choose_selector_or_slug(slug, kwargs)

    query_str = (
        """
    query_{idx}: getSignal(signal: \"{signal}\"){{
        timeseriesData(
            {selector_or_slug}
            from: \"{from_date}\"
            to: \"{to_date}\"
            interval: \"{interval}\"
            aggregation: {aggregation}
        ){{
    """
        + " ".join(kwargs["return_fields"])
        + """
        }}
    }}
    """
    ).format(idx=idx, signal=signal, selector_or_slug=selector_or_slug, **kwargs)

    result = execute_gql("{" + query_str + "}")["query_" + str(idx)]["timeseriesData"]
    return convert_to_datetime_idx_df(result)


def get_raw_signals(**kwargs):
    validate_kwargs("san.get_raw_signals", kwargs)
    idx = kwargs.pop("idx", 0)
    signals = kwargs.pop("signals", None)
    slug = kwargs.pop("slug", None)
    if slug:
        kwargs["selector"] = {"slug": slug}

    kwargs = _transform_query_args(_RAW_SIGNAL_RETURN_FIELDS, **kwargs)
    signals_arg = f"signals: {json.dumps(signals)}" if signals else ""
    selector_arg = kwargs["selector"] if "selector" in kwargs else ""

    query_str = (
        """
    query_{idx}: getRawSignals(
        {signals_arg}
        {selector_arg}
        from: \"{from_date}\"
        to: \"{to_date}\"
    ){{
    """
        + " ".join(kwargs["return_fields"])
        + "}}"
    ).format(idx=idx, signals_arg=signals_arg, selector_arg=selector_arg, **kwargs)

    result = execute_gql("{" + query_str + "}")["query_" + str(idx)]
    return convert_to_datetime_idx_df(result)


def _transform_query_args(return_fields, **kwargs):
    kwargs["return_fields"] = kwargs["return_fields"] if "return_fields" in kwargs else return_fields
    return sgh.transform_query_args("get_metric", **kwargs)


def _choose_selector_or_slug(slug, kwargs):
    if slug:
        return f'slug:"{slug}"'
    if "selector" in kwargs:
        return kwargs["selector"]
    raise SanError('"slug" or "selector" must be provided as an argument!')
