import os
import sys

from unifair.core.workflow import Workflow
from unifair.steps.imports.gdc import ImportGDCMetadataFromApi


def create_gdc_workflow():
    encode_workflow = Workflow()
    encode_workflow.add_step(ImportGDCMetadataFromApi())

    return encode_workflow


if __name__ == '__main__':
    workflow = create_gdc_workflow()
    print(os.path.abspath(sys.argv[1]))
    output = workflow.run(sys.argv[1])
    print(output)
