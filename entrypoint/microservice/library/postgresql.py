import psycopg2


class PostgresQL:
    """Connection to the PostgresQL database

    Args:
        host (str): The host address. (Default "127.0.0.1")
        port (str): The port number. (Default "5432")

    """

    def __init__(self, host="127.0.0.1", port="5432"):
        self.host = host
        self.port = port


    def connect(self, database, password, user="postgres"):
        """Connects to the database with the provided user and password

        Args:
            database (str): The database name.
            password (str): The password of the user.
            user (str): The postgresql user. (Default "postgres")
        """

        try:
            # create a connection
            self.connection = psycopg2.connect(
                user = user,
                password = password,
                host = self.host,
                port = self.port,
                database = database
            )

            # store the connection cursor
            self.cursor = self.connection.cursor()

        except (Exception, psycopg2.Error) as error:
            # notify the user about the error
            self.cursor = None


    def disconnect(self):
        """Disconnect the postgresql connection to the database"""
        if self.connection:
            self.cursor.close()
            self.connection.close()


    def execute(self, statement, params=None):
        """Execute the provided statement

        Args:
            statement (str): The postgresql statement to be executed.
            params (tuple): values to be formatted into the statement. (Default = None)

        Returns:
            list: a list of tuples containing the postgresql records.

        """
        if self.cursor is None:
            raise Exception("The connection is not established")
        else:
            if params is None:
                self.cursor.execute(statement)
            else:
                self.cursor.execute(statement, params)
            if self.cursor.description is not None:
                num_fields = len(self.cursor.description)
                field_names = [i[0] for i in self.cursor.description]
                return [{ field_names[i]: row[i] for i in range(num_fields) } for row in self.cursor.fetchall()]
            else:
                return None
        
    def executemany(self, statement, values=[]):
        """
        Implements self.cursor.executemany(). Provide statement and list of values to be used.

        Example:
        statement = "INSERT INTO test (id, ime) VALUES (%s, %s)"
        values = [(3, 'Andraz'), (4, 'Blaz'), (5, 'Cene')]

        This function will add all those pairs into the table `test`.
        """

        if self.cursor is None:
            raise Exception("The connection is not established")
        self.cursor.executemany(statement, values)
        # Commit the changes to the database
        self.connection.commit() 
        return True


    def get_documents_from_db(self, document_ids):
        """
        Function receives a list of document ids and returns a list of dictionaries of documents data.

        Parameters:
            documents_ids : list(int)
                list of document ids

        Returns:
            success (boolean), list of dictionaries of document data if the extraction from the database was successful.
        """

        statement = "SELECT * FROM documents WHERE document_id IN %s;"
        try:
            documents = self.execute(statement, [tuple(document_ids)])
        except Exception as e:
            return False, {'Error' : 'You provided invalid document ids.'}

        # Cleaning the output:
        # - removing fulltext field
        # - slicing down the fulltext_cleaned field to 500 chars
        # - we return only the first 10 results
        for i in range(len(documents)):
            if documents[i]['fulltext_cleaned'] is not None:
                documents[i]['fulltext_cleaned'] = documents[i]['fulltext_cleaned'][:500]
            documents[i].pop('fulltext')

        return True, documents
    
    def add_document_to_db(self, document_data):
        """
        Function will add document with `document_data` to the database. If any of the fields are not given
        those fields will be set to None. You have to provide atleast title of the document.

        This method will also try to call annotations service and also add those annotations.
        """

        metadata_fields = ['title', 'document_source', 'fulltext', 'abstract', 'date',
        'entryintoforce', 'fulltextlink', 'sourcename', 'sourcelink', 'status']

        add_metadata_statement = "INSERT INTO documents ("
        add_metadata_statement += ', '.join(metadata_fields)
        add_metadata_statement += ') VALUES (' + ', '.join(['%s']*len(metadata_fields))
        add_metadata_statement += ') ON CONFLICT DO NOTHING RETURNING document_id'

        data = [document_data.get(attribute, None) for attribute in metadata_fields]
        returned_data = self.execute(add_metadata_statement, data)
        self.connection.commit()

        document_id = returned_data[0]['document_id']

        add_authors_statement = "INSERT INTO document_authors (document_id, author) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        author_values = [(document_id, author) for author in document_data.get('authors', [])]
        self.executemany(add_authors_statement, author_values)

        add_areas_statement = "INSERT INTO document_areas (document_id, area) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        areas_values = [(document_id, area) for area in document_data.get('areas', [])]
        self.executemany(add_areas_statement, areas_values)

        add_keywords_statement = "INSERT INTO document_keywords (document_id, keyword) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        keywords_values = [(document_id, area) for area in document_data.get('keywords', [])]
        self.executemany(add_keywords_statement, keywords_values)

        add_subjects_statement = "INSERT INTO document_subjects (document_id, subject) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        subjects_values = [(document_id, area) for area in document_data.get('subjects', [])]
        self.executemany(add_subjects_statement, subjects_values)

        add_participants_statement = "INSERT INTO document_participants (document_id, participant) VALUES (%s, %s) ON CONFLICT DO NOTHING"
        participants_values = [(document_id, area) for area in document_data.get('participants', [])]
        self.executemany(add_participants_statement, participants_values)

        # TODO add annotations, ontology, wikipedia concepts to the db.