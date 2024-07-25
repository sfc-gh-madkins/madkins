DROP SERVICE IF EXISTS spcs_code_interpreter;
CREATE SERVICE spcs_code_interpreter
  IN COMPUTE POOL spcs_functions_gpu3
  FROM @spcs_functions_stage
  SPECIFICATION_FILE='/spcs/manifest2.yaml';

CREATE OR REPLACE FUNCTION code_interpreter_environment()
   RETURNS VARCHAR
   SERVICE = spcs_code_interpreter
   ENDPOINT='code-interpreter-http'
   AS '/environment';

CREATE OR REPLACE FUNCTION code_interpreter_execute(python_code VARCHAR)
   RETURNS VARCHAR
   SERVICE = spcs_code_interpreter
   ENDPOINT='code-interpreter-http'
   AS '/execute';

CREATE OR REPLACE FUNCTION code_interpreter_restart()
   RETURNS VARCHAR
   SERVICE = spcs_code_interpreter
   ENDPOINT='code-interpreter-http'
   AS '/restart';