import streamlit as st
import pandas as pd
import sqlite3
import base64  # for encoding images
import os
from io import StringIO

# ### Configuration ###
# SQLITE_DB_PATH = "data.db"  # No longer hardcoding, will use in-memory or user-provided

### Initialize Database Connection ###
def get_sqlite_connection(db_path=":memory:"):
    """
    Returns a connection to the SQLite database. Now takes a db_path.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None  # Important: Return None on error

### Helper Functions ###
def fetch_data(conn, query, params=()):
    """
    Fetches data from the database using a parameterized query.
    Takes a database connection as an argument.
    """
    if conn is None:
        return pd.DataFrame()  # Return empty DataFrame on connection error
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on query error

### 3D Visualization Component (Placeholder) ###
def st_3d_viewer(pdb_file_content):
    """
    Placeholder for the 3D molecular structure viewer. Now takes PDB file content.
    """
    # st.write("3D Structure Viewer (Placeholder)")
    # st.write(f"PDB File Content: {pdb_file_content[:100]}...")  # Show the first 100 characters

    # Try to display a static image if possible
    try:
        # st.image(image_path, caption="3D Structure (Placeholder)", use_column_width=True)
        st.warning("3D structure visualization is not fully implemented.  A placeholder is shown.")
    except Exception:
        st.warning("3D structure visualization is not fully implemented. A placeholder is shown.")
    st.write("3D structure visualization is not fully implemented.  A placeholder is shown.")
    st.write(f"PDB File: {pdb_file_content[:100]}...")

### Data Loading Functions ###
def load_data_from_csv(file_path, table_name, conn):
    """
    Loads data from a CSV file into a specified table in the SQLite database.
    """
    try:
        df = pd.read_csv(file_path)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        st.success(f"Data from {file_path} loaded into table {table_name} successfully.")
        return True
    except Exception as e:
        st.error(f"Error loading data from {file_path} into {table_name}: {e}")
        return False

def load_data_from_dataframe(df, table_name, conn):
    """Loads data from a Pandas DataFrame to a SQLite table"""
    try:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        st.success(f"Data from DataFrame loaded into table {table_name} successfully.")
        return True
    except Exception as e:
        st.error(f"Error loading data into {table_name}: {e}")
        return False

def create_database_tables(conn):
    """
    Creates the necessary tables in the SQLite database.
    """
    try:
        cursor = conn.cursor()
         #  EGFR Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS egfr (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gene_name TEXT NOT NULL,
                uniprot_accession TEXT NOT NULL,
                sequence TEXT,
                domain_structure TEXT
            )
        """)

        #  Aptamer Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aptamers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aptamer_id TEXT NOT NULL,
                sequence TEXT NOT NULL,
                sequence_modified TEXT,
                length INTEGER,
                target TEXT,
                binding_affinity REAL,
                modifications TEXT,
                stability_data TEXT,
                delivery_methods TEXT,
                toxicity_data TEXT,
                citations TEXT,
                notes TEXT
            )
        """)

          # Interaction Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aptamer_id INTEGER,
                egfr_id INTEGER,
                interaction_type TEXT NOT NULL,
                distance REAL,
                angle REAL,
                interacting_atoms TEXT,
                interacting_residues TEXT,
                FOREIGN KEY (aptamer_id) REFERENCES aptamers(id),
                FOREIGN KEY (egfr_id) REFERENCES egfr(id)
            )
        """)
        conn.commit()
        st.success("Database tables created (if they didn't exist).")
    except Exception as e:
        st.error(f"Error creating database tables: {e}")
    # finally: # Removed finally, the connection is handled in main()
    #     conn.close()

