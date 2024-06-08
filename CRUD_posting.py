# -*- coding: utf-8 -*-
"""
Created on Sat Jun  8 15:17:50 2024

@author: sayan
"""

import sqlite3
import os
from PIL import Image
import io

def create_connection(db_file):
    
    """
    Create a database connection to the SQLite database specified by db_file.

    Parameters:
    db_file (str): The path to the SQLite database file.

    Returns:
    sqlite3.Connection: A connection object to the SQLite database. 
                        If an error occurs, it returns None and prints the error message.

    Raises:
    sqlite3.Error: If there is an issue connecting to the SQLite database, 
                   the error will be caught and printed.
    """
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("SQLite version:", sqlite3.version)
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn, user_id):
    """
    Create a table for storing posts associated with the given user ID.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    user_id (str): The identifier for the user, used to create a unique table for their posts.

    Returns:
    None

    Raises:
    sqlite3.Error: If there is an issue executing the SQL query to create the table, the error will be caught and printed.
    """
    try:
        sql_create_posts_table = """
        CREATE TABLE IF NOT EXISTS {}_posts (post_id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_caption TEXT,
            image BLOB,
            comments INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0
        );""".format(user_id)
        cursor = conn.cursor()
        cursor.execute(sql_create_posts_table)
        print("Table created successfully.")
    except sqlite3.Error as e:
        print(e)



def insert_post(conn, user_id, text_caption, image_path):
    """
    Create a table for storing posts.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    user_id (str): The identifier for the user, used to create a unique table name.

    Returns:
    None

    Raises:
    sqlite3.Error: If there is an issue creating the table, the error will be caught and printed.
    """
    try:
        file=open(image_path, 'rb')
        image_data = file.read()
        sql_insert_post = """INSERT INTO {}_posts (post_caption, image) VALUES (?, ?);""".format(user_id)
        cursor = conn.cursor()
        cursor.execute(sql_insert_post, (text_caption, image_data))
        conn.commit()
        print("Post inserted successfully")
        file.close()
    except sqlite3.Error as e:
        print(r"error:",e)




def read_post(conn, user_id, post_id=None):
    """
    Retrieve a post from the posts table.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    user_id (str): The identifier for the user, used to identify the user's table.
    post_id (int, optional): The identifier for the post. If not provided, the user will be prompted to enter it.

    Returns:
    list: A list containing a dictionary with the post details if the post is found.
    None: If the post is not found or an error occurs.

    Raises:
    sqlite3.Error: If there is an issue retrieving the post, the error will be caught and printed.
    """
    try:
        if post_id is None:
            post_id=input(r"Enter your Post ID: ")
            post=post_id_check(conn, post_id, user_id)
            if len(post)==0:
                print("Post not found, try again.")
                crud(conn, user_id)
                return False
        sql_select_post = """SELECT * FROM {}_posts WHERE post_id = ?;""".format(user_id)
        cursor = conn.cursor()
        cursor.execute(sql_select_post, (post_id,))
        post = cursor.fetchone()
        post_=[]
        if post:
            post_id, text_caption, image_data, comments, likes = post
            post_.append({
                "post_id": post_id,
                "user_id": user_id,
                "text_caption": text_caption,
                "image_data": image_data,   # Return image data as binary, handle it as needed
                "comments": comments,
                "likes": likes
            })
            return post_
        else:
            return None
    except sqlite3.Error as e:
        print(e)



def read_all_post(conn, user_id):
    """
    Retrieve all posts from the user's posts table.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    user_id (str): The identifier for the user, used to identify the user's table.

    Returns:
    list: A list of dictionaries, each containing the details of a post. If an error occurs, returns an empty list.

    Raises:
    sqlite3.Error: If there is an issue retrieving the posts, the error will be caught and printed.
    """
    try:
        sql_select_post = """SELECT * FROM {}_posts;""".format(user_id)
        cursor = conn.cursor()
        cursor.execute(sql_select_post)
        posts = cursor.fetchall()
        all_posts = []
        for post in posts:
            post_id,  text_caption, image_data, comments, likes = post
            all_posts.append({
                "post_id": post_id,
                "user_id": user_id,
                "text_caption": text_caption,
                "image_data": image_data,          # Return image data is binary
                "comments": comments,
                "likes": likes
            })
        
        return all_posts
    except sqlite3.Error as e:
        print(e)
        return []

