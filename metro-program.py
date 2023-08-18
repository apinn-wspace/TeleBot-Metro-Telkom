import telebot
import mysql.connector
import sys
import os
import requests 
from telebot import types

API_KEY = "6682630708:AAGye4iCDngthehYanlBb5uwANwBDGnS8eA"
bot = telebot.TeleBot(API_KEY, parse_mode=None)

# Create a table to store STO and ME data
def create_table():
    try:
        conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = None,
            database = 'test'
        )
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metro_data (
                id INT AUTO_INCREMENT,
                sto_name VARCHAR(255),
                me_name VARCHAR(255),
                shareloc TEXT,
                photo_frame_before LONGBLOB,
                photo_frame_after LONGBLOB,
                photo_patchcore_before LONGBLOB,
                photo_patchcore_after LONGBLOB,
                photo_temperature_before LONGBLOB,
                photo_temperature_after LONGBLOB,
                filename_frame_before VARCHAR(255),
                filename_frame_after VARCHAR(255),
                filename_patchcore_before VARCHAR(255),
                filename_patchcore_after VARCHAR(255),
                filename_temperature_before VARCHAR(255),
                filename_temperature_after VARCHAR(255),
                PRIMARY KEY (id)
            )
        ''')

        conn.commit()
        print("Table 'metro_data' created successfully!")

    except mysql.connector.Error as err:
        print("Error:", err)

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Command /start
@bot.message_handler(commands=["start"])
def send_start_message(message):
    create_table()  # Call create_table function here to create the table before any other operations
    bot.send_message(message.chat.id, "Hello, I am ApinnBot!\nThanks for chatting with me!")

# Command /inputmetro
@bot.message_handler(commands=["inputmetro"])
def send_input_message(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    sto_menu = ["BDS", "BLP", "BTC", "BUM", "DBS", "KAI", "KIJ", "KMS", "LBJ", "MOR", "NGS",
                  "PNI", "RAI", "SGT", "SKN", "SLU", "SYA", "TBK", "TER", "TJT", "TPI", "TUB"]

    buttons = [types.KeyboardButton(item) for item in sto_menu]
    markup.add(*buttons)

    bot.send_message(message.chat.id, "User anda terdaftar di Witel RIKEP, silahkan pilih STO", reply_markup=markup)

# Handling STO selection
@bot.message_handler(func=lambda message: message.text in ["BDS", "BLP", "BTC", "BUM", "DBS", "KAI", "KIJ", "KMS",
                                                           "LBJ", "MOR", "NGS", "PNI", "RAI", "SGT", "SKN", "SLU",
                                                           "SYA", "TBK", "TER", "TJT", "TPI", "TUB"])
def send_me_message(message):
    sto = message.text    
    markup = types.ReplyKeyboardMarkup(row_width=1)
    me_menu = ["ME-D1-BDSA", "ME9-D1-BDSA", "ME-D1-BDS-RR"]
    buttons = [types.KeyboardButton(item) for item in me_menu]
    markup.add(*buttons)

    bot.send_message(message.chat.id, f"STO {sto} berhasil disimpan, silahkan pilih ME name yang akan diinputkan",
                     reply_markup=markup)

    # Save STO name to the database
    try:
        with mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = None,
            database = 'test'
        ) as conn:
            cursor = conn.cursor()

            # Insert STO name into the database
            cursor.execute('INSERT INTO metro_data (sto_name) VALUES (%s)', (sto,))
            conn.commit()

    except mysql.connector.Error as err:
        print("Error while saving STO name:", err)

# Handling ME selection
@bot.message_handler(func=lambda message: message.text in ["ME-D1-BDSA", "ME9-D1-BDSA", "ME-D1-BDS-RR"])
def handle_me_selection(message):
    me = message.text

    try:
        with mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = None,
            database = 'test'
        ) as conn:
            cursor = conn.cursor()

            # Update the ME name for the latest STO entry in the database
            cursor.execute('UPDATE metro_data SET me_name = %s WHERE id = (SELECT MAX(id) FROM metro_data)', (me,))
            conn.commit()

            bot.send_message(message.chat.id, "ME {} berhasil disimpan, Silahkan kirimkan lokasi Anda untuk melanjutkan."
                             .format(me))

    except mysql.connector.Error as err:
        print("Error while updating ME:", err)

# Handling user location
@bot.message_handler(content_types=["location"])
def handle_shareloc(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    shareloc = f"Latitude: {latitude}, Longitude: {longitude}"

    try:
        with mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = None,
            database = 'test'
        ) as conn:
            cursor = conn.cursor()

            # Update location for the latest STO entry in the database
            cursor.execute('UPDATE metro_data SET shareloc = %s WHERE id = (SELECT MAX(id) FROM metro_data)', (shareloc,))
            conn.commit()

            bot.send_message(message.chat.id, "Lokasi Anda berhasil disimpan. Kirim Photo Frame.")

    except mysql.connector.Error as err:
        print("Error while updating location:", err)

# Handling user upload
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    try:
        with mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = None,
            database = 'test'
        ) as conn:
            cursor = conn.cursor()

            # Get the last two file IDs from the photo array, if available
            if len(message.photo) >= 4:
                file_id1 = message.photo[-1].file_id
            if len(message.photo) >= 3:
                file_id2 = message.photo[-1].file_id
            if len(message.photo) >= 2:
                file_id3 = message.photo[-1].file_id
            if len(message.photo) >= 1:
                file_id4 = message.photo[-1].file_id 
            if len(message.photo) >= 0:
                file_id5 = message.photo[-1].file_id
            if len(message.photo) >= -1:
                file_id6 = message.photo[-1].file_id

            # Check if there are any entries in the database
            cursor.execute('SELECT COUNT(*) FROM metro_data')
            num_entries = cursor.fetchone()[0]

            if num_entries == 0:
                # No entries in the database, create a new entry
                cursor.execute('INSERT INTO metro_data (photo_frame_before) VALUES (%s)', (file_id1,))
                conn.commit()
                bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nSilakan Masukkan Foto Frame Metro Sesudah")
            else:
                # Retrieve the last entry
                cursor.execute('SELECT * FROM metro_data WHERE id = (SELECT MAX(id) FROM metro_data)')
                last_entry = cursor.fetchone()

                if not last_entry[4]:  # If photo_frame_before is not set
                    # Update the last entry with photo_frame_before
                    cursor.execute('UPDATE metro_data SET photo_frame_before = %s WHERE id = (SELECT MAX(id) FROM metro_data)',
                                   (file_id1,))
                    conn.commit()

                    # Save the photo_frame_before to computer storage
                    print("File ID 1:", file_id1)
                    file_info1 = bot.get_file(file_id1)
                    file_path1 = file_info1.file_path
                    download_path1 = f"./frame_before/frame_before_{last_entry[0]}.jpg"
                    downloaded_file1 = bot.download_file(file_path1)
                    with open(download_path1, "wb") as new_file1:
                        new_file1.write(downloaded_file1)

                    # Update filename_frame_before
                    filename_frame_before = os.path.basename(download_path1)
                    cursor.execute('UPDATE metro_data SET filename_frame_before = %s WHERE id = %s', (filename_frame_before, last_entry[0]))
                    conn.commit()

                    bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nSilakan Masukkan Foto Frame Metro Sesudah")

                elif not last_entry[5]:  # If photo_frame_after is not set
                    # Update the last entry with photo_frame_after
                    cursor.execute(
                        'UPDATE metro_data SET photo_frame_after = %s WHERE id = (SELECT MAX(id) FROM metro_data)',
                        (file_id2,))
                    conn.commit()

                    # Save the photo_frame_after to computer storage
                    print("File ID 2:", file_id2)
                    file_info2 = bot.get_file(file_id2)
                    file_path2 = file_info2.file_path
                    download_path2 = f"./frame_after/frame_after_{last_entry[0]}.jpg"
                    downloaded_file2 = bot.download_file(file_path2)
                    with open(download_path2, "wb") as new_file2:
                        new_file2.write(downloaded_file2)

                    # Update filename_frame_after
                    filename_frame_after = os.path.basename(download_path2)
                    cursor.execute('UPDATE metro_data SET filename_frame_after = %s WHERE id = %s', 
                        (filename_frame_after, last_entry[0]))
                    conn.commit()

                    bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nSilakan Masukkan Foto Patchcore Metro Sebelum")

                elif not last_entry[6]:  # If photo_patchcore_before is not set
                    # Update the last entry with photo_patchcore_before
                    cursor.execute('UPDATE metro_data SET photo_patchcore_before = %s WHERE id = (SELECT MAX(id) FROM metro_data)',
                        (file_id3,))
                    conn.commit()

                    # Save the photo_patchcore_before to computer storage
                    print("File ID 3:", file_id3)
                    file_info3 = bot.get_file(file_id3)
                    file_path3 = file_info3.file_path
                    download_path3 = f"./patchcore_before/patchcore_before_{last_entry[0]}.jpg"
                    downloaded_file3 = bot.download_file(file_path3)
                    with open(download_path3, "wb") as new_file3:
                        new_file3.write(downloaded_file3)

                    # Update filename_patchcore_before
                    filename_patchcore_before = os.path.basename(download_path3)
                    cursor.execute('UPDATE metro_data SET filename_patchcore_before = %s WHERE id = %s', 
                        (filename_patchcore_before, last_entry[0]))
                    conn.commit()

                    bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nSilakan Masukkan Foto Patchcore Metro Sesudah")

                elif not last_entry[7]:  # If photo_patchcore_after is not set
                    # Update the last entry with photo_patchcore_after
                    cursor.execute(
                        'UPDATE metro_data SET photo_patchcore_after = %s WHERE id = (SELECT MAX(id) FROM metro_data)',
                        (file_id4,))
                    conn.commit()

                    # Save the photo_patchcore_after to computer storage
                    print("File ID 4:", file_id4)
                    file_info4 = bot.get_file(file_id4)
                    file_path4 = file_info4.file_path
                    download_path4 = f"./patchcore_after/patchcore_after_{last_entry[0]}.jpg"
                    downloaded_file4 = bot.download_file(file_path4)
                    with open(download_path4, "wb") as new_file4:
                        new_file4.write(downloaded_file4)

                    # Update filename_patchcore_after
                    filename_patchcore_after = os.path.basename(download_path4)
                    cursor.execute('UPDATE metro_data SET filename_patchcore_after = %s WHERE id = %s', 
                        (filename_patchcore_after, last_entry[0]))
                    conn.commit()

                    bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nSilakan Masukkan Foto Suhu Metro Sebelum")

                elif not last_entry[8]:  # If photo_temperature_before is not set
                    # Update the last entry with photo_temperature_before
                    cursor.execute('UPDATE metro_data SET photo_temperature_before = %s WHERE id = (SELECT MAX(id) FROM metro_data)',
                        (file_id5,))
                    conn.commit()

                    # Save the photo_temperature_before to computer storage
                    print("File ID 5:", file_id5)
                    file_info5 = bot.get_file(file_id5)
                    file_path5 = file_info5.file_path
                    file_info5 = bot.get_file(file_id5)
                    file_path5 = file_info5.file_path
                    download_path5 = f"./temperature_before/temperature_before_{last_entry[0]}.jpg"
                    downloaded_file5 = bot.download_file(file_path5)
                    with open(download_path5, "wb") as new_file5:
                        new_file5.write(downloaded_file5)

                    # Update filename_temperature_before
                    filename_temperature_before = os.path.basename(download_path5)
                    cursor.execute('UPDATE metro_data SET filename_temperature_before = %s WHERE id = %s', 
                        (filename_temperature_before, last_entry[0]))
                    conn.commit()

                    bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nSilakan Masukkan Foto Temperature Metro Sesudah")

                else:  # If photo_temperature_after is not set
                    # Update the last entry with photo_temperature_after
                    cursor.execute(
                        'UPDATE metro_data SET photo_temperature_after = %s WHERE id = (SELECT MAX(id) FROM metro_data)',
                        (file_id6,))
                    conn.commit()

                    # Save the photo_temperature_after to computer storage
                    print("File ID 6:", file_id6)
                    file_info6 = bot.get_file(file_id6)
                    file_path6 = file_info6.file_path
                    download_path6 = f"./temperature_after/temperature_after_{last_entry[0]}.jpg"
                    downloaded_file6 = bot.download_file(file_path6)
                    with open(download_path6, "wb") as new_file6:
                        new_file6.write(downloaded_file6)

                    # Update filename_temperature_after
                    filename_temperature_after = os.path.basename(download_path6)
                    cursor.execute('UPDATE metro_data SET filename_temperature_after = %s WHERE id = %s', 
                        (filename_temperature_after, last_entry[0]))
                    conn.commit()

                    bot.send_message(message.chat.id, "Foto Berhasil Disimpan \nTerima kasih Data Metro Sudah Tersimpan")

    except Exception as e:
        print("Error while saving photo:", str(e))
        bot.send_message(message.chat.id, "Terjadi kesalahan saat menyimpan foto. Mohon coba lagi.")

# Start the bot
bot.polling()