FROM quay.io/jupyterhub/singleuser:4.1

USER root

RUN apt-get update -y &amp;&amp; apt-get install -y tzdata

USER jovyan

RUN conda install mamba -y && conda clean -afy
RUN mamba install nodejs=22 nano jupyterlab=4.1 jupyterlab-lsp=5.1 jupyter-lsp-python=2.2 -y && mamba clean -ay
RUN npm install pyright

RUN jupyter-labextension enable @jupyter-lsp/jupyterlab-lsp
RUN jupyter server extension enable jupyterlab_lsp
RUN jupyter server extension enable jupyter_lsp

RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/completion.jupyterlab-settings -o .jupyter/lab/user-settings/\@jupyter-lsp/jupyterlab-lsp/completion.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/manager.jupyterlab-settings -o .jupyter/lab/user-settings/\@jupyterlab/completer-extension/manager.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/notification.jupyterlab-settings -o .jupyter/lab/user-settings/\@jupyterlab/apputils-extension/notification.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/plugin.jupyterlab-settings -o .jupyter/lab/user-settings/@jupyter-lsp/jupyterlab-lsp/plugin.jupyterlab-settings
RUN wget https://raw.githubusercontent.com/fairtracks/omnipy/refs/heads/main/docker/jupyter_omnipy/config/pyright.json -o /opt/conda/etc/jupyter/jupyter_notebook_config.d/pyright.json
