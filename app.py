from flask import Flask, request, render_template, redirect, send_file, Response
from string import printable
from werkzeug.security import check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functions import addCookie, getCookie, removeCookie, createAccount, getUser, getHashedPassword, verify, checkEmailExists, checkUsernameExists, add_Description, follow, unFollow, getNotifications, deletePost, allSeen, makePost, getPost, getPostByID, viewPost, editComment, getCommentByID, addLog, addReport, deleteReport, getAllReports, changePassword, getNotificationsNotShown, forgotPassword, deleteAccount, allFollowRequests, topTen, changePublicSettings, changeEmailSettings, addNotification, denyTheFollowRequest, getSettings, editAPost, send_mail, likePost, unlikePost, comment, getAllUserPrivatePosts, getAllUserPublicPosts, deleteComment, changeEmail, getComments, clearNotifications, acceptTheFolloweRequest, deleteAccountLink, checkFollowRequest
from functions import mods
import os
from dotenv import load_dotenv

from functions import init_collections
init_collections()


# Load environment variables from .env file
load_dotenv()

# Initialize Flask app we call BOOK
book = Flask(__name__, static_url_path='', static_folder='static', template_folder='templates')
book.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
book.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///secret.pfps"
book.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
book.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB
pfps = SQLAlchemy(book)

upload_folder = "./pfps"
book.config["UPLOAD_FOLDER"] = upload_folder

class IMG(pfps.Model):
    id = pfps.Column(pfps.Integer, primary_key = True)
    img = pfps.Column(pfps.Text, nullable = False)
    mimetype = pfps.Column(pfps.Text, nullable = False)

with book.app_context():
    pfps.create_all()

@book.route("/")
def index():
    if getCookie("User") == False:
        return render_template("login.html")
    else:
        return render_template("index.html", user = getUser(getCookie("User")), number = len(getNotificationsNotShown(getCookie("User"))), mods=mods, posts=topTen(), settings=getSettings(getCookie("User")))
    
@book.route("/logout")
def logout():
    if getCookie("User") == False:
        return render_template("error.html", error="You are not logged in!")
    username = getCookie("User")
    removeCookie("User")
    return redirect("/")
    
@book.route("/login")
def loginPage():
    if getCookie("User") == False:
        return render_template("login.html")
    else:
        return render_template("error.html", error="You are already logged in!")
    
@book.route("/signup")
def signupPage():
    if getCookie("User") == False:
        return render_template("signup.html")
    else:
        return render_template("error.html", error = "You are already logged in!")
    
@book.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        if getCookie("User") != False:
            return render_template("error.html", error = "You are already logged in! If you do not believe you are, try clearing cookies.")
        username = request.form["username"]
        if len(username) > 20:
            return render_template("error.html", error = "Username too long! Max length is 20 characters.")
        if len(username) < 3:
            return render_template("error.html", error = "Username too short! Min length is 3 characters.")
        if set(username).difference(printable):
            return render_template("error.html", error = "Please do not use special characters in your username!")
        if username != username.lower():
            return render_template("error.html", error = "Please only use lowercase letters in your username!")
        if checkUsernameExists(username):
            return render_template("error.html", error = "Username already exists! please choose another.")
        password = request.form["password"]
        password2 = request.form["passwordagain"]
        if password != password2:
            return render_template("error.html", error = "Passwords do not match!")
        if len(password) > 25:
            return render_template("error.html", error = "Password too long! Max length is 25 characters.")
        if len(password) < 5:
            return render_template("error.html", error = "Password too short! Min length is 5 characters.")
        if set(password).difference(printable):
            return render_template("error.html", error = "Please do not use special characters in your password!")
        email = str(request.form["email"]).lower()
        if checkEmailExists(email):
            return render_template("error.html", error = "An account with this email already exists! Please use another email.")
        function = createAccount(username, email, password)
        if function == True or function == None:
            addLog(f"Account Created: Account with username {username} has been created.")
            addCookie("User", username)
            return render_template("success.html", success = "Account created successfully! Pleaase check your email to verify your account.")
        else:
            addLog(f"Account Creation Failed: Account creation failed for username {username}. Error: {function}")
            return render_template("error.html", error = f"Account creation failed! Error: {function}")
        

