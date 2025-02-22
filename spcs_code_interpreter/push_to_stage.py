import os
import sys
from snowflake.snowpark import Session

def list_files_and_folders(path):
    result = []
    for root, dirs, files in os.walk(path):
        # Exclude directories starting with a dot or underscore
        dirs[:] = [d for d in dirs if not (d.startswith('.') or d.startswith('_'))]
        for file in files:
            result.append(os.path.join(root, file))
    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Please provide the password as an argument.")
        sys.exit(1)

    password = sys.argv[1]

    # Usage example
    directory_path = os.getcwd()
    result = list_files_and_folders(directory_path)

    connection_params = {
        'account': 'awb48767',
        'user': 'madkins',
        'password': password,
        'role': 'MILES',
        'warehouse': 'MILES_WH',
        'database': 'MILES',
        'schema': 'SPCS_FUNCTIONS'
    }

    session = Session.builder.configs(connection_params).create()

    query = '''
        create or replace stage spcs_functions_stage
            ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
    '''

    session.sql(query).collect()

    for file in result:
        query = f'''
            put file://{file} @spcs_functions_stage{file[:file.rfind('/')].replace(os.getcwd(),'')}
            auto_compress=false overwrite=true;
        '''
        print(file)
        session.sql(query).collect()
