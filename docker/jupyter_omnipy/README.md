## The Docker image
For each release, the "Publish release" workflow (`.github/workflows/release.yml`) builds the
image for `linux/amd64` and `linux/arm64` and pushes it to the GitHub Container Registry as
`ghcr.io/fairtracks/jupyter_omnipy:<version>` and `ghcr.io/fairtracks/jupyter_omnipy:latest`.

To build the image by hand, pass the released version of Omnipy to install:
```bash
cd docker/jupyter_omnipy
docker build --build-arg OMNIPY_VERSION=0.xx.yy -t jupyter_omnipy:0.xx.yy .
```

## Update JupyterLab installation on OpenStack
- Log in to OpenStack VM and pull the new Docker image:
```bash
ssh -i .ssh/<rsa-file-name> alma@<openstack-ip>
sudo -s
su - jupyter
docker pull ghcr.io/fairtracks/jupyter_omnipy:0.xx.yy
```

- Edit `jupyterhub_config.py`:
```python
c.DockerSpawner.image = 'ghcr.io/fairtracks/jupyter_omnipy:0.xx.yy'
```

- Make sure that python packages "ipyvue" and "ipyvuetify" are installed
in the EXACT same version as in the Docker image. If not, the reactive
Omnipy output widgets might not work.
```bash
pip list | grep ipyvue
```

- To check the versions in the Docker container, run:
```bash
docker run --rm ghcr.io/fairtracks/jupyter_omnipy:0.xx.yy conda run -n omnipy /bin/bash -c "pip list | grep ipyvue"
```

- If the versions differ from the ones in the Docker container, install the correct versions:
```bash
pip install ipyvue==<version>
pip install ipyvuetify==<version>
```

- Restart JupyterHub:
```bash
killall jupyterhub
./run_all.sh
```
