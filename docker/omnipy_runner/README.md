## The Omnipy runner image

A slim image with Python and Omnipy, used by engines that run jobs on other machines, such as a
TES engine. A job runs as `python -m omnipy run <module:job> <bundle dir>`. The user's own code
and its dependencies are installed per job, so the image only holds Omnipy and its dependencies.

For each release, the "Publish release" workflow (`.github/workflows/release.yml`) builds the
image for each supported Python version, for `linux/amd64` and `linux/arm64`, and pushes it to
the GitHub Container Registry as:

```text
ghcr.io/fairtracks/omnipy_runner:<omnipy version>-py<python version>
```

for example `ghcr.io/fairtracks/omnipy_runner:0.24.0-py3.12`. Engines pick the tag from the
Omnipy and Python versions of the submitting side, as the versions must match.

To build the image by hand for a released version:

```bash
cd docker/omnipy_runner
docker build --build-arg OMNIPY_VERSION=0.xx.yy --build-arg PYTHON_VERSION=3.12 \
    -t omnipy_runner:0.xx.yy-py3.12 .
```

To build a development image from a checkout, build the wheel first and pass its directory as
the `wheels` build context:

```bash
uv build --wheel
docker build --build-context wheels=dist --build-arg PYTHON_VERSION=3.12 \
    -t omnipy_runner:dev-py3.12 docker/omnipy_runner
```

The build runs `pip check`, so an image with inconsistent dependencies fails to build.
