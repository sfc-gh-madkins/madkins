-- Setup script for the Hello Snowflake! application.

CREATE APPLICATION ROLE app_public;

CREATE OR ALTER VERSIONED SCHEMA code;
CREATE SCHEMA data CLONE feature_store;
GRANT USAGE ON SCHEMA code TO APPLICATION ROLE app_public;
GRANT USAGE ON SCHEMA data TO APPLICATION ROLE app_public;

CREATE VIEW IF NOT EXISTS data.wine_features$v1app AS SELECT * FROM feature_store.wine_features$v1app;
GRANT SELECT ON VIEW data.wine_features$v1app TO APPLICATION ROLE app_public;


CREATE OR REPLACE PROCEDURE code.hello()
  RETURNS STRING
  LANGUAGE SQL
  EXECUTE AS OWNER
  AS
  BEGIN
    RETURN 'Hello Snowflake!';
  END;
  GRANT USAGE ON PROCEDURE code.hello() TO APPLICATION ROLE app_public;


CREATE OR REPLACE FUNCTION code.addone(i int)
RETURNS INT
LANGUAGE PYTHON
RUNTIME_VERSION = '3.8'
HANDLER = 'addone_py'
AS
$$
def addone_py(i):
  return i+1
$$;
GRANT USAGE ON FUNCTION code.addone(int) TO APPLICATION ROLE app_public;


CREATE STREAMLIT code.streamlit_prediction_app
  FROM '/src/app'
  MAIN_FILE = '/streamlit.py'
;
GRANT USAGE ON STREAMLIT code.streamlit_prediction_app TO APPLICATION ROLE app_public;