def update_post(conn, user_id, post_id, text_caption=None, image_path=None):
    """
    Update a post in the user's posts table.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    user_id (str): The identifier for the user, used to identify the user's table.
    post_id (int): The identifier for the post to be updated.
    text_caption (str, optional): The new text caption for the post. Default is None.
    image_path (str, optional): The file path to the new image for the post. Default is None.

    Returns:
    None

    Raises:
    sqlite3.Error: If there is an issue updating the post, the error will be caught and printed.
    """
    try:
        cursor = conn.cursor()
        # Retrieve existing post data
        existing_post = read_post(conn, user_id, post_id=post_id)
        if existing_post:
            # Prepare SQL query
            sql_update_post = "UPDATE {}_posts SET ".format(user_id)
            parameters = []
            if text_caption:
                sql_update_post += "post_caption = ?, "
                parameters.append(text_caption)
            if image_path:
                file=open(image_path, 'rb')
                image_data = file.read()
                sql_update_post += "image = ?, "
                parameters.append(image_data)
            # Remove the trailing comma and space
            sql_update_post = sql_update_post[:-2]
            sql_update_post += f" WHERE post_id = {post_id};"
            # Execute the update query
            cursor.execute(sql_update_post, parameters)
            conn.commit()
            print("Post updated successfully")
            file.close()
        else:
            print("Post not found")
    except sqlite3.Error as e:
        print(e)


def delete_post(conn, post_id, user_id):
    """
    Delete a post from the user's posts table.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    post_id (int): The identifier for the post to be deleted.
    user_id (str): The identifier for the user, used to identify the user's table.

    Returns:
    None

    Raises:
    sqlite3.Error: If there is an issue deleting the post, the error will be caught and printed.
    """
    try:
        cursor = conn.cursor()
        sql_delete_post = "DELETE FROM {}_posts WHERE post_id = ?;".format(user_id)
        cursor.execute(sql_delete_post, (post_id,))
        conn.commit()
        print("Post deleted successfully")
    except sqlite3.Error as e:
        print(e)

def display_posts(posts, user_id):
    """
    Display all posts in a readable format.

    Parameters:
    posts (list): A list of dictionaries, each containing the details of a post.
    user_id (str): The identifier for the user, used to identify the user's posts.

    Returns:
    None

    Raises:
    None
    """
    for post in posts:
        print("User ID: {}".format(user_id))
        print("Post ID: {}".format(post["post_id"]))
        print("Text Caption: {}".format(post["text_caption"]))
        #print("Image Data: {}".format(post["image_data"]))
        display_image(post["image_data"])
        print("No. of comments: {}".format(post["comments"]))
        print("No. of likes: {}".format(post["likes"]))
        print("-" * 20)



def accept_post_image():
    
    """
    Prompt the user to input the file path of an image and validate the input.

    The function performs the following validations:
    - The file must exist and be accessible.
    - The file must have a '.png' or '.jpg' extension.
    - The file size must not exceed 5 MB.

    If the file meets all the criteria, its file path is returned. If not, the user is prompted to try again.

    Returns:
    str: The valid file path of the image to be posted.

    Raises:
    None
    """
    print("Only images with '.png' or 'jpg' extension are supported")
    img_path = input("Please enter the file path of the image to be posted: ")      
    file_name = os.path.basename(img_path)
    
    file_name, file_extension = os.path.splitext(file_name)
    print("File extension",file_extension)

    
    #Checks if the file exists and can be accessed by the code or not.
    try:                                                                   
        img_size_mb = os.path.getsize(img_path) / (1024 * 1024)        
    except Exception as error:
        print("Error: {}\n Please try again".format(error))
        #recursive calling
        img_path=accept_post_image()
    #Checks if the file exists, then whether it is a pdf file or not.
    if (file_extension!=".jpg" and file_extension!=".png"):
        print("Only images with '.png' or 'jpg' extension are supported, please try again.")
        #recursive calling
        img_path=accept_post_image()
    #Whether pdf file is less than 5 Mb or not, this is a constraint.
    if img_size_mb > 5:
        print("Image file size exceeds the maximum limit of 5 MB.\n PLease try again.")
        #recursive calling
        img_path=accept_post_image()

    return img_path