### Main Streamlit App ###
def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("GlioTarget Aptamer Explorer")
    st.markdown(
        """
        Explore EGFR-targeting aptamers and their interactions for potential glioblastoma therapies.
        Upload your data to get started.
        """
    )

    # --- Initialize Database Connection ---
    # Use an in-memory database by default
    conn = get_sqlite_connection()
    if conn is None:
        st.stop()  # Stop if database connection fails

    # Create tables
    create_database_tables(conn)

    # --- Data Upload Section ---
    st.sidebar.title("Data Upload")
    data_source = st.sidebar.selectbox(
        "Choose data source", ["Upload CSV", "Upload PDB", "Enter Data via DataFrame"]
    )

    if data_source == "Upload CSV":
        csv_file = st.sidebar.file_uploader("Upload CSV File", type="csv")
        table_name = st.sidebar.text_input("Table Name", "my_data")  # default table name
        if csv_file:
            # To avoid issues with file paths, use the file object directly.
            if load_data_from_csv(csv_file, table_name, conn):
                #st.success(f"CSV data loaded into table: {table_name}") # handled in function
                pass # moved message to function
            else:
                st.error("Failed to load CSV data.")

    elif data_source == "Enter Data via DataFrame":
        st.sidebar.subheader("Enter Data for a Table")
        table_name = st.sidebar.text_input("Table Name for DataFrame", "my_df_table")
        # Example DataFrame (replace with a text area for TSV input)

        # Use a text area for tab-separated data input
        tsv_data = st.sidebar.text_area("Enter data as TSV",
                                       "id\tgene_name\tuniprot_accession\tsequence\tdomain_structure\n"
                                       "1\tEGFR\tP00533\tExampleSequence\tExampleDomain",
                                       height=200)  # Adjust height as needed

        if st.sidebar.button("Load TSV Data"):
            try:
                # Read the TSV data using StringIO
                df = pd.read_csv(StringIO(tsv_data), sep='\t')
                # st.write(df)  # Display the DataFrame to verify
                if load_data_from_dataframe(df, table_name, conn):
                    pass
                else:
                    st.error("Failed to load DataFrame data")

            except Exception as e:
                st.error(f"Error reading TSV data: {e}")

    elif data_source == "Upload PDB":
        pdb_file = st.sidebar.file_uploader("Upload PDB File", type="pdb")
        if pdb_file:
            # Read the PDB file content
            pdb_file_content = pdb_file.read().decode("utf-8")
            # Store PDB content or path for later use
            st.session_state.pdb_content = pdb_file_content
            st.success("PDB file uploaded successfully.")

    # --- Main Content ---
    # st.session_state.get('pdb_content', None)
    # --- Sidebar ---
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(
        "Select a section", ["EGFR Data", "Aptamer Data", "Interaction Data", "3D Viewer"]
    )
    # --- EGFR Data Page ---
    if selected_page == "EGFR Data":
        st.header("EGFR Data")
        # Now the connection is passed to fetch_data
        egfr_data = fetch_data(conn, "SELECT * FROM egfr")
        if not egfr_data.empty: # Check if the dataframe is empty
            st.dataframe(egfr_data, use_container_width=True)
        else:
            st.warning("No EGFR data available.")

        egfr_id = st.selectbox("Select EGFR ID to view details", egfr_data["id"].tolist() if not egfr_data.empty else [])
        if egfr_id:
            egfr_details = fetch_data(conn, "SELECT * FROM egfr WHERE id = ?", (egfr_id,))
            if not egfr_details.empty:
                st.subheader(f"EGFR Details (ID: {egfr_id})")
                st.write(egfr_details.to_dict())
            else:
                st.error("EGFR not found.")

    # --- Aptamer Data Page ---
    elif selected_page == "Aptamer Data":
        st.header("Aptamer Data")
        aptamer_data = fetch_data(conn, "SELECT * FROM aptamers")
        if not aptamer_data.empty:
            st.dataframe(aptamer_data, use_container_width=True)
        else:
            st.warning("No aptamer data available.")

        aptamer_id = st.selectbox("Select Aptamer ID to view details", aptamer_data["id"].tolist()  if not aptamer_data.empty else [])
        if aptamer_id:
            aptamer_details = fetch_data(conn, "SELECT * FROM aptamers WHERE id = ?", (aptamer_id,))
            if not aptamer_details.empty:
                st.subheader(f"Aptamer Details (ID: {aptamer_id})")
                st.write(aptamer_details.to_dict())
            else:
                st.error("Aptamer not found")

        # Search functionality
        st.subheader("Search Aptamers")
        search_query = st.text_input("Enter search term")
        search_field = st.selectbox("Search by", ["aptamer_id", "sequence", "target"])
        if st.button("Search"):
            search_results = fetch_data(
                conn,
                f"SELECT * FROM aptamers WHERE {search_field} LIKE ?",
                ('%' + search_query + '%',),
            )
            if not search_results.empty:
                st.dataframe(search_results, use_container_width=True)
            else:
                st.info("No matching aptamers found.")

    # --- Interaction Data Page ---
    elif selected_page == "Interaction Data":
        st.header("Interaction Data")
        interaction_data = fetch_data(conn, "SELECT * FROM interactions")
        if not interaction_data.empty:
            st.dataframe(interaction_data, use_container_width=True)
        else:
            st.warning("No interaction data available.")

        # Filter interactions by Aptamer or EGFR ID
        st.subheader("Filter Interactions")
        filter_type = st.selectbox("Filter by", ["Aptamer ID", "EGFR ID", "All"])
        if filter_type == "Aptamer ID":
            aptamer_id = st.selectbox("Select Aptamer ID", aptamer_data["id"].tolist() if not aptamer_data.empty else [])
            if aptamer_id:
                interactions = fetch_data(
                    conn,
                    "SELECT * FROM interactions WHERE aptamer_id = ?", (aptamer_id,)
                )
                if not interactions.empty:
                    st.dataframe(interactions, use_container_width=True)
                else:
                    st.info("No interactions found for this aptamer.")
        elif filter_type == "EGFR ID":
            egfr_id = st.selectbox("Select EGFR ID", egfr_data["id"].tolist()  if not egfr_data.empty else [])
            if egfr_id:
                interactions = fetch_data(
                    conn,
                    "SELECT * FROM interactions WHERE egfr_id = ?", (egfr_id,)
                )
                if not interactions.empty:
                    st.dataframe(interactions, use_container_width=True)
                else:
                    st.info("No interactions found for this EGFR.")
        elif filter_type == "All":
             interaction_data = fetch_data(conn, "SELECT * FROM interactions")
             if not interaction_data.empty:
                st.dataframe(interaction_data, use_container_width=True)
             else:
                st.info("No interactions found .")

    # --- 3D Viewer Page ---
    elif selected_page == "3D Viewer":
        st.header("3D Structure Viewer")
        # Selectbox for choosing which structure to display.
        structure_type = st.selectbox(
            "Select structure to display",
            ["EGFR", "Aptamer-IV", "Aptamer-VI", "Aptamer-VII", "Uploaded PDB"],
        )
        # File paths (replace with your actual paths)
        pdb_file_paths = {
            "EGFR": "egfr.pdb",  # Placeholder
            "Aptamer-IV": "aptamer_iv.pdb",  # Placeholder
            "Aptamer-VI": "aptamer_vi.pdb",  # Placeholder
            "Aptamer-VII": "aptamer_vii.pdb",  # Placeholder
        }

        # Display the 3D viewer with the selected file.
        if structure_type in pdb_file_paths:
            st_3d_viewer(pdb_file_paths[structure_type])
        elif structure_type == "Uploaded PDB":
            if 'pdb_content' in st.session_state:
                st_3d_viewer(st.session_state.pdb_content)
            else:
                st.warning("Please upload a PDB file first.")
        else:
            st.error("Invalid structure type selected.")
    # Close the connection at the end of main()
    conn.close()

if __name__ == "__main__":
    main()
