from unifair.modules.fairtracks.tasks import import_dataset_from_encode
from unifair.modules.fairtracks.util import \
    serialize_to_tarpacked_csv_files as u_serialize_to_tarpacked_csv_files
from unifair.modules.tables.tasks import convert_to_1nf, remove_columns

# I have tried out a new organising principle: Modules. Modules are a collections of
# related dataset types, models, tasks, flows, and utilities, of a somewhat general nature
# (in the context of the module). I have moved the content from this file to modules according to
# the context of their generality.

# I have also tried out a naming scheme for objects, m_model, t_task, d_dataset, f_flow, u_utility.
# Might make the code more readable, but might also just be a nuisance. Any thoughts are welcome.

# The data import task is imported from the FAIRtracks module and is 'refined' here into a new
# TaskTemplate which only downloads 25 items for each endpoint (max_data_item_count is fixed to 25).

t_import_some_data_from_encode = import_dataset_from_encode.refine(
    name='t_import_some_data_from_encode',
    fixed_params=dict(max_data_item_count=25),
).apply()

# Also, the TaskTemplate objects are converted to Task objects by applying the TaskTemplate to a
# specific runtime environment. Currently, there are no runtimes or engines to be applied to, so
# there are no parameters specified for the 'apply()' method. This will come later. Calling apply()
# needs to be done manually for each task now, but will later only need to be done one time
# for each flow, and possibly not even that.

t_remove_columns = remove_columns.apply()
t_convert_to_1nf = convert_to_1nf.apply()

# # This will change to e.g.:
#
# runtime = RuntimeConfig(engine=PrefectEngine(...), ...)
# remove_columns = remove_columns.apply(runtime)

# As flows are not fully implemented, we will call the tasks directly in the code.

d_encode_json = t_import_some_data_from_encode(endpoints=['experiment', 'biosample'])
d_encode_json_pruned = t_remove_columns(
    d_encode_json, column_keys_for_data_items=dict(experiment=['audit'], biosample=['audit']))

# Temporary utility method to write datasets as tar-packed CSV files into the top-level data dir
# BTW: There is a PyCharm plugin named "File Expander" which shows tarballs in the project view
# as regular directories, which is very useful.

u_serialize_to_tarpacked_csv_files('encode_json_pruned', d_encode_json_pruned)

d_encode_1nf_dataset = t_convert_to_1nf(d_encode_json_pruned)

print(d_encode_1nf_dataset.to_json(pretty=True))
