import streamlit as st
import pandas as pd
import sqlite3
import base64  # for encoding images

# ### Configuration ###
SQLITE_DB_PATH = "data.db"  # Using the same database file

### Initialize Database Connection ###
def get_sqlite_connection():
    """
    Returns a connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to the database: {e}")
        return None  # Important: Return None on error

### Helper Functions ###
def fetch_data(query, params=()):
    """
    Fetches data from the database using a parameterized query.
    Handles database connection within the function.
    """
    conn = get_sqlite_connection()
    if conn is None:
        return pd.DataFrame()  # Return empty DataFrame on connection error
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return empty DataFrame on query error
    finally:
        conn.close()

### 3D Visualization Component (Placeholder) ###
def st_3d_viewer(pdb_file_path):
    """
    Placeholder for the 3D molecular structure viewer.
    This will be replaced with a working 3D viewer.
    """
    # st.write("3D Structure Viewer (Placeholder)")
    # st.write(f"Displaying structure from: {pdb_file_path}")

    # Try to display a static image if possible
    try:
        # Assuming you have a way to generate a PNG from the PDB (e.g., using PyMOL or ChimeraX)
        # and store it in a location accessible to the Streamlit app.
        image_path = "placeholder.png"  # Replace with a real path if you have one
        st.image(image_path, caption="3D Structure (Placeholder)", use_column_width=True)
    except Exception:
        st.warning("3D structure visualization is not fully implemented.  A placeholder is shown.")
    st.write("3D structure visualization is not fully implemented.  A placeholder is shown.")
    st.write(f"PDB File: {pdb_file_path}") # show the pdb file path

### Main Streamlit App ###
def main():
    """
    Main function to run the Streamlit app.
    """
    st.title("GlioTarget Aptamer Explorer")
    st.markdown(
        """
        Explore EGFR-targeting aptamers and their interactions for potential glioblastoma therapies.
        """
    )

    # --- Sidebar ---
    st.sidebar.title("Navigation")
    selected_page = st.sidebar.radio(
        "Select a section", ["EGFR Data", "Aptamer Data", "Interaction Data", "3D Viewer"]
    )

    # --- EGFR Data Page ---
    if selected_page == "EGFR Data":
        st.header("EGFR Data")
        egfr_data = fetch_data("SELECT * FROM egfr")  # No parameters needed here
        if not egfr_data.empty: # Check if the dataframe is empty
            st.dataframe(egfr_data, use_container_width=True)
        else:
            st.warning("No EGFR data available.")

        egfr_id = st.selectbox("Select EGFR ID to view details", egfr_data["id"].tolist() if not egfr_data.empty else [])
        if egfr_id:
            egfr_details = fetch_data("SELECT * FROM egfr WHERE id = ?", (egfr_id,))
            if not egfr_details.empty:
                st.subheader(f"EGFR Details (ID: {egfr_id})")
                st.write(egfr_details.to_dict())
            else:
                st.error("EGFR not found.")

    # --- Aptamer Data Page ---
    elif selected_page == "Aptamer Data":
        st.header("Aptamer Data")
        aptamer_data = fetch_data("SELECT * FROM aptamers")
        if not aptamer_data.empty:
            st.dataframe(aptamer_data, use_container_width=True)
        else:
            st.warning("No aptamer data available.")

        aptamer_id = st.selectbox("Select Aptamer ID to view details", aptamer_data["id"].tolist()  if not aptamer_data.empty else [])
        if aptamer_id:
            aptamer_details = fetch_data("SELECT * FROM aptamers WHERE id = ?", (aptamer_id,))
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
        interaction_data = fetch_data("SELECT * FROM interactions")
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
                    "SELECT * FROM interactions WHERE egfr_id = ?", (egfr_id,)
                )
                if not interactions.empty:
                    st.dataframe(interactions, use_container_width=True)
                else:
                    st.info("No interactions found for this EGFR.")
        elif filter_type == "All":
             interaction_data = fetch_data("SELECT * FROM interactions")
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
            ["EGFR", "Aptamer-IV", "Aptamer-VI", "Aptamer-VII"],
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
        else:
            st.error("Invalid structure type selected.")

if __name__ == "__main__":
    main()
