# Operational boundaries

## Health endpoint

`GET /api/health` returns only `status` and the application version. It does
not reveal filesystem paths, environment values, credentials, request content,
or the deployment commit. A successful response establishes that this handler
ran; it does not test other Vercel services or prove that a deployment is
current.

## Application request logs

Handled local and hosted routes emit one JSON record after a response with
these fields: `request_id`, a fixed route label, HTTP `status`,
`response_bytes`, and `duration_ms`. The response includes the same request ID
in `X-Request-ID`.
Application logs do not include client IPs, raw paths, query values, request
headers, manifests, or report contents. The local server suppresses the
standard-library request line because it includes the raw path and address.

These are application logs. As checked on September 29, 2026, Vercel may
independently process request, network, function, and platform logs. The Vercel
project-settings connector did not return project settings during this review,
so the project's actual request retention period and Firewall rate-limit
configuration remain unverified.
Proofline has no application-level rate limiter. Do not claim zero retention or
platform rate limiting without checking the live Vercel project settings.
Vercel documents configurable Firewall rate limits in its
[rate-limiting guide](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting-sdk).

Proofline does not write manifests or reports to application storage. Hosted
requests leave the browser and reach Vercel, so use synthetic or public-safe
data until platform request retention is confirmed.

## Production rollback

Keep the last known-good production deployment identifiable by its deployment
URL and source commit. If a release causes a production issue, an authorized
operator should select that deployment in the Vercel project dashboard and
roll production back to it, then verify the production alias and health
response. Require explicit user approval before any rollback or promotion.
Vercel documents the
[production rollback procedure](https://vercel.com/docs/deployments/rollback-production-deployment).

Do not trigger production promotion or rollback from Proofline, a check runner,
or an automated request.
