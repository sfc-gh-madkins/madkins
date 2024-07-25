####STREAMLIT
# Import python packages
import streamlit as st

import json
import pandas as pd

from snowflake.snowpark.context import get_active_session
from snowflake.snowpark import functions as F
from snowflake.ml.registry import model_registry

MODEL_REGISTRY_DB = 'MILES'
MODEL_REGISTRY_SCHEMA = 'ML'

MODEL_NAME = 'MY_RANDOM_FOREST_REGRESSOR'
MODEL_VERSION = 'V1'


# Write directly to the app
st.title("Snowflake Prediction Application")

# Get the current credentials
session = get_active_session()
st.write(f'{session.get_current_role()}')
st.write(f'{session.get_current_database()}')
st.write(f'{session.get_current_schema()}')
st.write(f'{session.get_current_warehouse()}')
st.write(f'{session.sql('SHOW DATABASES').collect()}')

# Instantiate Model Registry and get model metadata
registry = model_registry.ModelRegistry(
    session=session,
    database_name=MODEL_REGISTRY_DB, schema_name=MODEL_REGISTRY_SCHEMA,
    create_if_not_exists=False
)
model_ref = registry.ModelReference(
    registry=registry, model_name=MODEL_NAME, model_version=MODEL_VERSION
)

#Get model dataset to retrieve feature store metadata
dataset_ref = model_ref.list_artifacts().where(F.col('TYPE') == 'DATASET').select('NAME', 'VERSION').collect()[0]
dataset = registry.get_artifact(dataset_ref.NAME, dataset_ref.VERSION)

#entity retrieval from model metadata
entity_join_keys = []
entity_list = json.loads(json.loads(dataset.feature_store_metadata.features[0])['feature_view_ref'])['_entities']
for entity in entity_list:
    entity_join_keys = entity_join_keys + entity['join_keys']

input_values = {}
with st.form("entity_form"):
    # Create form elements here
    for entity in entity_join_keys:
        input_value = st.text_input(f"{entity}", key=f"input_{entity}")
        input_values[entity] = input_value

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Form Submitted!")

        # Create a DataFrame from the inputs
        entity_df = pd.DataFrame([input_values])
        st.write(entity_df)

fs = FeatureStore(
    session=session,
    database=FEATURE_STORE_REGISTRY_DB,
    name=FEATURE_STORE_REGISTRY_SCHEMA,
    default_warehouse=session.get_current_warehouse()
)

feature_df = fs.retrieve_feature_values(
    entity_df, dataset.load_features())

model = model_ref.load_model()
prediction = model.predict(feature_df.to_pandas())

st.write(f'{prediction}')
