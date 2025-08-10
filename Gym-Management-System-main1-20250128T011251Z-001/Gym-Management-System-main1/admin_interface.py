import streamlit as st
import psycopg2
import pandas as pd

# Function to retrieve all members from the database
def view_members(cursor):
    cursor.execute("SELECT * FROM Members")
    members = cursor.fetchall()
    return members

# Function to retrieve all available plans from the database
def view_plans(cursor):
    cursor.execute("SELECT * FROM Plans")
    plans = cursor.fetchall()
    return plans


# Function to mark attendance
def mark_attendance(cursor, conn, member_id, status):
    try:
        cursor.execute("INSERT INTO Attendance (member_id, status) VALUES (%s, %s)", (member_id, status))
        conn.commit()
        st.success(f"Attendance marked as {status} for Member ID: {member_id}")
    except psycopg2.Error as e:
        st.error(f"Error marking attendance: {e}")

# Function to get weekly attendance
def get_weekly_attendance(cursor):
    cursor.execute("""
        SELECT a.member_id, a.date, a.status
        FROM Attendance a
    """)
    attendance_records = cursor.fetchall()
    
    if not attendance_records:
        return pd.DataFrame()

    # Create a DataFrame for processing
    df = pd.DataFrame(attendance_records, columns=["Member ID", "Date", "Status"])
    df["Date"] = pd.to_datetime(df["Date"]).dt.date  # Keep only the date part
    
    # Pivot the table for weekly visualization
    attendance_pivot = df.pivot_table(
        index=["Member ID"],
        columns=["Date"],
        values="Status",
        aggfunc="first"  # Use 'first' to avoid lists in cells
    )
    attendance_pivot.fillna("Absent", inplace=True)  # Replace NaN with "Absent"
    return attendance_pivot

# Function to add a new item
def add_item(cursor, conn, item_name, item_quantity, item_price, item_description):
    try:
        cursor.execute("INSERT INTO Items (name, quantity, price, description) VALUES (%s, %s, %s, %s)",
                    (item_name, item_quantity, item_price, item_description))
        conn.commit()
        st.success(f"Item '{item_name}' added successfully!")
    except psycopg2.Error as e:
        st.error(f"Error adding item: {e}")

# Function to view all items
def view_items(cursor):
    cursor.execute("SELECT * FROM Items")
    items = cursor.fetchall()
    return items

# Function to add a new member to the database
def add_member(cursor, conn, first_name, last_name, email, phone, address, date_of_birth, plan_id):
    try:
        cursor.execute("INSERT INTO Members (first_name, last_name, email, phone, address, date_of_birth, date_joined, plan_id) VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, %s)",
                (first_name, last_name, email, phone, address, date_of_birth, plan_id))
        conn.commit()
        st.success("Member added successfully!")
    except psycopg2.Error as e:
        st.error(f"Error adding member: {e}")

# Function to update an existing member in the database
def update_member(cursor, conn, member_id, first_name, last_name, email, phone, address, date_of_birth, plan_id):
    try:
        cursor.execute("UPDATE Members SET first_name = %s, last_name = %s, email = %s, phone = %s, address = %s, date_of_birth = %s, plan_id = %s WHERE member_id = %s",
                (first_name, last_name, email, phone, address, date_of_birth, plan_id, member_id))
        conn.commit()
        st.success("Member updated successfully!")
    except psycopg2.Error as e:
        st.error(f"Error updating member: {e}")

# Attendance records will be deleted automatically due to the ON DELETE CASCADE rule.
def delete_member(cursor, conn, member_id):
    try:
        cursor.execute("DELETE FROM MemberCredentials WHERE member_id = %s", (member_id,))
        cursor.execute("DELETE FROM Members WHERE member_id = %s", (member_id,))
        conn.commit()
        st.success("Member and related attendance records deleted successfully!")
    except psycopg2.Error as e:
        st.error(f"Error deleting member: {e}")

