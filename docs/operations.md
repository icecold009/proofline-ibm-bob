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

These are application logs. As checked on September 29, 2026, the Vercel
dashboard identifies this project under a Hobby team. Vercel documents a
one-hour retention period for Hobby runtime logs; this is platform log
retention, not application storage, and does not establish the retention of
every request, network, or billing record. See Vercel's
[runtime log limits](https://vercel.com/docs/logs/runtime) and
[Hobby plan limits](https://vercel.com/docs/plans/hobby).

The live Firewall dashboard showed system mitigations active, zero custom
project rules, no enforced rules, and no rate-limited requests in its selected
past-day window. Proofline has no application-level rate limiter, and this
project has no configured custom Firewall rate limit. System mitigations are
not a per-project request-rate policy. Do not claim that requests are rate
limited by this project. Vercel documents configurable Firewall rate limits
in its [rate-limiting guide](https://vercel.com/docs/vercel-firewall/vercel-waf/rate-limiting-sdk).

Proofline does not write manifests or reports to application storage. Hosted
requests leave the browser and reach Vercel, where function runtime logs are
retained for one hour on the observed Hobby plan. The retention of other
platform request, network, or billing records is not established here. Use
synthetic or public-safe data on hosted routes.

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