@book.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        if getCookie("User") != False:
            return render_template("error.html", error = "You are already logged in!")
        username = request.form["username"]
        if getUser(username) == False:
            return render_template("error.html", error = "Username does not exist!")
        password = request.form["password"]
        if check_password_hash(getHashedPassword(username), password) == False:
            addLog(f"Failed Login Attempt: Failed login attempt for username {username}. Incorrect Password.")
            return render_template("error.html", error = "Incorrect password!")
        addLog(f"Successful Login: User {username} has logged in successfully.")
        addCookie("User", username)
        return redirect("/")
    
@book.route("/verify/<username>/<id>")
def verifyPage(username, id):
    function = verify(username, id)
    if function == True:
        addLog(f"Account Verified: Account with username {username} has been verified.")
        return render_template("success.html", success = "Account verified successfully! You can now log in.")
    else:
        return render_template("error.html", error = "This is not a valid verification link.")
    
@book.route("/profile/<username>")
def profile(username):
    username = username.lower()
    user_doc = getUser(username)
    if not user_doc:
        return render_template("error.html", error="This user does not exist!")

    follow = None
    requestPending = False

    viewer = getCookie("User")
    if viewer:
        if viewer == username:
            follow = None
        elif viewer in user_doc["Followers"]:
            follow = True
        else:
            follow = False
            # Only check pending if the account is private
            if not getSettings(username)["Public"]:
                requestPending = bool(checkFollowRequest(viewer, username))
    return render_template(
        "profile.html",
        profileUser=user_doc,
        follow=follow,
        mods=mods,
        requestPending=requestPending,
    )
    
@book.route("/add_description")
def add_description_page():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to add a description!")
    else:
        if getUser(getCookie("User"))["Verified"] == False:
            return render_template("error.html", error = "You must verify your account to add a description! Please check your email.")
        description = getUser(getCookie("User"))["Description"]
        if description == None:
            description = ""
        return render_template(
            "add_description.html",
            user=getUser(getCookie("User")),
            description=description
        )
    

@book.route("/add_description", methods=["POST", "GET"])
def add_description():
    if request.method == "POST":
        if getCookie("User") != False:
            if getUser(getCookie("User"))["Verified"] == False:
                return render_template("error.html", error = "You must verify your account to add a description! Please check your email.")
            description = request.form["description"]
            if len(description) > 150:
                return render_template("error.html", error = "Description too long! Max length is 150 characters.")
            function = add_Description(getCookie("User"), description)
            if function == True:
                addLog(f"Description Added: User {getCookie('User')} has added/updated their description.")
                return redirect(f"/profile/{getCookie('User')}")
            else:
                return render_template("error.html", error = f"An error occurred while adding your description! Error: {function}")
        else:
            return render_template("error.html", error = "You must be logged in to add a description!")
        
@book.route("/followers/<username>")
def followers(username):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to view followers!")
    else:
        if getUser(getCookie("User"))["Verified"] == False:
            return render_template("error.html", error = "You must verify your account to view followers! Please check your email.")
        user = getUser(username)
        return render_template("follow.html", name="Followers", user=user, message=f"{username} has no followers!")
    
@book.route("/following/<username>")
def following(username):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to view who this user is following!")
    else:
        if getUser(getCookie("User"))["Verified"] == False:
            return render_template("error.html", error = "You must verify your account to view who this user is following! Please check your email.")
        user = getUser(username)
        return render_template("follow.html", name="following", user=user, message = f"{username} is not following anyone!")
    
@book.route("/addpfp")
def addpfppage():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to add a profile picture!")
    else:
        if getUser(getCookie("User"))["Verified"] == False:
            return render_template("error.html", error = "You must verify your account to add a profile picture! Please check your email.")
        return render_template("addpfp.html")

@book.route("/addpfp", methods=["POST", "GET"])
def addpfp():
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to add a profile picture!")
        else:
            if getUser(getCookie("User"))["Verified"] == False:
                return render_template("error.html", error = "You must verify your account to add a profile picture! Please check your email.")
            try:
                username = getCookie("User")
                id = getUser(username)["_id"]
                img = IMG.query.filter_by(id=id).first()
                pfps.session.delete(img)
                pfps.session.commit()
            except:
                pass
            file1 = request.files["image"]
            mimetype = file1.mimetype
            img = IMG(img = file1.read(), mimetype=mimetype, id=getUser(getCookie("User"))["_id"])
            pfps.session.add(img)
            pfps.session.commit()
            addLog(f"Profile Picture Added: User {getCookie('User')} has added/updated their profile picture.")
            return redirect("/")
        