def render_admin_interface(cursor, conn):
    st.sidebar.subheader("Admin Interface")

    # Options for admin
    options = ["Attendance", "View Members", "Add Member", "Update Member", "View Plans", "Delete Member", "Add Item", "View Item"]
    choice = st.sidebar.selectbox("Select Option", options)

    # View members
    if choice == "View Members":
        st.subheader("View Members")
        members = view_members(cursor)
        for member in members:
            st.write("Member ID:", member[0])
            st.write("First Name:", member[1])
            st.write("Last Name:", member[2])
            st.write("Email:", member[3])
            st.write("Phone:", member[4])
            st.write("Address:", member[5])
            st.write("Date of Birth:", member[6])
            st.write("Date Joined:", member[7])
            st.write("Plan ID:", member[8])
            st.write("-" * 30)

    

    # Add member
    elif choice == "Add Member":
        st.subheader("Add Member")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        address = st.text_input("Address")
        date_of_birth = st.date_input("Date of Birth")

        # Retrieve available plans
        plans = view_plans(cursor)
        plan_names = [plan[1] for plan in plans]
        selected_plan_name = st.selectbox("Select Plan", plan_names)

        # Get the ID of the selected plan
        selected_plan_id = next((plan[0] for plan in plans if plan[1] == selected_plan_name), None)

        if st.button("Add Member"):
            add_member(cursor, conn, first_name, last_name, email, phone, address, date_of_birth, selected_plan_id)

    # Update member
    elif choice == "Update Member":
        st.subheader("Update Member")
        member_id_update = st.number_input("Enter Member ID to Update", min_value=1, step=1)
        if member_id_update:
            member_to_update = next((member for member in view_members(cursor) if member[0] == member_id_update), None)
            if member_to_update:
                first_name = st.text_input("First Name", value=member_to_update[1])
                last_name = st.text_input("Last Name", value=member_to_update[2])
                email = st.text_input("Email", value=member_to_update[3])
                phone = st.text_input("Phone", value=member_to_update[4])
                address = st.text_input("Address", value=member_to_update[5])
                date_of_birth = st.date_input("Date of Birth", value=member_to_update[6] if member_to_update[6] else None)

                # Retrieve available plans
                plans = view_plans(cursor)
                plan_names = [plan[1] for plan in plans]
                selected_plan_index = next((i for i, plan in enumerate(plans) if plan[0] == member_to_update[8]), -1)

                selected_plan_name = st.selectbox("Select Plan", plan_names, index=selected_plan_index if selected_plan_index != -1 else 0)
                selected_plan_id = next((plan[0] for plan in plans if plan[1] == selected_plan_name), None)

                if st.button("Update Member"):
                    update_member(cursor, conn, member_id_update, first_name, last_name, email, phone, address, date_of_birth, selected_plan_id)
            else:
                st.error("Member not found.")

    elif choice == "Attendance":
        st.subheader("Attendance")
        sub_choice = st.radio("Choose Action", ["Mark Attendance", "View Attendance"])

        if sub_choice == "Mark Attendance":
            members = view_members(cursor)  # Fetch all members
            member_names = [f"{member[1]} {member[2]} (ID: {member[0]})" for member in members]
            selected_member = st.selectbox("Select Member", member_names)
            
            # Extract member ID from selection
            member_id = int(selected_member.split("(ID: ")[1].strip(")"))
            status = st.radio("Attendance Status", ["Present", "Absent"])
            
            if st.button("Mark Attendance"):
                mark_attendance(cursor, conn, member_id, status)

        elif sub_choice == "View Attendance":
            attendance_data = get_weekly_attendance(cursor)
            
            if not attendance_data.empty:
                st.subheader("Weekly Attendance Sheet")
                st.dataframe(attendance_data)  # Display the pivoted DataFrame
            else:
                st.error("No attendance data found.")



    # View plans
    elif choice == "View Plans":
        st.subheader("View Plans")
        plans = view_plans(cursor)
        for plan in plans:
            st.write("Plan ID:", plan[0])
            st.write("Plan Name:", plan[1])
            st.write("Plan Cost:", plan[2])
            st.write("-" * 30)

    # Delete member
    elif choice == "Delete Member":
        st.subheader("Delete Member")
        member_id_delete = st.number_input("Enter Member ID to Delete", min_value=1, step=1)
        if st.button("Delete Member"):
            delete_member(cursor, conn, member_id_delete)

    # Add Items
    elif choice == "Add Item":
        st.subheader("Add New Item")
        item_name = st.text_input("Item Name")
        item_quantity = st.number_input("Quantity", min_value=1, step=1)
        item_price = st.number_input("Price", min_value=0.0, step=0.01, format="%.2f")
        item_description = st.text_area("Description")

        if st.button("Add Item"):
            add_item(cursor, conn, item_name, item_quantity, item_price, item_description)

    # View Items
    elif choice == "View Item":
        st.subheader("View Items")
        items = view_items(cursor)

        if items:
            for item in items:
                st.write("Item ID:", item[0])
                st.write("Name:", item[1])
                st.write("Quantity:", item[2])
                st.write(f"Price: ${item[3]:.2f}")
                st.write("Description:", item[4])
                st.write("-" * 30)
        else:
            st.info("No items available.")

