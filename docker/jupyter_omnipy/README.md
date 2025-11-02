## Build and push multi-platform Docker image on MacOS
### Install multipass
Follow installation instructions: https://canonical.com/multipass/install

### Setup Docker on multipass
Instructions: https://documentation.ubuntu.com/multipass/en/latest/how-to-guides/manage-instances/run-a-docker-container-in-multipass/#alias-of-the-docker-commands

Example:
- Launch docker VM:
```bash
multipass launch docker --name docker-dev --cpus 6 --memory 10G --disk 100G --bridged
```

- Add to `~/.zshrc` (or `~/.bashrc`):
```
export PATH="$PATH:$HOME/Library/Application Support/multipass/bin"
```

- Setup QEMU and buildx inside docker VM:
```bash
multipass shell docker-dev
docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
docker buildx create --name builder
docker buildx inspect --bootstrap
exit
```

- Log in to Docker Hub:
```bash
docker login
```

- Build the image:
```bash
cd docker/jupyter_omnipy
multipass transfer -r * docker-dev:
docker buildx build --platform linux/amd64,linux/arm64 -t fairtracks/jupyter_omnipy:0.xx.yy --push .
```

## Update JupyterLab installation on OpenStack
- Log in to OpenStack VM and pull the new Docker image:
```bash
ssh -i .ssh/<rsa-file-name> alma@<openstack-ip>
sudo -s
su - jupyter
docker pull fairtracks/jupyter_omnipy:0.xx.yy
```

- Edit `jupyterhub_config.py`:
```python
c.DockerSpawner.image = 'docker.io/fairtracks/jupyter_omnipy:0.xx.yy'
```

- Make sure that python packages "ipyvue" and "ipyvuetify" are installed
in the EXACT same version as in the Docker image. If not, the reactive
Omnipy output widgets might not work.
```bash
pip list | grep ipyvue
```

- To check the versions in the Docker container, run:
```bash
docker run --rm fairtracks/jupyter_omnipy:0.xx.yy conda run -n omnipy /bin/bash -c "pip list | grep ipyvue"
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
