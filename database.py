import sqlite3


class SQLiteDatabase:
    """
    SQLite Database Class. Each object can be attached to a single database file/location.
    """
    def __init__(self, empty_results_dict, table_name='properties', file_path='saved_properties.db'):
        self.file_path =file_path
        self.initalise_db_table(empty_results_dict, table_name)

    def initalise_db_table(self, empty_results_dict, table_name):
        """
        Check to see if given table exists within the attached database file (self.file_path)
        If it doesn't, then create such a table, creating a schema based upon empty_results_dict
        If it does exist, do nothing

        :param empty_results_dict: dict, keys will be column names
        :param table_name: name for table in SQLite db file
        :return:
        """
        # Connect to a database (or create it if it doesn't exist)
        conn = sqlite3.connect(self.file_path)

        # Create a cursor to interact with the database
        cursor = conn.cursor()

        # Check to see if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")

        # If it exists, do nothing
        if cursor.fetchone():
            pass

        # If it doesn't exist, create table
        else:
            # Extract column names and data types from the dictionary
            columns = ', '.join(f'{key} TEXT' for key in empty_results_dict.keys())

            # Create the table
            create_table_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({columns});'
            cursor.execute(create_table_query)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def insert_data_into_table(self, data_dict, table_name = 'properties'):
        """
        Saves a Python dict to an SQLite database table, each key in the dict corresponds to a column heading.
        This schema is set up on object instantiation - i.e. self.__init__()
        :param data_dict:
        :return:
        """
        if not self.does_row_exist(data_dict['id'], table_name=table_name):
            # Connect to the SQLite database
            conn = sqlite3.connect(self.file_path)
            cursor = conn.cursor()

            # Generate the query to insert data into the table
            columns = ', '.join(data_dict.keys())

            # Remove any " characters from the values to ensure the SQL query isn't prematurely escaped
            disallowed_chars = ['"']
            values = ', '.join([f'"{str(value).replace(disallowed_chars[0], "")}"' for value in data_dict.values()])
            insert_query = f'INSERT INTO {table_name} ({columns}) VALUES ({values});'

            # Execute the query
            cursor.execute(insert_query)

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

        else:
            print('Database entry already exists for this id - skipping')

    def fetch_data_by_id(self, property_id, table_name='properties'):
        """
        Fetch a row of data from the SQLite database, returning the row as a dict keyed by column name

        str property_id: id of row to fetch from database
        str table_name: optional, default = properties, name of table to fetch data from
        """

        # Connect to the SQLite database
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        # Create query to select data by ID
        select_query = f'SELECT * FROM {table_name} WHERE id = {property_id};'

        # Execute the query
        cursor.execute(select_query)

        # Fetch the result
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        # Convert the result to a dictionary
        if result:
            columns = [column[0] for column in cursor.description]
            data_dict = dict(zip(columns, result))
            return data_dict
        else:
            print(f'Result not found for id: {id}')
            return None

    def does_row_exist(self, property_id, table_name='properties'):
        """
        Check if a row exists for a certain key/id value. Returns boolean

        :param property_id: str, property_id/primary key in table
        :param table_name: table name to check
        :return: boolean
        """
        # Connect to the database
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        # Check if a row with the specified ID exists in the 'properties' table
        select_query = f'SELECT 1 FROM {table_name} WHERE id = {property_id} LIMIT 1'
        cursor.execute(select_query)

        # cursor.execute('''
        #     SELECT 1 FROM properties WHERE id = ? LIMIT 1
        # ''', (property_id,))

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Return True if a row exists, False otherwise
        return result is not None

    def get_unnotified_property_ids(self, table_name='properties'):
        """
        Return a list of property ids/row primary keys that have a value of '0' corresponding to column 'notified'

        :param table_name: optional, name of table to query against
        :return:
        """
        # Connect to the database
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        # Fetch IDs of properties with notified set to False
        select_query = f'SELECT id, rental_platforms FROM {table_name} WHERE notified = 0'
        cursor.execute(select_query)

        # cursor.execute('''
        #     SELECT id, rental_platforms FROM properties WHERE notified = 0
        # ''')

        # Retrieve the results
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Extract the IDs from the results and return as a list
        # return [result[0] for result in results]
        return results

    def get_all_property_ids(self, table_name='properties'):
        """
        Return a list of all values in column 'id' from SQLite table
        :param table_name:
        :return:
        """
        # Connect to the database
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        # Fetch all IDs from the table
        select_query = f'SELECT id from {table_name}'
        cursor.execute(select_query)

        # cursor.execute('''
        #     SELECT id FROM properties
        # ''')

        # Retrieve the results
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        # Extract the IDs from the results and return as a list
        return [result[0] for result in results]

    def get_position(self, id, values=['price', 'time_to_work_pub_trans'], table_name='properties'):

        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        results = {}

        for value in values:

            query = f'''
                SELECT position
                FROM (
                    SELECT id, ROW_NUMBER() OVER (ORDER BY {value}) AS position
                    FROM {table_name}
                ) AS ranked
                WHERE id = ?;
            '''

            cursor.execute(query, (id,))
            result = cursor.fetchone()

            if result:
                position = result[0]
                results[value] = position
            else:
                print(f"No row found with id {id}")

        conn.close()

        return results

    def get_entry_count(self, table_name='properties'):
        """
        Get total number of entries/rows within a SQLite table
        :param table_name: name of table within SQLite db
        :return: count (int)
        """
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        query = f'SELECT COUNT(*) FROM {table_name};'
        cursor.execute(query)

        count = cursor.fetchone()[0]

        conn.close()

        return int(count)


    def update_column_by_id(self, id, column_name, new_value, table_name='properties'):
        """
        Update a single value in an SQLite table by specifying the 'id' (row) and 'column_name' (col)

        :param id: id of row entry
        :param column_name: name of column in which value will be updated
        :param new_value: value to be written to the db
        :param table_name: name of table within SQLite db
        :return:
        """
        conn = sqlite3.connect(self.file_path)
        cursor = conn.cursor()

        query = f'UPDATE {table_name} SET {column_name} = ? WHERE id = ?;'
        cursor.execute(query, (new_value, id))

        # Commit the changes
        conn.commit()

        print(f'Column "{column_name}" updated for row with id {id}.')

        conn.close()




