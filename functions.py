import pymongo
#from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
#import smtplib
#import ssl
import random
import requests
import json
from flask import session
import os
import dns
import string
#from email.mime.text import MIMEText
#from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from dotenv import load_dotenv
import certifi
import resend

# Load environment variables from .env file
load_dotenv()

resend.api_key = os.environ.get('RESEND_API_KEY')

# Initialize MongoDB client
# Initialize MongoDB client (lazy connection)
bookDB = None

def get_db():
    global bookDB
    if bookDB is None:
        bookDB = pymongo.MongoClient(
            os.environ.get('MONGODB_URI'),
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,
        )
    return bookDB

usersDB = None
profilesCollection = None
notificationsCollection = None
settingsCollection = None
followRequestsCollection = None
reportsCollection = None
forgotPasswordCollection = None
deleteAccountsCollection = None
postsDB = None
postsCollection = None
commentsCollection = None

def init_collections():
    global usersDB, profilesCollection, notificationsCollection, settingsCollection
    global followRequestsCollection, reportsCollection, forgotPasswordCollection
    global deleteAccountsCollection, postsDB, postsCollection, commentsCollection
    
    db = get_db()
    usersDB = db.Users
    profilesCollection = usersDB.Profiles
    notificationsCollection = usersDB.Notifications
    settingsCollection = usersDB.Settings
    followRequestsCollection = usersDB.FollowRequests
    reportsCollection = usersDB.Reports
    forgotPasswordCollection = usersDB.ForgotPassword
    deleteAccountsCollection = usersDB.DeleteAccount
    postsDB = db.Posts
    postsCollection = postsDB.Posts
    commentsCollection = postsDB.Comments

#mods hehehe thats me
mods = ["polto"]
#OG Users
ogs = ["locooldog", "dario"]

# Function to add a cookie to the session
def addCookie(key, value):
    session[key] = value

# Function to remove a cookie from the session
def removeCookie(key):
    session.clear()

# Function to get a cookie from the session
def getCookie(key):
    try:
        if session.get(key, False) != False:
            return session.get(key)
        else:
            return False
    except:
        return False
    
# Function to generate a random number with a specified number of digits
#use this for the create account function
def random_with_whatever_digits(whatever):
    range_start = 10**(whatever-1)
    range_end = (10**whatever)-1
    return random.randint(range_start, range_end)

# Function to check if a user ID exists in the database
def getUserID(id):
    myQuery = {"Username": id}
    myDoc = profilesCollection.find(myQuery)
    for i in myDoc:
        return True
    return False

def getHashedPassword(username):
    myQuery = {"Username": username}
    myDoc = profilesCollection.find(myQuery)
    for i in myDoc:
        return i['Password']
    return False
    
def createAccount(username, email, password):
    passwordHash = generate_password_hash(password)
    # Generate a unique user ID with 10 digits for now
    id = random_with_whatever_digits(10)
    while getUserID(int(id)) == True:
        id = random_with_whatever_digits(10)
    # document that stores user information
    document = [{
        "_id": int(id),
        "Username": username,
        "Password": passwordHash,
        "Created": str(datetime.datetime.now()),
        "Email": email,
        "Verified": False,
        "Blocked": [],
        "Followers": [],
        "Following": [],
        "Description": None,
    }]
    # TODO: MAKE THE SEND MAIL FUNCTION
    mailManIsHere = send_mail(email, username, id) # this will send the mail
    if mailManIsHere == True:
        # insert the document into the collection
        profilesCollection.insert_many(document)
    else:
        return mailManIsHere

# Function to retrieve user details by username
def getUser(username):
    # get user details
    myQuery = {"Username": username}
    myDoc = profilesCollection.find(myQuery)
    # check if user is deleted
    for i in myDoc:
        if(i.get("Deleted", None) == None):
            return i
        return False
    return False

# Function to check if a username already exists in the database
def checkUsernameExists(username):
    myQuery = {"Username": username}
    myDoc = profilesCollection.find(myQuery)
    for i in myDoc:
        return True
    return False

# Function to check if an email already exists in the database
def checkEmailExists(email):
    myQuery = {"Email": email}
    myDoc = profilesCollection.find(myQuery)
    for i in myDoc:
        return True
    return False

# Function to verify a user's email using a verification link
def verify(username, id):
    user = getUser(username)
    if user == False:
        return False
    # this can be used to `verify` users when they click the link in their email
    userID = str(user["_id"])
    if str(userID) == str(id):
        user2 = user
        del user2["Verified"]
        user2["Verified"] = True
        delete = {"Username": username}
        profilesCollection.delete_one(delete)
        profilesCollection.insert_one(user2)
        return True
    else:
        return False
    
