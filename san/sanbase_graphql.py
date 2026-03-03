import san.pandas_utils
import san.sanbase_graphql_helper as sgh
from san.batch import Batch
from san.error import SanValidationError
from san.sanitize import sanitize_gql_string

# ---------------------------------------------------------------------------
# Query template registry
# ---------------------------------------------------------------------------
# Each entry maps a query name to a GraphQL template string.
# Templates use Python .format() placeholders.  The special token
# ``{_return_fields}`` is replaced by the auto-formatted return fields.
#
# "simple_slug" queries share a single template (slug + from/to/interval).
# Queries with extra parameters get their own template.
# ---------------------------------------------------------------------------

_SIMPLE_SLUG_QUERIES = ("prices", "ohlc", "miners_balance", "exchange_funds_flow")

_CUSTOM_TEMPLATES = {
    "historical_balance": """
    query_{idx}: historicalBalance (
        address: \"{address}\",
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{{_return_fields}}}""",

    "top_holders_percent_of_total_supply": """
    query_{idx}: topHoldersPercentOfTotalSupply(
        slug: \"{slug}\",
        numberOfHolders: {number_of_holders},
        from: \"{from_date}\",
        to: \"{to_date}\"
    ){{{_return_fields}}}""",

    "top_transfers": """
    query_{idx}: topTransfers(
        {address_selector}
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\"
    ){{{_return_fields}}}""",

    "social_volume": """
    query_{idx}: socialVolume (
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\",
        socialVolumeType: {social_volume_type}
    ){{{_return_fields}}}""",
}

_PROJECT_BY_SLUG_TEMPLATES = {
    "eth_top_transactions": """
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            ethTopTransactions (
                from: \"{from_date}\",
                to: \"{to_date}\",
                limit: {limit},
                transactionType: {transaction_type}
            ){{{_return_fields}}}}}""",

    "eth_spent_over_time": """
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            ethSpentOverTime(
                from: \"{from_date}\",
                to: \"{to_date}\",
                interval: \"{interval}\"
            ){{
        datetime,
        ethSpent
        }}
    }}""",

    "token_top_transactions": """
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            tokenTopTransactions (
                from: \"{from_date}\",
                to: \"{to_date}\",
                limit: {limit}
            ){{
        datetime,
        fromAddress{{
            address,
            isExchange
        }},
        toAddress{{
            address,
            isExchange
        }},
        trxHash,
        trxValue
        }}
    }}""",
}


# ---------------------------------------------------------------------------
# Generic query builder
# ---------------------------------------------------------------------------

def _build_slug_query(query_name: str, template: str, idx, slug, **kwargs):
    """Build a GraphQL query from a template with slug sanitization."""
    kwargs = sgh.transform_query_args(query_name, **kwargs)
    slug = sanitize_gql_string(slug)
    return_fields = " ".join(kwargs["return_fields"])
    # _format_return_fields doubles braces for .format() template concatenation
    # (as in create_query_str), but here we substitute as a value, so unescape.
    return_fields = return_fields.replace("{{", "{").replace("}}", "}")
    return template.format(idx=idx, slug=slug, _return_fields=return_fields, **kwargs)


def _make_simple_slug_fn(query_name):
    """Generate a simple slug query function that delegates to create_query_str."""
    def fn(idx, slug, **kwargs):
        return sgh.create_query_str(query_name, idx, slug, **kwargs)
    fn.__name__ = query_name
    return fn


def _make_custom_slug_fn(query_name, template):
    """Generate a custom-template slug query function."""
    def fn(idx, slug, **kwargs):
        return _build_slug_query(query_name, template, idx, slug, **kwargs)
    fn.__name__ = query_name
    return fn


# Register simple slug queries
for _name in _SIMPLE_SLUG_QUERIES:
    globals()[_name] = _make_simple_slug_fn(_name)

# Register custom-template slug queries
for _name, _tmpl in _CUSTOM_TEMPLATES.items():
    globals()[_name] = _make_custom_slug_fn(_name, _tmpl)

# Register projectBySlug queries
for _name, _tmpl in _PROJECT_BY_SLUG_TEMPLATES.items():
    globals()[_name] = _make_custom_slug_fn(_name, _tmpl)


# ---------------------------------------------------------------------------
# Queries with unique logic (cannot be data-driven)
# ---------------------------------------------------------------------------

def emerging_trends(idx, **kwargs):
    kwargs = sgh.transform_query_args("emerging_trends", **kwargs)
    return_fields = " ".join(kwargs["return_fields"])
    return_fields = return_fields.replace("{{", "{").replace("}}", "}")
    query_str = """
    query_{idx}: getTrendingWords (
        from: \"{from_date}\",
        to: \"{to_date}\",
        size: {size},
        interval: \"{interval}\"
    ){{{_return_fields}
    }}
    """.format(idx=idx, _return_fields=return_fields, **kwargs)
    return query_str


