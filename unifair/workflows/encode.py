from unifair.core.data import NoData
from unifair.core.workflow import Workflow
from unifair.steps.imports.encode import ImportEncodeMetadataFromApi


def create_encode_workflow():
    encode_workflow = Workflow()
    encode_workflow.add_step(ImportEncodeMetadataFromApi())

    return encode_workflow


if __name__ == "__main__":
    workflow = create_encode_workflow()
    output = workflow.run(NoData())
    print(output)