@book.route("/pfps/<username>")
def get_profile_user(username):
    try:
        id = getUser(username)["_id"]
        img = IMG.query.filter_by(id=id).first()
        return Response(img.img, mimetype=img.mimetype)
    except:
        return send_file("static/unnamed.png")
    
@book.route("/follow/<username>")
def follow_page(username):
    if getCookie("User") == False:
        return render_template("error.html", error="You must be logged in to follow users!")
    if getUser(getCookie("User"))["Verified"] == False:
        return render_template("error.html", error = "You must verify your account to follow users! Please check your email.")
    if getUser(username)["Verified"] == False:
        return render_template("error.html", error = f"You cannot follow {username} because they have not verified their account!")
    function = follow(getCookie("User"), username)
    if function == True:
        addLog(f"User Followed: User {getCookie('User')} has followed {username}.")
        return redirect(f"/profile/{username}")
    else:
        return render_template("error.html", error = f"An error occurred while trying to follow {username}! Error: {function}")
    
@book.route("/unfollow/<username>")
def unfollow_page(username):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to unfollow users!")
    if getUser(getCookie("User"))["Verified"] == False:
        return render_template("error.html", error = "You must verify your account to unfollow users! Please check your email.")
    function = unFollow(getCookie("User"), username)
    if function == True:
        addLog(f"User Unfollowed: User {getCookie('User')} has unfollowed {username}.")
        return redirect(f"/profile/{username}")
    else:
        return render_template("error.html", error = f"An error occured while trying to unfollow {username}! Error: {function}")
    
@book.route("/notifications")
def notifications():
    if getCookie("User") == False:
        return render_template("login.html")
    if getUser(getCookie("User")) == False:
        removeCookie("User")
        return redirect("/")
    notifications = getNotifications(getCookie("User"))
    allSeen(getCookie("User"))
    return render_template("notifications.html", notifications = notifications)
    
@book.route("/clear_notifications")
def clear_notifications():
    if getCookie("User") == False:
        return render_template("login.html")
    if getUser(getCookie("User")) == False:
        removeCookie("User")
        return redirect("/")
    clearNotifications(getCookie("User"))
    return redirect("/notifications")

@book.route("/make_post")
def make_post_page():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to make a post!")
    else:   
        user = getUser(getCookie("User"))
        if user == False:
            removeCookie("User")
            return render_template("error.html", error = "Account not found. Please log in again.")
        if user["Verified"] == False:
            return render_template("error.html", error = "You must verify your account to make a post! Please check your email.")
        return render_template("make_post.html", user=user)
    
@book.route("/make_post", methods=["POST", "GET"])
def make_post():
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("login.html")
        else:
            if getUser(getCookie("User"))["Verified"] == False:
                return render_template("error.html", error = "You must verify your account to make a post! Please check your email.")
            title = request.form["title"]
            description = request.form["description"]
            posttype = request.form["posttype"]
            if getPost(description) != False:
                return render_template("error.html", error = "A post with this description already exists! Please choose another description.")
            if len(description) > 1000:
                return render_template("error.html", error= "Description to long! Max length is 1000 characters.")
            makePost(getCookie("User"), title, description, posttype)
            id = str(getPost(description)["_id"])
            addLog(f"Post Made: User {getCookie('User')} has made a post: DOMAINHERE/post/{id}")
            return redirect(f"/post/{id}")

@book.route("/post/<id>")
def view_post(id):
    if getPostByID(id) == False:
        return render_template("error.html", error = "This post does not exist!")
    post = getPostByID(id)
    comments = getComments(id)

    perms = {"perms": False, "liked": False}
    if getCookie("User") != False:
        viewPost(id, getCookie("User"))
        if post["Author"] == getCookie("User") or getCookie("User") in mods:
            perms["perms"] = True
        if getCookie("User") in post["LikesPeople"]:
            perms["liked"] = True

    if post["Type"] == "Public":
        return render_template("post.html", post=post, perms=perms["perms"], liked=perms["liked"], comments=comments, mods=mods, username=getCookie("User"))
    else:
        if getCookie("User") in mods:
            return render_template("post.html", post=post, perms=True, liked=perms["liked"], comments=comments, mods=mods, username=getCookie("User"))
        elif getCookie("User") == post["Author"]:
            return render_template("post.html", post=post, perms=True, liked=perms["liked"], comments=comments, mods=mods, username=getCookie("User"))
        elif getCookie("User") in getUser(post["Author"])["Followers"]:
            return render_template("post.html", post=post, perms=False, liked=perms["liked"], comments=comments, mods=mods, username=getCookie("User"))
        else:
            return render_template("error.html", error = "You do not have permission to view this post!")
        