def ohlcv(idx, slug, **kwargs):
    return_fields = ["openPriceUsd", "closePriceUsd", "highPriceUsd", "lowPriceUsd", "volume", "marketcap"]
    batch = Batch()
    batch.get(f"prices/{slug}", **kwargs)
    batch.get(f"ohlc/{slug}", **kwargs)
    [price_df, ohlc_df] = batch.execute()
    merged = san.pandas_utils.merge(price_df, ohlc_df)
    if merged.size != 0:
        return merged[return_fields]
    return merged


def projects(idx, slug, **kwargs):
    if slug == "erc20":
        return sgh.erc20_projects(idx, **kwargs)
    elif slug == "all":
        return sgh.all_projects(idx, **kwargs)
    raise SanValidationError(f"Unknown project group: {slug}")


def social_volume_projects(idx, **kwargs):
    return f"""
    query_{idx}: socialVolumeProjects
    """


def topic_search(idx, **kwargs):
    kwargs = sgh.transform_query_args("topic_search", **kwargs)
    return """
    query_{idx}: topicSearch (
        source: {source},
        searchText: \"{search_text}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    )    """.format(idx=idx, **kwargs)


# ---------------------------------------------------------------------------
# Metric queries (selector/slug pattern)
# ---------------------------------------------------------------------------

def __choose_selector_or_slugs(slugs, **kwargs):
    if slugs:
        sanitized_slugs = [sanitize_gql_string(str(s)) for s in slugs]
        slug_list = ", ".join(f'"{s}"' for s in sanitized_slugs)
        return f"selector: {{slugs: [{slug_list}]}}"

    if "slugs" in kwargs:
        slugs_val = kwargs["slugs"]
        if isinstance(slugs_val, list):
            sanitized_slugs = [sanitize_gql_string(str(s)) for s in slugs_val]
            slug_list = ", ".join(f'"{s}"' for s in sanitized_slugs)
            return f"selector: {{slugs: [{slug_list}]}}"
        return slugs_val
    if "selector" in kwargs:
        return kwargs["selector"]
    raise SanValidationError('"slugs" or "selector" must be provided as an argument!')


def __choose_selector_or_slug(slug, **kwargs):
    if slug:
        return f'slug:"{sanitize_gql_string(slug)}"'

    if "slug" in kwargs:
        slug_val = kwargs["slug"]
        if isinstance(slug_val, str):
            return f'slug:"{sanitize_gql_string(slug_val)}"'
        return slug_val
    if "selector" in kwargs:
        return kwargs["selector"]
    raise SanValidationError('"slug" or "selector" must be provided as an argument!')


def get_metric_timeseries_data(idx, metric, slug=None, **kwargs):
    kwargs = sgh.transform_query_args("get_metric", **kwargs)
    selector_or_slug = __choose_selector_or_slug(slug, **kwargs)
    metric = sanitize_gql_string(metric)
    transform_arg = _transform_arg_helper(kwargs)

    return """
    query_{idx}: getMetric(metric: \"{metric}\"){{
        timeseriesDataJson(
            {selector_or_slug}
            {transform_arg}
            from: \"{from_date}\"
            to: \"{to_date}\"
            interval: \"{interval}\"
            aggregation: {aggregation}
            includeIncompleteData: {include_incomplete_data}
        )
    }}
    """.format(
        idx=idx, metric=metric,
        selector_or_slug=selector_or_slug, transform_arg=transform_arg,
        **kwargs,
    )


def get_metric_timeseries_data_per_slug(idx, metric, slugs=None, **kwargs):
    kwargs = sgh.transform_query_args("get_metric", **kwargs)
    selector_or_slugs = __choose_selector_or_slugs(slugs, **kwargs)
    metric = sanitize_gql_string(metric)
    transform_arg = _transform_arg_helper(kwargs)

    return """
    query_{idx}: getMetric(metric: \"{metric}\"){{
        timeseriesDataPerSlugJson(
            {selector_or_slugs}
            {transform_arg}
            from: \"{from_date}\"
            to: \"{to_date}\"
            interval: \"{interval}\"
            aggregation: {aggregation}
            includeIncompleteData: {include_incomplete_data}
        )
    }}
    """.format(
        idx=idx, metric=metric,
        selector_or_slugs=selector_or_slugs, transform_arg=transform_arg,
        **kwargs,
    )


def _transform_arg_helper(kwargs):
    transform_arg_str = ""
    if "transform" in kwargs and isinstance(kwargs["transform"], dict):
        transform_arg_str += "transform:{"
        for k, v in kwargs["transform"].items():
            sanitized_key = sanitize_gql_string(str(k))
            if isinstance(v, int):
                transform_arg_str += f"{sanitized_key}: {v}\n"
            elif isinstance(v, str):
                transform_arg_str += f'{sanitized_key}: "{sanitize_gql_string(v)}"\n'
            else:
                raise SanValidationError(f'"transform" argument incorrect: {kwargs["transform"]}')
        transform_arg_str += "}"
    return transform_arg_str


def get_api_calls_made():
    return """{
    currentUser {
        apiCallsHistory(from: "utc_now-30d", to: "utc_now", interval: "1d", authMethod: APIKEY) {
            apiCallsCount, datetime
        }
    }}"""
