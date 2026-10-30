# inf-003 — SQS queues, DLQs and least-privilege IAM in Terraform

- Repo: `ecom-infra`
- Phase: P1 · priority: P0 · kind: infra · transport: infra
- Started: 2026-10-30 · Finished: 2026-10-30

## What

`ecom-infra/aws/` now holds the whole SQS surface, executable against LocalStack
with no AWS account:

| File | Contents |
|---|---|
| `versions.tf` | `terraform >= 1.9`, `hashicorp/aws ~> 5.0` |
| `providers.tf` | `local.localstack = var.endpoint != ""`; dummy key/secret, `skip_credentials_validation`, `skip_requesting_account_id`, `skip_metadata_api_check`, and `endpoints { sqs, iam }` only when an endpoint is set |
| `variables.tf` | `region` (`us-east-1`), `endpoint` (`""`), `queue_prefix` (`""`), `max_receive_count` (5), visibility 60, retention 1209600, wait 20 |
| `sqs.tf` | three queues + three DLQs via `for_each`, `sqs_managed_sse_enabled = true`, `redrive_policy` → its own `-dlq` |
| `iam.tf` | one role per queue (`ecs-tasks.amazonaws.com`), a policy limited to that queue's ARN, read-only on its DLQ |
| `outputs.tf` | queue/role ARNs and the DLQ names, so a service can be pointed at them without reading Terraform state |

Leaving `endpoint` empty points the same configuration at real AWS; nothing else
changes.

## LocalStack has to serve IAM

`SERVICES: sqs,iam` in the compose file. Without `iam`, `apply` fails at the
first role — the queues and the policies both have to be creatable for the plan
to be a real plan.

## SQS forbids dots — the naming decision

The design notes called the queues `notify.send-email`, `import.process-row`,
`media.resize-image`. LocalStack rejected the first one:

```
InvalidParameterValue: Value ... for parameter QueueName is invalid.
Can only include alphanumeric characters, hyphens, or underscores. 1 to 80 in length.
```

A dot is legal only as the trailing `.fifo`. The canonical names are therefore
**hyphenated**: `notify-send-email`, `import-process-row`, `media-resize-image`,
each with a `-dlq` twin. The change had to land in three places at once — the
init hook, this Terraform, and the contract registry (`inf-003` → `ec-003`);
`TASK_QUEUES` in `@ecom/contracts@1.8.0` is now the single source of truth and the
tests pin the values the other two use.

## Verification (a real apply, not a plan)

```powershell
docker run --rm -v "${PWD}/aws:/tf" -w /tf hashicorp/terraform:1.9 fmt -check   # clean
docker run --rm -v "${PWD}/aws:/tf" -w /tf hashicorp/terraform:1.9 init
docker run --rm -v "${PWD}/aws:/tf" -w /tf hashicorp/terraform:1.9 validate     # Success
```

A throwaway apply against LocalStack with `-var queue_prefix=tfcheck-` created
**15 resources** (3 queues + 3 DLQs + 3 roles + 3 policies + 3 attachments), and a
second script asserted **18/18**: each `redrivePolicy` points at its own `-dlq`
with `maxReceiveCount 5`; retention 14d, visibility 60s, receive-wait 20s; SSE
enabled; no `"*"` resource in any policy; every ARN scoped to its own queue.
`terraform destroy` then removed all 15, and `verify-stack` stayed at 31/31, so
the dev queues were never touched.

## Decisions

| Decision | Why | Rejected |
|---|---|---|
| `queue_prefix` variable rather than a workspace | a test apply must not be able to collide with the dev queues, and the guard has to be impossible to forget | `terraform workspace` (one wrong `select` and you are in the dev queue) |
| Per-queue role, not one shared role | least privilege is the acceptance criterion; a shared role is the thing that later becomes `sqs:*` | one `ecom-tasks` role with a wildcard policy |
| `sqs_managed_sse_enabled = true` | free, and a queue that cannot be encrypted later without a migration | customer-managed KMS (cost, no local benefit) |
| Endpoints only when `var.endpoint != ""` | the same files must be valid for real AWS | a separate `localstack.tf` overlay that drifts |

## Open

- `aws/` is committed without a `backend` block (local state). Before a real
  environment exists it needs an S3+DynamoDB backend, or `apply` runs on one
  laptop only.
- `terraform.tfstate*` from the throwaway apply was deleted; `.terraform/` is
  git-ignored and `.terraform.lock.hcl` is committed.
