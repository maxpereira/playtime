import sqlite3
import os
import sys
import shutil

# Helper function to output the header lines
def print_header():
    print("Playtime v1.0 - OnionUI Activity Tracker Utilities")
    print("Report Issues: https://github.com/maxpereira/playtime\n")

# Helper function to clear the screen output
def clear_screen():
    os_name = os.name
    if os_name == 'posix':  # Linux and macOS
        os.system('clear')
    elif os_name == 'nt':  # Windows
        os.system('cls')
    else:
        print("Screen clearing not supported for this operating system.")

# Ask for the SD card drive letter, back up the database, and try to connect to it
clear_screen()
print_header()
sdcard = input("Enter SD card drive letter: ")
dbfile = sdcard+":\Saves\CurrentProfile\play_activity\play_activity_db.sqlite"
if os.path.isfile(dbfile):
    clear_screen()
    print_header()
    print("The play activity database is found!")
    try:
        shutil.copy(dbfile, sdcard+":\Saves\CurrentProfile\play_activity\play_activity_db.sqlite.bak")
    except:
        print("An exception occurred creating a backup. There may be permissions issues with the SD card.")
        input("Press Enter to exit...")
        sys.exit()
    
    try:
        conn=sqlite3.connect(dbfile)
    except:
        print("An exception occurred connecting to the database. There may be permissions issues with the SD card.")
        input("Press Enter to exit...")
        sys.exit()
    
    print("A backup was created: "+sdcard+":\Saves\CurrentProfile\play_activity\play_activity_db.sqlite.bak\n")
    input("Press Enter to continue...")
    c=conn.cursor()
else:
    print("The play activity database was not found! Exiting...")
    sys.exit()

# View all play activity entries
def view_entries():
    clear_screen()
    print_header()
    c.execute("SELECT * FROM play_activity")
    
    del_rows = c.fetchall()
    result_dict = {}

    # Sum the play activity entries and count occurrences based on the rom_id
    for item in del_rows:
        key = item[0]
        value = item[1]
        result_dict[key] = result_dict.get(key, {"sum": 0, "count": 0})
        result_dict[key]["sum"] += value
        result_dict[key]["count"] += 1

    print("Listing all play activity entries:\n")

    # Display the play activity entries
    for key, values in result_dict.items():
        c.execute("SELECT name FROM rom WHERE id = ?", (key,))
        selected_names = c.fetchall()
        selected_names_first_entry = ', '.join(name[0] for name in selected_names)
        print(f"{selected_names_first_entry}: {values['sum']} seconds, {values['count']} plays")
    
    input("\nPress Enter to return to menu...")    

# Handle deletion of rows based on mode chosen
def del_entries():
    clear_screen()
    print_header()
    del_choice = 0
    
    if del_mode == 1:
        del_choice = input("Enter second count for deletion threshold: ")
        c.execute("SELECT * FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING SUM(play_time) < "+str(del_choice)+")")
    elif del_mode == 2:
        del_choice = input("Enter play count for deletion threshold: ")
        c.execute("SELECT * FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING COUNT(*) <= "+str(del_choice)+")")
    elif del_mode == 3:
        c.execute('SELECT name FROM rom')

        names = c.fetchall()
        count = 1
        for name in names:
            print(str(count) + ": "+name[0])
            count = count+1
    
        del_choice = input("\nEnter the ID of the game to delete: ")
        c.execute("SELECT * FROM play_activity WHERE rom_id = "+del_choice)

    del_rows = c.fetchall()
    result_dict = {}

    # Sum the play activity entries and count occurrences based on the rom_id
    for item in del_rows:
        key = item[0]
        value = item[1]
        result_dict[key] = result_dict.get(key, {"sum": 0, "count": 0})
        result_dict[key]["sum"] += value
        result_dict[key]["count"] += 1

    clear_screen()
    print_header()
    print("The following entries will be deleted:\n")

    # Display the play activities entries to be deleted
    for key, values in result_dict.items():
        c.execute("SELECT name FROM rom WHERE id = ?", (key,))
        selected_names = c.fetchall()
        selected_names_first_entry = ', '.join(name[0] for name in selected_names)
        print(f"{selected_names_first_entry}: {values['sum']} seconds, {values['count']} plays")

    # Ask for confirmation then delete the play activity entries
    answer = input("\nContinue? (y/n): ")
    if answer.lower() in ["y","yes"]:
        if del_mode == 1:
            c.execute("DELETE FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING SUM(play_time) < "+str(del_choice)+")")
        elif del_mode == 2:
            c.execute("DELETE FROM play_activity WHERE rom_id IN ( SELECT rom_id FROM play_activity GROUP BY rom_id HAVING COUNT(*) <= "+str(del_choice)+")")
        elif del_mode == 3:
            c.execute("DELETE FROM play_activity WHERE rom_id = "+del_choice)
        conn.commit()
        
        clear_screen()
        print_header()
        print("The play entries were deleted!")
        input("Press Enter to return to menu...")
    elif answer.lower() in ["n","no"]:
        print("Returning to menu")
    else:
        print("Invalid entry - returning to menu")

# Show the main menu
while True:
    clear_screen()
    print_header()
    print("1. View all play activity entries")
    print("2. Delete activity entries under X seconds of playtime")
    print("3. Delete activity entries under X plays")
    print("4. Delete all entries for a particular game")
    print("5. Exit")

    menu_choice = input("\nChoose an option: ")
    
    if menu_choice == '1':
        view_entries()
    elif menu_choice == '2':
        del_mode = 1
        del_entries()
    elif menu_choice == '3':
        del_mode = 2
        del_entries()
    elif menu_choice == '4':
        del_mode = 3
        del_entries()        
    elif menu_choice == '5':
        conn.close()
        print("Closing database connection and exiting...")
        break
    else:
        print("Invalid choice.")        