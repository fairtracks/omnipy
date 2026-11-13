# Configuration

Reference configuration options for runtime, model behavior, and execution settings.

This section is coming soon — check back as Omnipy evolves.

For the rate limiting of HTTP requests per host (`requests_per_time_period`,
`time_period_in_secs` and `burst_ratio`), see
[Rate limiting of HTTP requests](../learn/rate-limiting.md#configuration).

## Secrets and machine-local values

Secret settings, such as the S3 access key and secret key under
`runtime.config.job.output_storage.s3`, use pydantic's `SecretStr`. They are masked when the
config is displayed. Read the value with `get_secret_value()`.

Some settings belong to the current machine: file paths, detected values such as the user
interface type, and the log output streams. Their fields are marked with `MACHINE_LOCAL` from
`omnipy.config`.

## Portable config export

`to_portable_dict()` on any config section returns its values as JSON-compatible data, leaving out
secrets and machine-local values. `update_from_portable_dict()` applies such data to a config on
another machine, updating nested sections in place:

```python
import json

import omnipy as om

portable = json.dumps(om.runtime.config.to_portable_dict())

# On another machine:
om.runtime.config.update_from_portable_dict(json.loads(portable))
```

Jobs that run remotely use this to run with the same settings as on the submitting machine.

## S3 output storage

Persisted outputs can be written to S3-compatible storage instead of a local directory. This
needs the `s3` extra:

```console
$ pip install "omnipy[s3]"
```

```python
import omnipy as om

s3 = om.runtime.config.job.output_storage.s3
s3.endpoint_url = 'https://s3.example.org'  # leave empty for AWS
s3.bucket_name = 'my-bucket'
s3.access_key = '...'
s3.secret_key = '...'
om.runtime.config.job.output_storage.protocol = 's3'
```

Outputs are then written under `s3://<bucket>/<persist_data_dir_path>/`, in the same run folders
as locally, and restored from there. Without keys, the usual AWS credential sources apply, such
as environment variables. `omnipy.hub.output_storage` also has functions for uploading,
downloading and listing files in the same storage.
