# API Response Reference

This document summarizes the current Santiment API response patterns that `sanpy` should handle.

## Response matrix

| Scenario | HTTP status | JSON shape | Typical trigger |
| --- | ---: | --- | --- |
| Success | `200` | `{"data": {...}}` | Query or mutation succeeds |
| Auth pre-check failure | `400` | `{"errors":{"details":"..."}}` | Invalid JWT, invalid API key, malformed `Authorization` header |
| Rate limit or response-size limit | `429` | `{"errors":{"details":"..."}}` | API rate limit reached or response size limit exceeded |
| Business-level pre-check failure | `401` | `{"errors":{"details":"..."}}` | Access blocked before resolver execution |
| GraphQL validation error | `200` | `{"errors":[{"message":"...","locations":[...]}]}` | Invalid field, invalid argument type, schema validation failure |
| GraphQL full failure | `200` | `{"errors":[{"message":"..."}]}` | Unauthorized, missing metric/signal, invalid selector, resource not found |
| GraphQL partial failure | `200` | `{"data": {...}, "errors":[{"message":"...","path":[...]}]}` | One field fails while other fields still resolve |
| GraphQL partial failure with details | `200` | `{"data":{"mutationName":null},"errors":[{"message":"...","details":{...}}]}` | Mutation validation or changeset failure |
| Non-GraphQL endpoint/parser failure | `400` / `404` / `500` | `{"errors":{"details":"..."}}` | Bad request body, missing route, endpoint-level exception |

## Client rules

1. Check the HTTP status code first.
2. For non-`200` responses, treat `errors.details` as the primary error payload.
3. For `200` responses, inspect the `errors` field before treating the result as a pure success.
4. `data` without `errors` is a full success.
5. `data` with `errors` is a partial success and must not be treated as a pure success.
6. `errors.details` usually comes from plugs or endpoint-level failures.
7. `errors[].message` usually comes from the GraphQL layer.