@book.route("/delete_post/<id>")
def delete_post(id):
    if getPostByID(id) == False:
        return render_template("error.html", error = "This post does not exist!")
    title = getPostByID(id)["Title"]
    author = getPostByID(id)["Author"]
    if getCookie("User") == False:
        return render_template("error.html", error="You must be logged in to delete a post!")
    function = deletePost(getCookie("User"), int(id))
    if function == True:
        addLog(f"Post Deleted: User {getCookie('User')} has deleted the post titled '{title}' made by {author}")
        return render_template("success.html", success = "Post deleted successfully!")
    else:
        return render_template("error.html", error = f"An error occurred while trying to delete this post! Error: {function}")
    
@book.route("/settings")
def settings():
    if getCookie("User") == False:
        return render_template("login.html")
    else:
        settings_doc = getSettings(getCookie("User"))
        return render_template("settings.html", user=getUser(getCookie("User")), settings=settings_doc)
    
@book.route("/settings/public")
def settings_public():
    if getCookie("User") == False:
        return render_template("login.html")
    else:
        function = changePublicSettings(getCookie("User"))
        if function == True:
            return redirect("/settings")
        else:
            return render_template("error.html", error = f"An error occurred while trying to change your settings! Error: {function}")
        
@book.route("/settings/emailnotifications")
def settings_emailnotifications():
    if getCookie("User") == False:
        return render_template("login.html")
    else:
        function = changeEmailSettings(getCookie("User"))
        if function == True:
            return redirect("/settings")
        else:
            return render_template("error.html", error = f"An error occurred while trying to change your settings! Error: {function}")
        
@book.route("/accept/<follower>/<following>")
def accept_follow(follower, following):
    if getCookie("User") == False:
        return render_template("login.html")
    if getUser(getCookie("User"))["Verified"] == False:
        return render_template("error.html", error = "You must verify your account to accept followers! Please check your email.")
    function = acceptTheFolloweRequest(getCookie("User"), follower, following)
    if function == True:
        addNotification(follower, f"{following} has accepted your follow request!")
        return render_template("success.html", success = f"You have accepted {follower} to follow you!")
    else:
        return render_template("error.html", error = f"An error occurred while trying to accept {follower}! Error: {function}")
        
@book.route("/decline/<follower>/<following>")
def decline_follow(follower, following):
    if getCookie("User") == False:
        return render_template("login.html")
    if getUser(getCookie("User"))["Verified"] == False:
        return render_template("error.html", error = "You must verify your account to decline followers! Please check your email.")
    function = denyTheFollowRequest(getCookie("User"), follower, following)
    if function == True:
        addLog(f"Follow Request Declined: User {getCookie('User')} has declined the follow request from {follower}.")
        return render_template("success.html", success = f"You have declined {follower} to follow you!")
    else:
        return render_template("error.html", error = f"An error occured while trying to decline {follower}! Error: {function}")
    
@book.route("/allfollowrequests")
def all_follow_requests():
    if getCookie("User") == False:
        return render_template("login.html")
    else:
        if getSettings(getCookie("User"))["Public"] == True:
            return render_template("error.html", error = "Your account is public, you do not have any follow requests!")
        else:
            return render_template("all_follow_requests.html", all_follow_requests = allFollowRequests(getCookie("User")))
        
@book.route("/publicposts/<username>")
def public_posts(username):
    username = username.lower()
    if getUser(username) == False:
        return render_template("error.html", error = f"The user: '{username}' does not exist!")
    else:
        posts = getAllUserPublicPosts(username)
        return render_template("posts.html", posts=posts, title=f"{username}'s Public Posts", username=username)
    
@book.route("/edit_post/<id>")
def edit_post_page(id):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to edit a post!")
    if getPostByID(id) == False:
        return render_template("error.html", error = "This post does not exist!")
    post = getPostByID(id)
    username = getCookie("User")
    if post["Author"] == username:
        pass
    elif username in mods:
        pass
    else:
        return render_template("error.html", error = "You do not have permission to edit this post!")
    return render_template("edit_post.html", post=post)