##TODO NEXT: SEND MAIL FUNCTION also, set up email configuration in .env file along with the Gmail Account: name decided to be "GoodSoil"
# For email, start out with google and then branch off into maybe titain mail with domain.
# Free domain is from the github students pack at name.com (Hopefully) 
# Add the domain function here. Depednding on the domain, the email sending function will change.

def send_mail(receiver_mail, username, id):
    funHTMLCode = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;}}
        .container {{max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);}}
        .header {{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 12px 12px 0 0;}}
        .header h1 {{font-size: 28px; margin-bottom: 5px;}}
        .header p {{font-size: 14px; opacity: 0.9;}}
        .content {{padding: 40px 30px;}}
        .content p {{font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 20px;}}
        .button {{display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;}}
        .button:hover {{opacity: 0.9;}}
        .footer {{background: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #eee; border-radius: 0 0 12px 12px;}}
        .footer p {{font-size: 12px; color: #999;}}
        .highlight {{color: #667eea; font-weight: 600;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 GoodSoil</h1>
            <p>Welcome to our community</p>
        </div>
        <div class="content">
            <p>Hi <span class="highlight">{username}</span>,</p>
            <p>Thank you for creating an account on GoodSoil! Please verify your email address to activate your account and get started.</p>
            <a href='https://www.goodsoil.online/verify/{username}/{str(id)}' class="button">Verify Email Address</a>
            <p style="font-size: 14px; color: #666;">If you didn't create this account, please ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 GoodSoil. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""
    try:
        params = {
            "from": "GoodSoil <noreply@korbindev.tech>",
            "to": [receiver_mail],
            "subject": "GoodSoil Email Verification",
            "html": funHTMLCode,
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return f"Request to send email failed. Please try again later. Error: {e}"

# Function to add or update a user's description
def add_Description(username, description):
    try:
        user = getUser(username)
        if user == False:
            return "User not found."
        result = profilesCollection.update_one(
            {"Username": username},
            {"$set": {"Description": description}},
            upsert=False
        )
        if result.matched_count == 0:
            return "Profile document not found."
        return True
    except Exception as e:
        return f"Failed to update description: {e}"
    
# follow function
def follow(follower, following):
    follower = follower.lower()
    following = following.lower()
    if follower in getUser(following)["Followers"]:
        return f"You have already followed {following}."
    if getUser(following) == False:
        return f"The user {following} does not have an account."
    if follower == following:
        return "You cannot follow yourself."
    if getSettings(following)["Public"] == False:
        # Use truthiness, not == True, and proper query
        if checkFollowRequest(follower, following):
            return f"You have already sent a follow request to {following}."
        followRequest(follower, following)
        return True
    
    followrUser = getUser(follower) # the one who follows
    followingDoc = followrUser["Following"]
    followingDoc.append(following)
    del followrUser["Following"]
    followrUser["Following"] = followingDoc
    delete = {"Username" : follower}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([followrUser])
    followingUser = getUser(following) # the one being followed
    followersDoc = followingUser["Followers"]
    followersDoc.append(follower)
    del followingUser["Followers"]
    followingUser["Followers"] = followersDoc
    delete = {"Username" : following}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([followingUser])
    return True

def unFollow(username, unfollow):
    if username not in getUser(unfollow)["Followers"]:
        return f"You are not following {unfollow}."
    if getUser(unfollow) == False:
        return f"The user {unfollow} does not exist."
    user = getUser(username)
    doc = user["Following"]
    doc.remove(unfollow)
    del user["Following"]
    user["Following"] = doc
    delete = {"Username": username}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([user])
    other = getUser(unfollow)
    otherDoc = other["Followers"]
    otherDoc.remove(username)
    del other["Followers"]
    other["Followers"] = otherDoc
    otherDelete = {"Username": unfollow}
    profilesCollection.delete_one(otherDelete)
    profilesCollection.insert_many([other])
    return True

# NOTIFICATIONS FUNCTIONSSSSS #
def getNotifications(username):
    myQuery = {"Username" : username}
    myDoc = notificationsCollection.find(myQuery)
    notifications = []
    for i in myDoc:
        notifications.append(i)
    return notifications

def getNotificationsNotShown(username):
    myQuery = {"Username": username}
    myDoc = notificationsCollection.find(myQuery)
    notifications = []
    for i in myDoc:
        if i["Seen"] == False:
            notifications.append(i)
    return notifications

def addNotification(username, notification):
    notificationDoc = {"Username": username, "Notification": notification, "Seen": False}
    notificationsCollection.insert_many([notificationDoc])
    if getSettings(username)["Email"] == True:
        funHTMLCode = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;}}
        .container {{max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);}}
        .header {{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; border-radius: 12px 12px 0 0;}}
        .header h1 {{font-size: 24px;}}
        .content {{padding: 40px 30px;}}
        .content p {{font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 20px;}}
        .notification {{background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; border-radius: 8px; margin: 20px 0;}}
        .notification p {{margin: 0; color: #555;}}
        .button {{display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;}}
        .footer {{background: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #eee; border-radius: 0 0 12px 12px;}}
        .footer p {{font-size: 12px; color: #999;}}
        .highlight {{color: #667eea; font-weight: 600;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔔 New Notification</h1>
        </div>
        <div class="content">
            <p>Hi <span class="highlight">{username}</span>,</p>
            <p>You have a new notification on GoodSoil:</p>
            <div class="notification">
                <p>{notification}</p>
            </div>
            <p style="font-size: 14px; color: #666;">To manage your notification preferences, visit your account settings.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 GoodSoil. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""
        try:
            receiver_email = getUser(username)["Email"]
            params = {
                "from": "GoodSoil <GoodSoil <noreply@korbindev.tech>>",
                "to": [receiver_email],
                "subject": "GoodSoil Notification",
                "html": funHTMLCode,
            }
            resend.Emails.send(params)
        except Exception as e:
            print(f"Email notification error: {e}")
    return True

    
def clearNotifications(username):
    notifications = getNotifications(username)
    for notif in notifications:
        delete = {"_id": notif["_id"]}
        notificationsCollection.delete_one(delete)
    return True

def allSeen(username):
    notifications = getNotifications(username)
    myQuery = {"Username": username}
    newValues = {"$set": {"Seen": True}}
    notificationsCollection.update_many(myQuery, newValues)
    return True
        
# Post functions #
def getPost(description):
    myQuery = {"Description": description}
    myDoc = postsCollection.find(myQuery)
    for i in myDoc:
        return i
    return False

def getPostByID(id):
    myQuery = {"_id": int(id)}
    myDoc = postsCollection.find(myQuery)
    for i in myDoc:
        return i
    return False

def makePost(username, title, description, postType):
    postID = random_with_whatever_digits(10)
    while getUserID(int(postID)) == True:
        postID = random_with_whatever_digits(10)
    wordSplit = description.split()
    mentions = []
    for word in wordSplit:
        if word.startswith("@") == True:
            mention = word.replace("@", "")
            if getUser(mention) != False:
                mentions.append(mention)
    for mention in mentions:
        addNotification(mention, f"You were mentioned in a post by {username}. Check it out <a href='/post/{postID}'>here</a>!")
    if mentions != []:
        allMentions = ", ".join(mentions)
        addLog(f"{username} mentioned {allMentions} in a <a href='/post/{postID}'>post</a>.")
        addNotification(username, f"You mentioned {allMentions} in your <a href='/post/{postID}'>post</a>.")
    document = [{"_id": postID, "Author": username, "Title": title, "Description": description, "Likes": 0, "LikesPeople": [], "Views": [], "Type": postType, "Created": datetime.datetime.now(), "Pinned": False}]
    postsCollection.insert_many(document)

def viewPost(id, username):
    post = getPostByID(id)
    if username in post["Views"]:
        return True
    else:
        views = post["Views"]
        views.append(username)
        del post["Views"]
        post["Views"] = views
        delete = {"_id": int(id)}
        postsCollection.delete_one(delete)
        postsCollection.insert_many([post])
        return True

def deletePost(username, postID):
    post = getPostByID(int(postID))
    if post == False:
        return "That post does not exist."
    if post["Author"] == username:
        delete = {"_id": post["_id"]}
        postsCollection.delete_one(delete)
        return True
    elif username in mods:
        delete = {"_id": post["_id"]}
        postsCollection.delete_one(delete)
        addNotification(post["Author"], f"Your post titled '{post['Title']}' has been removed by a moderator.")
        return True
    else:
        return "You do not have permission to delete this post."
    
def getTop():
    number = 0
    posts = []
    pinned = []
    # Get all posts sorted by Pinned first (descending), then by Likes (descending)
    for post in postsCollection.find().sort([("Pinned", -1), ("Likes", -1)]):
        if post.get("Pinned", False):
            pinned.append(post)
        else:
            if number == 10:
                break
            posts.append(post)
            number += 1
    return pinned + posts

def getNew():
    number = 0
    posts = []
    pinned = []
    # Get all posts sorted by Pinned first (descending), then by Created (descending)
    for post in postsCollection.find().sort([("Pinned", -1), ("Created", -1)]):
        if post.get("Pinned", False):
            pinned.append(post)
        else:
            if number == 10:
                break
            posts.append(post)
            number += 1
    return pinned + posts

def getSettings(username):
    myQuery = {"Username": username}
    myDoc = settingsCollection.find(myQuery)
    for i in myDoc:
        return i
    return {"Username": username, "Email": False, "Public": True}

def getSettingsOfUser(username):
    myQuery = {"Username": username}
    myDoc = settingsCollection.find(myQuery)
    for i in myDoc:
        return i
    return False

def changePublicSettings(username):
    document = getSettings(username)
    # Toggle the Public setting
    document["Public"] = not document["Public"]
    # Update the document in the database
    settingsCollection.replace_one(
        {"Username": username},
        document,
        upsert=True
    )
    return True

def changeEmailSettings(username):
    document = getSettings(username)
    # Toggle the Email setting
    document["Email"] = not document["Email"]
    # Update the document in the database
    settingsCollection.replace_one(
        {"Username": username},
        document,
        upsert=True
    )
    return True

def followRequest(follower, following):
    document = {"Follower": follower, "following": following}
    followRequestsCollection.insert_many([document])

def checkFollowRequest(follower, following):
    # Ensure consistent casing
    follower = follower.lower()
    following = following.lower()
    myQuery = {"Follower": follower, "following": following}
    doc = followRequestsCollection.find_one(myQuery)
    return doc if doc else False

def acceptTheFolloweRequest(username, follower, following):
    follower = follower.lower()
    following = following.lower()
    if username != following:
        return "You do not have permission to accept this follow request."
    req = checkFollowRequest(follower, following)
    if req == False:
        return "No pending follow request found."
    userID = req["_id"]
    delete = {"_id": userID}
    followRequestsCollection.delete_one(delete)
    followerUser = getUser(follower) # the one who follows
    followingDoc = followerUser["Following"]
    followingDoc.append(following)
    del followerUser["Following"]
    followerUser["Following"] = followingDoc
    delete = {"Username" : follower}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([followerUser])
    followingUser = getUser(following) # the one being followed
    followersDoc = followingUser["Followers"]
    followersDoc.append(follower)
    del followingUser["Followers"]
    followingUser["Followers"] = followersDoc
    delete = {"Username" : following}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([followingUser])
    addNotification(follower, f"Your follow request to {following} has been accepted!")
    return True

def allFollowRequests(username):
    myQuery = {"following": username.lower()}
    myDoc = followRequestsCollection.find(myQuery)
    requests = []
    for i in myDoc:
        requests.append(i)
    return requests

def denyTheFollowRequest(username, follower, following):
    follower = follower.lower()
    following = following.lower()
    if username != following:
        return "You do not have permission to deny this follow request."
    req = checkFollowRequest(follower, following)
    if req == False:
        return "No pending follow request found."
    delete = {"_id": req["_id"]}
    followRequestsCollection.delete_one(delete)
    return True

def allUserPosts(username):
    myQuery = {"Author": username}
    myDoc = postsCollection.find(myQuery)
    posts = []
    for i in myDoc:
        posts.append(i)
    return posts

def editAPost(username, postID, description):
    post = getPostByID(int(postID))
    wordSplit = description.split()
    mentions = []
    for word in wordSplit:
        if word.startswith("@") == True:
            mention = word.replace("@", "")
            if getUser(mention) != False:
                mentions.append(mention)
    oldMentions = []
    wordSplitOld = post["Description"].split()
    for word in wordSplitOld:
        if word.startswith("@") == True:
            mention = word.replace("@","")
            if getUser(mention) != False:
                if mention not in mentions:
                    oldMentions.append(mention)
    for i in oldMentions:
        try:
            mentions.remove(i)
        except:
            pass
    for mention in mentions:
        addNotification(mention, f"{username} mentioned you in an edited post. Check it out <a href='/post/{postID}'>here</a>!")
    if mentions != []:
        allMentions = ", ".join(mentions)
        addLog(f"{username} mentioned {allMentions} in an edited <a href='/post/{postID}'>post</a>.")
        addNotification(username, f"You mentioned {allMentions} in your edited <a href='/post/{postID}'>post</a>.")
        if post == False:
            return "That post does not exist."
        if post["Author"] != username:
            pass
        elif username in mods:
            pass
        else:
            return "You do not have permission to edit this post."
        del post["Description"]
        post["Description"] = description
        delete = {"_id": post["_id"]}
        postsCollection.delete_one(delete)
        postsCollection.insert_many([post])
        return True
    
    ## MAYBE HAD HUMAN CHECK LATER ##
    ## TODO: add capatcha to create account and login functions ##

def likePost(postID, username):
    post = getPostByID(int(postID))
    if username in post["LikesPeople"]:
        return "You have already liked this post."
    likesPeople = post["LikesPeople"]
    likesPeople.append(username)
    del post["LikesPeople"]
    post["LikesPeople"] = likesPeople
    likes = post["Likes"]
    likes += 1
    del post["Likes"]
    post["Likes"] = likes
    delete = {"_id" : post["_id"]}
    postsCollection.delete_one(delete)
    postsCollection.insert_many([post])
    addNotification(post["Author"], f"Your post titled '{post['Title']}' has a new like!")
    return True
    
def unlikePost(postID, username):
    post = getPostByID(int(postID))
    if username not in post["LikesPeople"]:
        return "You have not liked this post."
    likesPeople = post["LikesPeople"]
    likesPeople.remove(username)
    del post["LikesPeople"]
    post["LikesPeople"] = likesPeople
    likes = post["Likes"]
    likes -= 1
    del post["Likes"]
    post["Likes"] = likes
    delete = {"_id":post["_id"]}
    postsCollection.delete_one(delete)
    postsCollection.insert_many([post])
    return True


def comment(username, postID, commentText):
    post = getPostByID(int(postID))
    if post == False:
        return "That post does not exist."
    if post["Type"] == "Public":
        pass
    else:
        if post["Author"] == username:
            pass
        else:
            if username in getUser(post["Author"])["Followers"]:
                pass
            else:
                return "You do not have permission to comment on this post."
    document = {"Post": int(postID), "Comment": commentText, "Author": username, "Created": str(datetime.datetime.now())}
    insert = commentsCollection.insert_one(document)
    commentID = insert.inserted_id
    if post["Author"] != username:
        addNotification(post["Author"], f"{username} commented on your post. Check it out <a href='/post/{postID}#comment-{commentID}'>here</a>!")
    wordSplit = commentText.split()
    mentions = []
    for word in wordSplit:
        if word.startswith("@") == True:
            mention = word.replace("@", "")
            if getUser(mention) != False:
                if mention not in mentions:
                    mentions.append(mention)
    for mention in mentions:
        addNotification(mention, f"You were mentioned in a comment by {username}. Check it out <a href='/post/{postID}#comment-{commentID}'>here</a>!")
    if mentions != []:
        allMentions = ", ".join(mentions)
        addLog(f"{username} mentioned {allMentions} in a <a href='/post/{postID}#comment-{commentID}'>comment</a>.")
        addNotification(username, f"You mentioned {allMentions} in your <a href='/post/{postID}#comment-{commentID}'>comment</a>.")
    return [f"/post/{str(postID)}#comment-{str(commentID)}"]

def getComments(postID):
    myQuery = {"Post": int(postID)}
    myDoc = commentsCollection.find(myQuery)
    comments = []
    for i in myDoc:
        comments.append(i)
    return comments

def getAllUserPublicPosts(username):
    myQuery = {"Author": username}
    myDoc = postsCollection.find(myQuery)
    posts=[]
    for i in myDoc:
        if i["Type"] == "Public":
            posts.append(i)
    return posts

def getAllUserPrivatePosts(username):
    myQuery = {"Author": username}
    myDoc = postsCollection.find(myQuery)
    posts = []
    for i in myDoc:
        if i["Type"] == "Private":
            posts.append(i)
    return posts

def getCommentByID(commentID):
    myQuery = {"_id": ObjectId(commentID)}
    myDoc = commentsCollection.find(myQuery)
    for i in myDoc:
        return i
    return False

def deleteComment(username, commentID):
    comment = getCommentByID(commentID)
    if comment == False:
        return "That comment does not exist."
    if comment["Author"] == username:
        pass
    elif username in mods:
        pass
    else:
        return "You do not have permission to delete this comment."
    delete = {"_id": ObjectId(commentID)}
    commentsCollection.delete_one(delete)
    return True

def changeEmail(username, email):
    user2 = getUser(username)
    user = user2
    del user["Email"]
    user["Email"] = email
    del user["Verified"]
    user["Verified"] = False
    delete = {"Username": username}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([user])
    userID = getUser(username)["_id"]
    mailManIsHere = send_mail(email, username, userID)
    return mailManIsHere

def editComment(username, commentID, newComment):
    comment = getCommentByID(commentID)
    if comment == False:
        return "That comment does not exist."
    if comment["Author"] == username:
        pass
    elif username in mods:
        pass
    else:
        return "You do not have permission to edit this comment."
    wordSplit = newComment.split()
    mentions = []
    for word in wordSplit:
        if word.startswith("@") == True:
            mention = word.replace("@","")
            if getUser(mention) != False:
                if mention not in mentions:
                    mentions.append(mention)
    oldMentions = []
    wordSplitOld = comment["Comment"].split()
    for work in wordSplitOld:
        if word.startswith("@") == True:
            mention = word.replace("@","")
            if getUser(mention) != False:
                if mention not in mentions:
                    oldMentions.append(mention)
    for i in oldMentions:
        try:
            mentions.remove(i)
        except:
            pass
    for mention in mentions:
        addNotification(mention, f"{username} mentioned you in an edited comment. Check it out <a href='/post/{comment['Post']}#comment-{commentID}'>here</a>!")
    if mentions != []:
        allMentions = ", ".join(mentions)
        addLog(f"{username} mentioned {allMentions} in an edited <a href='/post/{comment['Post']}#comment-{commentID}'>comment</a>.")
        addNotification(username, f"You mentioned {allMentions} in your edited <a href='/post/{comment['Post']}#comment-{commentID}'>comment</a>.")
    del comment["Comment"]
    comment["Comment"] = newComment
    delete = {"_id": ObjectId(commentID)}
    commentsCollection.delete_one(delete)
    commentsCollection.insert_many([comment])
    return True

def addLog(logText):
    fileOBJ = open("log.txt", "a")
    i = str(datetime.datetime.now())
    fileOBJ.write(f"\n[{i}] {logText}")
    fileOBJ.close()

def addReport(username, report):
    myQuery = {"Username": username}
    myDoc = reportsCollection.find(myQuery)
    allDocs = []
    for i in myDoc:
        allDocs.append(i)
    if allDocs == []:
        pass
    else:
        timeDoc = allDocs[-1]
        diff = datetime.datetime.now() - timeDoc["Time"]
        diffInSeconds = diff.total_seconds()
        if diffInSeconds < 600:
            return "You can only submit one report every 10 minutes. Please try again later."
    
    document = {"Username": username, "Report": report, "Time": datetime.datetime.now()}
    reportsCollection.insert_one(document)
    return True

def getAllReports():
    reports = []
    for report in reportsCollection.find():
        reports.append(report)
    return reports

def deleteReport(username, reportID):
    if username not in mods:
        return "You do not have permission to delete this report."
    myQuery = {"_id": ObjectId(reportID)}
    myDoc = reportsCollection.find(myQuery)
    reports = []
    for i in myDoc:
        reports.append(i)
    if reports == []:
        return "That report does not exist."
    delete = {"_id": ObjectId(reportID)}
    reportsCollection.delete_one(delete)
    return True

def changePassword(username, newPassword, oldPassword, newPasswordTwo):
    if newPassword != newPasswordTwo:
        return "The new passwords do not match."
    if check_password_hash(getHashedPassword(username), oldPassword) == False:
        addLog(f"{username} attempted to change their password but provided an incorrect current password.")
        return "Incorrect password."
    user2 = getUser(username)
    user = user2
    del user["Password"]
    passwordHash = generate_password_hash(newPassword)
    user["Password"] = passwordHash
    delete = {"_id" : user2["_id"]}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([user])
    addLog(f"{username} successfully changed their password.")
    addNotification(username, "You have successfully changed your password.")
    return True

def forgotPassword(username, email):
    user = getUser(username)
    userEmail = user["Email"]
    if userEmail.lower() != email.lower():
        addLog(f"{username} attempted to reset their password but provided an incorrect email.")
        return "The email provided does not match our records."
    myQuery = {"Username" : username}
    myDoc = forgotPasswordCollection.find(myQuery)
    allDocs = []
    for i in myDoc:
        allDocs.append(i)
    if allDocs == []:
        pass
    else:
        timeDoc = allDocs[-1]
        diff = datetime.datetime.now() - timeDoc["Time"]
        diffInSeconds = diff.total_seconds()
        if diffInSeconds < 3600:
            addLog(f"{username} attempted to reset their password but had already requested a reset within the last hour.")
            return "You can only request a password reset once every hour. Please try again later."
    newPassword = ""
    for i in range(12):
        theList = ['number', 'letter']
        theRandom = random.choice(theList)
        if theRandom == "number":
            thing = random.randint(0,9)
        if theRandom == "letter":
            thing = random.choice(string.ascii_letters)
        newPassword = newPassword + str(thing)
    
    funHTMLCode = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;}}
        .container {{max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(102, 126, 234, 0.2);}}
        .header {{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px 20px; text-align: center; border-radius: 12px 12px 0 0;}}
        .header h1 {{font-size: 24px;}}
        .content {{padding: 40px 30px;}}
        .content p {{font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 20px;}}
        .password-box {{background: #f9f9f9; border: 2px solid #667eea; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0;}}
        .password-box p {{font-size: 14px; color: #999; margin-bottom: 10px;}}
        .password {{font-size: 24px; font-weight: 800; color: #667eea; font-family: 'Courier New', monospace; letter-spacing: 3px;}}
        .warning {{background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 8px; margin: 20px 0;}}
        .warning p {{font-size: 14px; color: #856404; margin: 0;}}
        .footer {{background: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #eee; border-radius: 0 0 12px 12px;}}
        .footer p {{font-size: 12px; color: #999;}}
        .highlight {{color: #667eea; font-weight: 600;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset</h1>
        </div>
        <div class="content">
            <p>Hi <span class="highlight">{username}</span>,</p>
            <p>You requested a password reset for your GoodSoil account. Your temporary password is:</p>
            <div class="password-box">
                <p>Temporary Password</p>
                <div class="password">{newPassword}</div>
            </div>
            <div class="warning">
                <p><strong>⚠️ Important:</strong> Please log in immediately and change this password to something secure. Do not share this password with anyone.</p>
            </div>
            <p style="font-size: 14px; color: #666;">If you didn't request this reset, you can ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 GoodSoil. All rights reserved.</p>
            <p>This is an automated message, please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""
    try:
        params = {
            "from": "GoodSoil <noreply@korbindev.tech>",
            "to": [userEmail],
            "subject": "GoodSoil Password Reset",
            "html": funHTMLCode,
        }
        resend.Emails.send(params)
    except Exception as e:
        print(f"Forgot password email error: {e}")
        return "Request to send email failed. Please try again later."
    
    document = {"Username": username, "Time": datetime.datetime.now()}
    forgotPasswordCollection.insert_many([document])
    passwordHash = generate_password_hash(newPassword)
    user = getUser(username)
    del user["Password"]
    user["Password"] = passwordHash
    delete = {"_id": user["_id"]}
    profilesCollection.delete_one(delete)
    profilesCollection.insert_many([user])
    addLog(f"{username} successfully reset their password.")
    return True
# Work in progress
# TODO: finalize account deletion function
def deleteAccountLink(username, usernameLink, email, password, passwordTwo):
    if username != usernameLink:
        addLog(f"{username} attempted to delete the account of {usernameLink}.")
        return "You do not have permission to delete this account."
    if password != passwordTwo:
        return "The passwords do not match."
    if getUser(username)["Email"] != email:
        addLog(f"{username} attempted to delete their account but provided an incorrect email.")
        return "The email provided does not match our records."
    if check_password_hash(getHashedPassword(username), password) == False:
        addLog(f"{username} attempted to delete their account but provided an incorrect password.")
        return "The password provided is incorrect."
    deleteAccountList = []
    myQuery = {"Username": username}
    myDoc = deleteAccountsCollection.find(myQuery)
    for i in myDoc:
        deleteAccountList.append(i)
    if deleteAccountList == []:
        pass
    else:
        timeDoc = deleteAccountList[-1]
        diff = datetime.datetime.now() - timeDoc["Time"] 
        diffInSeconds = diff.total_seconds()
        if diffInSeconds < 600:
            return "You can only request account deletion once every 10 minutes. Please try again later."
    document = [{"Username": username, "Time": datetime.datetime.now()}]
    deleteAccountsCollection.insert_many(document)
    deleteAccountsList = []
    myQuery = {"Username": username}
    myDoc = deleteAccountsCollection.find(myQuery)
    for i in myDoc:
        deleteAccountsList.append(i)
    id = deleteAccountsList[-1]["_id"]
    
    funHTMLCode = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); padding: 20px;}}
        .container {{max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(231, 76, 60, 0.2);}}
        .header {{background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 30px 20px; text-align: center; border-radius: 12px 12px 0 0;}}
        .header h1 {{font-size: 24px;}}
        .content {{padding: 40px 30px;}}
        .content p {{font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 20px;}}
        .warning {{background: #ffe6e6; border-left: 4px solid #e74c3c; padding: 20px; border-radius: 8px; margin: 20px 0;}}
        .warning p {{color: #c0392b; margin: 0;}}
        .button {{display: inline-block; background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 20px 0;}}
        .footer {{background: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #eee; border-radius: 0 0 12px 12px;}}
        .footer p {{font-size: 12px; color: #999;}}
        .highlight {{color: #e74c3c; font-weight: 600;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Account Deletion Request</h1>
        </div>
        <div class="content">
            <p>Hi <span class="highlight">{username}</span>,</p>
            <p>You requested to delete your GoodSoil account. To confirm this action, please click the button below:</p>
            <a href='https://www.goodsoil.online/deleteaccount/{username}/{str(id)}' class="button">Confirm Account Deletion</a>
            <div class="warning">
                <p><strong>⚠️ Warning:</strong> This action is permanent and cannot be undone. All your posts, comments, and data will be deleted.</p>
            </div>
            <p style="font-size: 14px; color: #666;">If you didn't request this, you can ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; 2026 GoodSoil. All rights reserved.</p>
            <p>If this is an error, please send a report.</p>
        </div>
    </div>
</body>
</html>
"""
    try:
        userEmail = getUser(username)["Email"]
        params = {
            "from": "GoodSoil <noreply@korbindev.tech>",
            "to": [userEmail],
            "subject": "GoodSoil Account Deletion Confirmation",
            "html": funHTMLCode,
        }
        resend.Emails.send(params)
        addLog(f"{username} requested to delete their account. A confirmation email has been sent to {userEmail}.")
        return True
    except Exception as e:
        print(f"Delete account email error: {e}")
        return "Request to send email failed. Please try again later."

  #TODO: finish  
def deleteAccount(username, usernameLink, id):
    if username != usernameLink:
        addLog(f"{username} attempted to delete the account of {usernameLink}.")
        return f"You do not have permission to delete {usernameLink}'s account."
    email = getUser(username)["Email"]
    deleteAccountList = []
    myQuery = {"_id": ObjectId(id)}
    myDoc = deleteAccountsCollection.find(myQuery)
    for i in myDoc:
        deleteAccountList.append(i)
    if deleteAccountList == []:
        return "Invalid account deletion request."
    timeDoc = deleteAccountList[-1]
    if username != timeDoc["Username"]:
        return f"This is not a link to delete the account of {username}."
    diff = datetime.datetime.now() - timeDoc["Time"]
    diffInSeconds = diff.total_seconds()
    if diffInSeconds > 600:
        return "This account deletion link has expired. Please request a new account deletion."
    weDeleteThis = {"Username": username}
    deleteAccountsCollection.delete_many(weDeleteThis)
    notificationsCollection.delete_many(weDeleteThis)
    settingsCollection.delete_many(weDeleteThis)
    followRequestsCollection.delete_many({"Follower": username})
    followRequestsCollection.delete_many({"Following": username})
    forgotPasswordCollection.delete_many(weDeleteThis)
    for post in allUserPosts(username):
        commentsCollection.delete_many({"Post": post["_id"]})
    postsCollection.delete_many({"Author": username})
    commentsCollection.delete_many({"Author": username})
    delete = {"Username": username}
    profilesCollection.delete_one(delete)
    addLog(f"{username} has successfully deleted their account.")
    
    funHTMLCode = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        * {{margin: 0; padding: 0; box-sizing: border-box;}}
        body {{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%); padding: 20px;}}
        .container {{max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 10px 40px rgba(76, 175, 80, 0.2);}}
        .header {{background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%); color: white; padding: 30px 20px; text-align: center; border-radius: 12px 12px 0 0;}}
        .header h1 {{font-size: 24px;}}
        .content {{padding: 40px 30px;}}
        .content p {{font-size: 16px; color: #333; line-height: 1.6; margin-bottom: 20px;}}
        .footer {{background: #f5f5f5; padding: 20px; text-align: center; border-top: 1px solid #eee; border-radius: 0 0 12px 12px;}}
        .footer p {{font-size: 12px; color: #999;}}
        .highlight {{color: #4CAF50; font-weight: 600;}}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Account Deleted</h1>
        </div>
        <div class="content">
            <p>Hi <span class="highlight">{username}</span>,</p>
            <p>Your GoodSoil account has been successfully deleted. We're sorry to see you go.</p>
            <p>If you have any feedback or if there's anything we could have done better, please let us know by replying to this email.</p>
            <p style="margin-top: 30px; font-size: 14px; color: #666;">Best wishes,<br><strong>The GoodSoil Team</strong></p>
        </div>
        <div class="footer">
            <p>&copy; 2026 GoodSoil. All rights reserved.</p>
            <p>This is an automated message.</p>
        </div>
    </div>
</body>
</html>
"""
    try:
        params = {
            "from": "GoodSoil <noreply@korbindev.tech>",
            "to": [email],
            "subject": "GoodSoil Account Deletion Confirmation",
            "html": funHTMLCode,
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Account deletion confirmation email error: {e}")
        return True  # Still return True since account is already deleted


def topTen():
    number = 0
    posts = []
    pinned = []
    myDoc = postsCollection.find({"Type": "Public"}).sort([("Pinned", -1), ("Likes", -1)])
    for post in myDoc:
        if post.get("Pinned", False):
            pinned.append(post)
        else:
            if number == 10:
                break
            posts.append(post)
            number += 1
    return pinned + posts

def pinPost(username, postID):
    if username not in mods:
        return "You do not have permission to pin this post."
    post = getPostByID(int(postID))
    if post == False:
        return "That post does not exist."
    post["Pinned"] = True
    delete = {"_id": int(postID)}
    postsCollection.delete_one(delete)
    postsCollection.insert_many([post])
    addLog(f"{username} pinned the post titled '{post['Title']}' by {post['Author']}")
    return True

def unpinPost(username, postID):
    if username not in mods:
        return "You do not have permission to unpin this post."
    post = getPostByID(int(postID))
    if post == False:
        return "That post does not exist."
    post["Pinned"] = False
    delete = {"_id": int(postID)}
    postsCollection.delete_one(delete)
    postsCollection.insert_many([post])
    addLog(f"{username} unpinned the post titled '{post['Title']}' by {post['Author']}")
    return True


    


    