def accept_post_caption():
    
    """
    Prompt the user to input a caption for their post and validate the input.

    The function allows the user to leave the caption empty or re-enter it if desired.
    
    Returns:
    str: The valid caption for the post.

    Raises:
    None
    """
    caption = input(r"Please enter the caption for your post:  ")
    if caption=="":
        opt=input(r"You have left caption for the post empty, continue posting with caption as it is? \n(Y/N): ")
        if opt=="Y":
            return caption
        elif opt=="N":
            caption=accept_post_caption()
        else:
            print("Invalid entry, try again.")
            caption=accept_post_caption()
    return caption

def check_user_id(conn):
    """
    Check if a user exists based on the provided user ID.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.

    Returns:
    str: The validated user ID if found in the database.

    Raises:
    sqlite3.Error: If there is an issue executing the query, the error will be caught and printed.
    """
    try:
        user_id=input(r"Enter User ID: ")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", ("{}_posts".format(user_id),))
        table = cursor.fetchone()
        if table is not None:
            print("User_exists")
            return user_id
        else:
            print("User not found")
            user_id=check_user_id(conn)
            return user_id
    except sqlite3.Error as e:
        print(e)
        return False



def post_id_check(conn, post_id, user_id):
    """
    Check if a post with the given post_id exists in the user's posts table.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    post_id (int): The identifier for the post to be checked.
    user_id (str): The identifier for the user, used to identify the user's table.

    Returns:
    list: A list of tuples representing the post(s) with the given post_id. 
          If no post is found, an empty list is returned.

    Raises:
    sqlite3.Error: If there is an issue executing the query, the error will be caught and printed.
    """
    try:
        cursor = conn.cursor()
        sql_check_post = "SELECT * FROM {}_posts WHERE post_id = ?;".format(user_id)
        cursor.execute(sql_check_post, (post_id,))
        post = cursor.fetchall()
        return post
    except sqlite3.Error as e:
        print(e)
        return False



def display_image(image_data):
    """
    Display an image from binary data.

    Parameters:
    image_data (bytes): The binary data of the image to be displayed.

    Returns:
    None

    Raises:
    Exception: If there is an issue displaying the image, the error will be caught and printed.
    """
    try:
        image = Image.open(io.BytesIO(image_data))
        image.show()
    except Exception as e:
        print(f"Error displaying image: {e}")


def crud(conn, user_id):

    """
    A menu-driven interface for users to perform CRUD operations on their posts.

    Parameters:
    conn (sqlite3.Connection): A connection object to the SQLite database.
    user_id (str): The identifier for the user, used to identify the user's posts.

    Returns:
    None
    
    Raises:
    None
    """

    opt=input("""\nPress 1 to see all your posts, along with their captions and post IDs.
                 \nPress 2 to view one specific post (the post ID is required).
                 \nPress 3 to create a new post.
                 \nPress 4 to edit/update an old post (the post ID is required)
                 \nPress 5 to delete an old post (the post ID is required).
                 \nPress 6 to exit.\n""")
    match opt:
        
        case "1":
            posts=read_all_post(conn, user_id)
            display_posts(posts,user_id)
            crud(conn, user_id)

        case "2":
            post=read_post(conn, user_id)
            display_posts(post,user_id)
            crud(conn, user_id)

        case "3":
            img_path=accept_post_image()
            caption=accept_post_caption()
            insert_post(conn, user_id, caption, img_path)
            crud(conn, user_id)

        case "4":
            print("To update existing post-")
            post_id=input(r"Enter your Post ID: ")
            post=post_id_check(conn, post_id, user_id)
            if len(post)==0:
                print("Post not found, try again.")
                crud(conn, user_id)
                return False
            else:
                print('Post found')
            img_path=accept_post_image()
            caption=accept_post_caption()
            update_post(conn, user_id, post_id, text_caption=caption, image_path=img_path)
            crud(conn, user_id)

        case "5":
            print("To delete exixting post-")
            post_id=input(r"Enter your Post ID: ")
            
            post=post_id_check(conn, post_id, user_id)
            if len(post)==0:
                print("Post not found, try again.")
                crud(conn, user_id)
                return False
            delete_post(conn, post_id, user_id)
            crud(conn, user_id)

        case "6":
            print("Exiting...")
            return
            
        case _:
            print("Invalid input, please try again.")
            crud(conn, user_id)      




if __name__ == '__main__':

    conn=create_connection("posts_data.db")
    user_id=check_user_id(conn)
    crud(conn, user_id)