@book.route("/edit_post_function/<id>", methods=["POST", "GET"])
def edit_post(id):
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to edit a post!")
        if getPostByID(int(id)) == False:
            return render_template("error.html", error = "This post does not exist!")
        desctiption = request.form["description"]
        function = editAPost(getCookie("User"), int(id), desctiption)
        if function == True:
            return redirect(f"/post/{id}")
        else:
            return render_template("error.html", error = f"An error occurred while trying to edit this post! Error: {function}")

@book.route("/resend_verification")
def resend_verification():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to resend the verification email!")
    user = getUser(getCookie("User"))
    if user["Verified"] == True:
        return render_template("error.html", error = "Your account is alread verified!")
    function = send_mail(user["Email"], user["Username"], user["_id"])
    if function == True:
        return render_template("success.html", success = "Verification email resent successfully! Please check your email.")
    else:
        return render_template("error.html", error = f"An error occurred while trying to resend the verification email! Error: {function}")
    
@book.route("/likePost/<id>")
def like_post(id):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to like a post!")
    if getUser(getCookie("User"))["Verified"] == False:
        return render_template("error.html", error = "You must verify your account to like posts! Please check your email.")
    function = likePost(id, getCookie("User"))
    if function == True:
        return redirect(f"/post/{id}")
    else:
        return render_template("error.html", error = f"An error occurred while trying to like this post! Error: {function}")
    
@book.route("/unlikePost/<id>")
def unlike_post(id):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to unlike a post!")
    if getUser(getCookie("User"))["Verified"] == False:
        return render_template("error.html", error = "You must verify your account to unlike posts! Not sure how you liked it in the first place, but please check your email to verify.")
    function = unlikePost(id, getCookie("User"))
    if function == True:
        return redirect(f"/post/{id}")
    else:
        return render_template("error.html", error = f"An error occurred while trying to unlike this post! Error: {function}")

@book.route("/comment_post/<id>", methods=["POST", "GET"])
def comment_post(id):
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error="You must be logged in to comment on a post!")
        if getUser(getCookie("User"))["Verified"] == False:
            return render_template("error.html", error = "You must verify your account to comment on posts! Please check your email.")
        commenti = request.form["comment"]
        function = comment(getCookie("User"), id, commenti)
        if type(function) is str:
            return render_template("error.html", error = f"An error occurred while trying to comment on this post! Error: {function}")
        else:
            return redirect(function[0])

@book.route("/privateposts/<username>")
def private_posts(username):
    username = username.lower()
    if getUser(username) == False:
        return render_template("error.html", error = f"The user: '{username}' does not exist!")
    else:
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to view private posts!")
        if getCookie("User") not in getUser(username)["Followers"] and getCookie("User") != username:
            return render_template("error.html", error = "You do not have permission to view this user's private posts!")
        posts = getAllUserPrivatePosts(username)
        return render_template("posts.html", posts=posts, title=f"{username.upper()}'s PRIVATE POSTS", username=username)
    
@book.route("/delete_comment/<commentid>")
def delete_comment(commentid):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to delete a comment!")
    username = getCookie("User")
    function = deleteComment(username, commentid)
    if function == True:
        return render_template("success.html", success = "Comment deleted successfully!")
    else:
        return render_template("error.html", error = f"An error occurred while trying to delete this comment! Error: {function}")
    
@book.route("/change_email")
def change_email_page():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to change your email!")
    return render_template("change_email.html")

@book.route("/change_email", methods=["POST", "GET"])
def change_email():
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to change your email!")
        new_email = str(request.form["email"]).lower()
        function = changeEmail(getCookie("User"), new_email)
        if function == True:
            return render_template("success.html", success = "Email changed successfully! Please check your email to verify the new email address.")
        else:
            return render_template("error.html", error = f"An error occurred while trying to change your email! Error: {function}")
        
@book.route("/edit_comment/<commentid>")
def edit_comment_page(commentid):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to edit a comment!")
    if getCommentByID(commentid) == False:
        return render_template("error.html", error = "This comment does not exist!")
    post = getCommentByID(commentid)
    username = getCookie("User")
    if post["Author"] == username:
        pass
    elif username in mods:
        pass
    else:
        return render_template("error.html", error = "You do not have permission to edit this comment!")
    return render_template("edit_comment.html", desc=post["Comment"], commentid=commentid)
    
