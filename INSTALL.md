# Installation and usage of omnipy

## Installation

`pip install omnipy`


## Run example scripts:
  - Install `omnipy-examples`:
    - `pip install omnipy-examples`
  - Example script:
    - `omnipy-examples isajson`
  - For help on the command line interface:
    - `omnipy-examples --help`
  - For help on a particular example:
    - `omnipy-examples isajson --help`

### Output of flow runs

The output will by default appear in the `data` directory, with a timestamp. 

  - It is recommended to install a file viewer that are capable of browsing tar.gz files. 
    For instance, the "File Expander" plugin in PyCharm is excellent for this.
  - To unpack the compressed files of a run on the command line 
    (just make sure to replace the datetime string from this example): 

```
for f in $(ls data/2023_02_03-12_51_51/*.tar.gz); do mkdir ${f%.tar.gz}; tar xfzv $f -C ${f%.tar.gz}; done
```
    
### Run with the Prefect engine

Omnipy is integrated with the powerful [Prefect](https://prefect.io) data flow orchestration library.

- To run an example using the `prefect` engine, e.g.:
  - `omnipy-examples --engine prefect isajson`
- After completion of some runs, you can check the flow logs and orchestration options in the Prefect UI:
  - `prefect orion start`

More info on Prefect configuration will come soon...