@book.route("/edit_comment_function/<commentid>", methods=["POST", "GET"])
def edit_comment(commentid):
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to edit a comment!")
        if getCommentByID(commentid) == False:
            return render_template("error.html", error = "This comment does not exist!")
        desc = request.form["desc"]
        function = editComment(getCookie("User"), commentid, desc)
        if function == True:
            comment_doc = getCommentByID(commentid)
            return redirect(f"/post/{str(comment_doc['Post'])}#comment-{commentid}")
        else:
            return render_template("error.html", error = f"An error occurred while trying to edit this comment! Error: {function}")

@book.route("/favicon.ico")
def favicon():
    return send_file("static/Logo.ico")    

@book.route("/make_report")
def make_report_page():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to make a report!")
    return render_template("make_report.html")

@book.route("/make_report", methods = ["POST", "GET"])
def make_report():
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to make a report!")
        description = request.form["description"]
        function = addReport(getCookie("User"), description)
        if function == True:
            addLog(f"Report Made: User {getCookie('User')} has made a report.")
            return render_template("success.html", success = "Report was made successfully! Thank you for helping to keep our community safe.")
        else:
            return render_template("error.html", error = f"An error occurred while tring to make this report! Error: {function}")
        
@book.route("/all_reports")
def all_reports():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to view reports!")
    if getCookie("User") not in mods:
        return render_template("error.html", error = "You do not have permission to view reports! Please respond to the verification email to request moderator access.")
    return render_template("reports.html", reports = getAllReports())

@book.route("/delete_report/<id>")
def delete_report_page(id):
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to delete reports!")
    if getCookie("User") not in mods:
        return render_template("error.html", error = "You do not have permission to delete reports! Please respond to the verification email to request moderator access.")
    function = deleteReport(getCookie("User"), id)
    if function == True:
        return redirect("/all_reports")
    else:
        return render_template("error.html", error = f"An error occurred while trying to delete this report! Error: {function}")

@book.route("/change_password")
def change_password_page():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to change your password!")
    return render_template("change_password.html")

@book.route("/change_password", methods=["POST", "GET"])
def change_password():
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to change your password!")
        old_password = request.form["oldpassword"]
        new_password = request.form["newpassword"]
        new_password2 = request.form["newpasswordagain"]
        function = changePassword(getCookie("User"), new_password, old_password, new_password2)
        if function == True:
            return render_template("success.html", success = "Password changed successfully!")
        else:
            return render_template("error.html", error = f"An error occurred while trying to change your password! Error: {function}")
        
@book.route("/forgot_password")
def forgot_password_page():
    return render_template("forgot_password.html")

@book.route("/forgot_password", methods=["POST", "GET"])
def forgot_password():
    if request.method == "POST":
        username = request.form["username"]
        email = str(request.form["email"]).lower()
        function = forgotPassword(username, email)
        if function == True:
            return render_template("success.html", success = "Password reset email sent successfully! Please check your email.")
        else:
            return render_template("error.html", error = f"An error occurred while trying to send the password reset email! Error: {function}")
    
@book.route("/delete_account")
def delete_account_page():
    if getCookie("User") == False:
        return render_template("error.html", error = "You must be logged in to delete your account!")
    return render_template("delete_account.html")

@book.route("/delete_account_function/<usernamelink>/<id>", methods = ["POST", "GET"])
def delet_account(usernamelink, id):
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to delete your account!")
        function = deleteAccount(getCookie("User"), usernamelink, id)
        if function == True:
            try:
                username = getCookie("User")
                id = getUser(username)["_id"]
                img = IMG.query.filter_by(id=id).first()
                pfps.session.delete(img)
                pfps.session.commit()
            except:
                pass
            removeCookie("User")
            return render_template("success.html", success  = "Account deleted successfully! we're sorry to see you go. :(")
        else:
            return render_template("error.html", error = f"An error occurred while trying to delete your account! Error: {function}")
        
@book.route("/delete_account", methods = ["POST", "GET"])
def delete_account():
    if request.method == "POST":
        if getCookie("User") == False:
            return render_template("error.html", error = "You must be logged in to delete your account!")
        usernamelink = request.form["usernamelink"]
        email = str(request.form["email"]).lower()
        password = request.form["password"]
        password2 = request.form["passwordagain"]
        function = deleteAccountLink(getCookie("User"), usernamelink, email, password, password2)
        if function == True:
            return render_template("success.html", success = "A confirmation email has been sent. Please check your inbox.")
        else:
            return render_template("error.html", error = f"An error occurred while trying to request account deletion! Error: {function}")
