import datetime
import os
import re
from dateutil.relativedelta import relativedelta
import boto3 as boto3
from flask import Flask, render_template, request, redirect, session, jsonify
import pymysql
second_sale_region_aws_name = 'us-east-1'
second_sale_bucket_aws_name = "insurence-management-s3-project"
second_sale_email_aws_name = 'sksharmila1922@gmail.com'
second_sale_s3_aws_name = boto3.client('s3', aws_access_key_id="AKIA6E6I24PMFYM3NRPD", aws_secret_access_key="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")
second_sale_ses_aws_name = boto3.client('ses', aws_access_key_id="AKIA6E6I24PMFYM3NRPD", aws_secret_access_key="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", region_name=second_sale_region_aws_name)
# conn = pymysql.connect(host="localhost", user="root", password="Venu@123", db="secondsale_shopping")
conn = pymysql.connect(host="insurencemanagementrds.cwhayzj5qrw4.us-east-1.rds.amazonaws.com", user="admin", password="admin123", db="secondsale_shopping")
cursor = conn.cursor()


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static"


app = Flask(__name__)
app.secret_key = "kjdarsiodughdgrs"

@app.route("/")
def index():
    cursor.execute("select * from transaction where status = 'Product sold'")
    transactions = cursor.fetchall()
    print(transactions)
    for transaction in transactions:
        settlement_date = transaction[6]
        current_date = datetime.date.today()
        settlement_date = datetime.datetime.strptime(settlement_date, "%Y-%m-%d").date()
        transaction_id = transaction[0]
        if settlement_date <= current_date:
            cursor.execute("update transaction set status= 'Amount Settled' where transaction_id='" + str(transaction_id) + "'")
            conn.commit()
    return render_template("home.html")

@app.route("/email_verify")
def email_verify():
    return render_template("email_verify.html")

@app.route("/email_verify1")
def email_verify1():
    email = request.args.get("email")
    second_sale_ses_aws_name.verify_email_address(
        EmailAddress=email
    )
    return render_template("message.html", msg="Click on the link to verify your emailid", color='text-success')

@app.route("/aLogin")
def aLogin():
    return render_template("aLogin.html")


@app.route("/aLogin1", methods=['post'])
def aLogin1():
    user_name = request.form.get("user_name")
    password = request.form.get("password")
    if user_name == 'admin' and password == 'admin':
        session['role'] = "admin"
        return render_template("admin.html")
    else:
        return render_template("message.html", msg="Invalid login details", color='text-danger')


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("home.html")


@app.route("/addCategory")
def addCategory():
    cursor.execute("select * from category")
    categories = cursor.fetchall()
    return render_template("addCategory.html", categories=categories)


@app.route("/addCategory1", methods=['post'])
def addCategory1():
    category_name = request.form.get("category_name")
    count = cursor.execute("select * from category where category_name = '"+str(category_name)+"'")
    if count > 0:
        return render_template("amsg.html", msg="Category Exists", color='text-danger')
    else:
        cursor.execute("insert into category(category_name) values('" + str(category_name) + "')")
        conn.commit()
        return render_template("amsg.html", msg="Category Added Successfully", color='text-success')


@app.route("/add_sub_Category")
def add_sub_Category():
    cursor.execute("select * from category")
    categories = cursor.fetchall()
    cursor.execute("select * from sub_category")
    sub_categories = cursor.fetchall()
    return render_template("add_sub_Category.html", categories=categories, sub_categories=sub_categories, get_category_by_subCategory_id=get_category_by_subCategory_id)


@app.route("/add_sub_Category1",methods=['post'])
def add_sub_Category1():
    subcategory_name = request.form.get("subcategory_name")
    category_id = request.form.get("category_id")
    cursor.execute("insert into sub_category(sub_category_name,category_id) values('" + str(subcategory_name) + "', '" + str(category_id) + "')")
    conn.commit()
    return render_template("amsg.html", msg="SubCategory Added Successfully", color='text-success')


def get_category_by_subCategory_id(category_id):
    cursor.execute("select * from category where category_id = '" + str(category_id) + "'")
    categorie = cursor.fetchall()
    return categorie[0]


@app.route("/uLogin")
def uLogin():
    return render_template("uLogin.html")

@app.route("/user_reg")
def user_reg():
    return render_template("user_reg.html")


@app.route("/userReg1",methods=['post'])
def userReg1():
    name = request.form.get("name")
    phone = request.form.get("phone")
    about = request.form.get("about")
    email = request.form.get("email")
    password = request.form.get("password")
    address = request.form.get("address")
    count = cursor.execute("select * from user where  phone = '"+str(phone)+"' or email = '"+str(email)+"'")
    if count == 0:
        user_ids = second_sale_ses_aws_name.list_identities(
            IdentityType='EmailAddress'
        )
        if email in user_ids['Identities']:
            user_details = 'You' + '' + ' Have Sucessfully Registered In to Second Sale Website'
            second_sale_ses_aws_name.send_email(Source=second_sale_email_aws_name, Destination={'ToAddresses': [email]},
                                            Message={'Subject': {'Data': user_details, 'Charset': 'utf-8'},
                                                     'Body': {'Html': {'Data': user_details, 'Charset': 'utf-8'}}})
            cursor.execute( "insert into user(name,email,phone,password,address,about,status) values('" + str(name) + "', '" + str(email) + "', '" + str(phone) + "', '" + str(password) + "', '" + str(address) + "', '" + str(about) + "', 'unauthorised')")
            conn.commit()
            return render_template("message.html", msg="You Have Successfully Registered.", color='text-success')
        else:
            return render_template("message.html", msg="User You Have not Verified Your Email.Please verify Your EMAIL and Login or Register", color='text-danger')
    else:
        return render_template("message.html", msg="Failed To Register", color='text-danger')


@app.route("/viewUsers")
def viewUsers():
    cursor.execute("select * from user")
    users = cursor.fetchall()
    return render_template("viewUsers.html", users=users)


@app.route("/authorize_user")
def authorize_user():
    user_id = request.args.get("user_id")
    cursor.execute("update user set status= 'authorised' where user_id='" + str(user_id) + "'")
    conn.commit()
    return viewUsers()


@app.route("/un_authorize_user")
def un_authorize_user():
    user_id = request.args.get("user_id")
    cursor.execute("update user set status= 'unauthorised' where user_id='" + str(user_id) + "'")
    conn.commit()
    return viewUsers()


@app.route("/uLogin1",methods=['post'])
def uLogin1():
    email = request.form.get("email")
    password = request.form.get("password")
    total_count = cursor.execute("select * from user where  password = '"+str(password)+"' and email = '"+str(email)+"'")
    if total_count > 0:
        results = cursor.fetchall()

        user_mails = second_sale_ses_aws_name.list_identities(
            IdentityType='EmailAddress'
        )
        if email in user_mails['Identities']:
            user_mails_detail = 'You' + '' + ' Have Sucessfully Logged In to Second Sale Website'
            second_sale_ses_aws_name.send_email(Source=second_sale_email_aws_name, Destination={'ToAddresses': [email]},
                                            Message={'Subject': {'Data': user_mails_detail, 'Charset': 'utf-8'},
                                                     'Body': {'Html': {'Data': user_mails_detail, 'Charset': 'utf-8'}}})

            for result in results:
                if result[7] == 'authorised':
                        session['user_id'] = result[0]
                        session['role'] = "user"
                        return redirect("/uhome")
                else:
                    return render_template("message.html", msg="Your Account Not Verified", color='text-warning')
        else:
            return render_template("message.html", msg="User Not Verified. Please verify Your EMAIL and Login", color='text-danger')
    else:
        return render_template("message.html", msg="Invalid login details", color='text-danger')


@app.route("/uhome")
def uhome():
    user_id = session["user_id"]
    cursor.execute("select * from user where user_id = '" + str(user_id) + "'")
    user = cursor.fetchall()
    seller_name = user[0][1]
    other_user_id = request.args.get('other_user_id')
    cursor.execute("select * from user where user_id in(select receiver_id from chat where sender_id = '"+str(user_id)+"') and user_id in(select sender_id from chat where receiver_id = '"+str(user_id)+"')")
    users = cursor.fetchall()
    return render_template("uhome.html",users=users,seller_id=user_id,seller_name=seller_name,str=str)


@app.route("/sell_product")
def sell_product():
    return render_template("sell_product.html")


@app.route("/choose_category")
def choose_category():
    cursor.execute("select * from category")
    categories = cursor.fetchall()
    return render_template("choose_category.html", categories=categories)


@app.route("/choose_sub_categories")
def choose_sub_categories():
    category_id = request.args.get("category_id")
    cursor.execute("select * from sub_category where category_id = '"+str(category_id)+"'")
    sub_categories = cursor.fetchall()
    return render_template("choose_sub_categories.html", sub_categories=sub_categories)


@app.route("/product_details")
def product_details():
    sub_category_id = request.args.get("sub_category_id")
    return render_template("product_details.html", sub_category_id=sub_category_id)


@app.route("/product_details1",methods=['post'])
def product_details1():
    sub_category_id = request.form.get("sub_category_id")
    product_name = request.form.get("product_name")
    price = request.form.get("price")
    picture = request.files.get("picture")
    path = APP_ROOT + "/Product_Images/" + picture.filename
    picture.save(path)
    second_sale_s3_aws_name.upload_file(path, second_sale_bucket_aws_name, picture.filename)
    picture_name = picture.filename
    picture_link = f'https://{second_sale_bucket_aws_name}.s3.amazonaws.com/{picture_name}'
    description = request.form.get("description")
    seller_id = session['user_id']
    cursor.execute("insert into product(product_name,price,picture,description,sub_category_id,seller_id,posted_date,status) values('" + str(product_name) + "', '" + str(price) + "', '" + str(picture_link) + "', '" + str(description) + "', '" + str(sub_category_id) + "', '" + str(seller_id) + "', '" + str(datetime.datetime.now()) + "', 'Available')")
    conn.commit()
    return render_template("umsg.html", msg="Product Posted", color='text-success')



@app.route("/viewProducts")
def viewProducts():
    category_id = request.args.get("category_id")
    sub_category_id = request.args.get("sub_category_id")
    product_name = request.args.get("product_name")
    if product_name == None:
        product_name = ""
    if category_id == None:
        category_id = "all"
    if sub_category_id == None:
        sub_category_id = "all"

    query = ""
    if category_id == 'all' and sub_category_id == 'all' and product_name == '':
        query = "select * from product where status = 'Available'"
    if category_id == 'all' and sub_category_id == 'all' and product_name != '':
        query = "select * from product where product_name like '%" + str(product_name) + "%' and status = 'Available'"
    elif category_id == 'all' and sub_category_id != 'all' and product_name == '':
        query = "select * from product where sub_category_id = '"+str(sub_category_id)+"' and status = 'Available'"
    elif category_id == 'all' and sub_category_id != 'all' and product_name != '':
        query = "select * from product where product_name like '%" + str(product_name) + "%' and status = 'Available' and sub_category_id = '"+str(sub_category_id)+"'"
    elif category_id != 'all' and sub_category_id == 'all' and product_name == '':
        query = "select * from product where sub_category_id in(select sub_category_id from sub_category where category_id = '"+str(category_id)+"' or status = 'Available')"
    elif category_id != 'all' and sub_category_id == 'all' and product_name != '':
        query = "select * from product where sub_category_id in(select sub_category_id from sub_category where category_id = '" + str(category_id) + "' or status = 'Available' or product_name like '%" + str(product_name) + "%')"
    elif category_id != 'all' and sub_category_id != 'all' and product_name == '':
        query = "select * from product where sub_category_id = '"+str(sub_category_id)+"' and status = 'Available'"
    elif category_id != 'all' and sub_category_id != 'all' and product_name != '':
        query = "select * from product where product_name like '%" + str(product_name) + "%' and status = 'Available' and sub_category_id = '"+str(sub_category_id)+"'"
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.execute("select * from category")
    categories = cursor.fetchall()
    print(category_id)
    if category_id !='all':
        cursor.execute("select * from sub_category where category_id = '"+str(category_id)+"'")
        sub_categories = cursor.fetchall()
    else:
        sub_categories = []
    return render_template("viewProducts.html", is_product_seller1=is_product_seller1, category_id=category_id, sub_category_id=sub_category_id, categories=categories, sub_categories=sub_categories, products=products, get_sub_category_by_products=get_sub_category_by_products, get_category_by_sub_category=get_category_by_sub_category, get_seller_by_posted_products=get_seller_by_posted_products, str=str, product_name=product_name)


def get_sub_category_by_products(sub_category_id):
    cursor.execute("select * from sub_category where sub_category_id = '" + str(sub_category_id) + "'")
    sub_category = cursor.fetchall()
    return sub_category[0]


def get_category_by_sub_category(category_id):
    cursor.execute("select * from category where category_id = '" + str(category_id) + "'")
    category = cursor.fetchall()
    return category[0]


def get_seller_by_posted_products(seller_id):
    cursor.execute("select * from user where user_id = '" + str(seller_id) + "'")
    seller = cursor.fetchall()
    return seller[0]


@app.route("/view_details")
def view_details():
    seller_id = request.args.get("seller_id")
    product_id = request.args.get("product_id")
    cursor.execute("select * from product where product_id = '"+str(product_id)+"'")
    product = cursor.fetchall()
    buyer_id = session['user_id']
    return render_template("view_details.html", buyer_id=buyer_id, product=product[0], seller_id=seller_id, get_seller_by_posted_products=get_seller_by_posted_products, get_sub_category_by_products=get_sub_category_by_products, get_category_by_sub_category=get_category_by_sub_category, is_product_seller=is_product_seller, str=str)


def is_product_seller(product_id):
    cursor.execute("select * from product where product_id = '" + str(product_id) + "'")
    product_seller = cursor.fetchall()
    print(session['user_id'])
    print(product_seller[0][8])
    if product_seller[0][8] == session['user_id']:
        return False
    else:
        return True


def is_product_seller1(product_id):
    cursor.execute("select * from product where product_id = '" + str(product_id) + "'")
    product_seller = cursor.fetchall()
    print(session['user_id'])
    print(product_seller[0][8])
    if product_seller[0][8] == session['user_id']:
        return True
    else:
        return False


@app.route("/buyer_requests")
def buyer_requests():
    cursor.execute("select * from transaction where status = 'Product Return Request Sent' or status = 'Requested' or status = 'Product sold' or status = 'Amount Settled' or status = 'Request Cancelled By buyer' or status = 'Rejected' or status = 'Accepted' and seller_id = '"+str(session['user_id'])+"'")
    transactions = cursor.fetchall()
    return render_template("buyer_requests.html", transactions=transactions, get_product_by_transactions=get_product_by_transactions, get_sub_category_by_transactions=get_sub_category_by_transactions,get_category_by_transactions=get_category_by_transactions,get_buyer_by_transactions=get_buyer_by_transactions,get_seller_by_transactions=get_seller_by_transactions)


@app.route("/accept_return_request", methods=['post'])
def accept_return_request():
    transaction_id = request.form.get("transaction_id")
    cursor.execute("update transaction set status= 'Return Request Accepted' where transaction_id='" + str(transaction_id) + "'")
    conn.commit()
    cursor.execute("select * from transaction where transaction_id = '" + str(transaction_id) + "'")
    product = cursor.fetchall()
    product_id = product[0][7]
    print(product_id)
    cursor.execute("update product set status= 'Available' where product_id='" + str(product_id) + "'")
    conn.commit()
    return viewProducts()


@app.route("/make_offer")
def make_offer():
    seller_id = request.args.get("seller_id")
    product_id = request.args.get("product_id")
    return render_template("make_offer.html", product_id=product_id, seller_id=seller_id)


@app.route("/make_offer1",methods=['post'])
def make_offer1():
    seller_id = request.form.get("seller_id")
    product_id = request.form.get("product_id")
    requested_amount = request.form.get("requested_amount")
    buyer_id = session['user_id']
    seller_amount = (int(requested_amount) * 0.98)
    admin_amount = (int(requested_amount)*0.02)
    cursor.execute(
        "insert into transaction(requested_amount,seller_amount,admin_amount,seller_id,product_id,buyer_id,status) values('" + str(
            requested_amount) + "', '" + str(
            seller_amount) + "', '" + str(admin_amount) + "', '" + str(seller_id) + "', '" + str(
            product_id) + "', '" + str(buyer_id) + "', 'Requested')")
    conn.commit()
    return render_template("umsg.html", msg="Offer Requested", color='text-primary')


@app.route("/viewRequests")
def viewRequests():
    cursor.execute("select * from transaction where buyer_id = '" + str(session['user_id']) + "'")
    transactions = cursor.fetchall()
    return render_template("viewRequests.html", get_settlement_date_hold=get_settlement_date_hold, is_product_seller=is_product_seller, get_seller_by_transactions=get_seller_by_transactions, get_buyer_by_transactions=get_buyer_by_transactions, get_category_by_transactions=get_category_by_transactions, get_sub_category_by_transactions=get_sub_category_by_transactions, transactions=transactions, get_product_by_transactions=get_product_by_transactions)


def get_product_by_transactions(product_id):
    cursor.execute("select * from product where product_id = '" + str(product_id) + "'")
    product = cursor.fetchall()
    return product[0]


def get_sub_category_by_transactions(sub_category_id):
    cursor.execute("select * from sub_category where sub_category_id = '" + str(sub_category_id) + "'")
    sub_category = cursor.fetchall()
    return sub_category[0]


def get_category_by_transactions(category_id):
    cursor.execute("select * from category where category_id = '" + str(category_id) + "'")
    category = cursor.fetchall()
    return category[0]


def get_buyer_by_transactions(user_id):
    cursor.execute("select * from user where user_id = '" + str(user_id) + "'")
    buyer = cursor.fetchall()
    return buyer[0]


def get_seller_by_transactions(user_id):
    cursor.execute("select * from user where user_id = '" + str(user_id) + "'")
    seller = cursor.fetchall()
    return seller[0]


@app.route("/view_seller_requests")
def view_seller_requests():
    product_id = request.args.get("product_id")
    cursor.execute("select * from transaction where product_id = '" + str(product_id) + "'")
    transactions = cursor.fetchall()
    return render_template("view_seller_requests.html", transactions=transactions, get_product_by_transactions=get_product_by_transactions, get_sub_category_by_transactions=get_sub_category_by_transactions, get_category_by_transactions=get_category_by_transactions, get_buyer_by_transactions=get_buyer_by_transactions, get_seller_by_transactions=get_seller_by_transactions)


@app.route("/accept", methods=['post'])
def accept():
    transaction_id = request.form.get("transaction_id")
    cursor.execute("update transaction set status= 'Accepted' where transaction_id='" + str(transaction_id) + "'")
    conn.commit()
    return render_template("umsg.html", msg="Request Accepted", color='text-primary')


@app.route("/reject", methods=['post'])
def reject():
    transaction_id = request.form.get("transaction_id")
    cursor.execute("update transaction set status= 'Rejected' where transaction_id='" + str(transaction_id) + "'")
    conn.commit()
    return render_template("umsg.html", msg="Request Rejected", color='text-danger')


@app.route("/pay_amount", methods=['post'])
def pay_amount():
    amount = request.form.get("amount")
    transaction_id = request.form.get("transaction_id")
    return render_template("pay_amount.html", amount=amount, transaction_id=transaction_id)


@app.route("/pay_amount1",methods=['post'])
def pay_amount1():
    transaction_id = request.form.get("transaction_id")
    print(type(transaction_id))
    date = datetime.date.today()
    settlement_date = date + relativedelta(days=15)
    print(type(settlement_date))
    print(settlement_date)
    print(type(date))
    settlement_date = str(settlement_date)
    date = str(date)
    cursor.execute("update transaction set status= 'Product sold', date = '"+str(date)+"', settlement_date = '"+str(settlement_date)+"' where transaction_id='" + str(transaction_id) + "'")
    conn.commit()
    cursor.execute("select * from transaction where transaction_id = '" + str(transaction_id) + "'")
    product = cursor.fetchall()
    product_id = product[0][7]
    print(product_id)
    cursor.execute("update product set status= 'Product sold' where product_id='" + str(product_id) + "'")
    conn.commit()
    return viewRequests()


def get_settlement_date_hold(transaction_id):
    cursor.execute("select * from transaction where transaction_id = '" + str(transaction_id) + "'")
    transaction = cursor.fetchall()
    settlement_date = transaction[0][6]
    current_date = datetime.date.today()
    settlement_date = datetime.datetime.strptime(settlement_date, "%Y-%m-%d").date()
    if settlement_date >= current_date:
        return True
    else:
        return False


@app.route("/return_product",methods=['post'])
def return_product():
    transaction_id = request.form.get("transaction_id")
    cursor.execute("update transaction set status= 'Product Return Request Sent' where transaction_id='" + str(transaction_id) + "'")
    conn.commit()
    return viewRequests()


@app.route("/cancel_product",methods=['post'])
def cancel_product():
    transaction_id = request.form.get("transaction_id")
    cursor.execute("update transaction set status= 'Request Cancelled By buyer' where transaction_id='" + str(transaction_id) + "'")
    conn.commit()
    return viewRequests()


@app.route("/get_messages")
def get_messages():
    other_user_id = request.args.get('other_user_id')
    user_id = session['user_id']
    cursor.execute("select * from where chat where sender_id = '"+str(user_id)+"' or receiver_id = '"+str(other_user_id)+"' or sender_id = '"+str(other_user_id)+"' or receiver_id = '"+str(user_id)+"'")
    messages = cursor.fetchall()
    messages2 = []
    for message in messages:
        message[0] = str(message[0])
        message['sender_id'] = message[5]
        message['receiver_id'] = message[6]
        messages2.append(message)

    return {"messages": messages2}


@app.route("/get_message")
def get_message():
    other_user_id = request.args.get('other_user_id')
    user_id = session['user_id']
    print("select * from chat where sender_id = '" + str(user_id) + "' or receiver_id = '" + str(other_user_id) + "' or isSenderRead = 'unread' or sender_id = '" + str(other_user_id) + "' or receiver_id = '"+str(user_id)+"' or isReceiverRead = 'unread'")
    cursor.execute("select * from chat where sender_id = '" + str(user_id) + "' or receiver_id = '" + str(other_user_id) + "' or isSenderRead = 'unread' or sender_id = '" + str(other_user_id) + "' or receiver_id = '"+str(user_id)+"' or isReceiverRead = 'unread'")
    messages = cursor.fetchall()
    messages = list(messages)
    for message in messages:
        if str(message[5]) == user_id:
            cursor.execute("update chat set isSenderRead= 'read' where chat_id='" + str(message[0]) + "'")
            conn.commit()
        elif str(message[6]) == user_id:
            cursor.execute("update chat set isReceiverRead= 'read' where chat_id='" + str(message[0]) + "'")
            conn.commit()
    messages2 = []
    for message in messages:
        message[0] = str(message[0])
        message[5] = str(message[5])
        message[6] = str(message[6])
        messages2.append(message)
    return {"messages": messages2}


@app.route("/send_messages")
def send_messages():
    other_user_id = request.args.get('other_user_id')
    user_id = session['user_id']
    message = request.args.get('message')
    cursor.execute("insert into chat(sender_id,receiver_id,message,isSenderRead,isReceiverRead,date) values('" + str(user_id) + "', '" + str(other_user_id) + "', '" + str(message) + "', 'unread', 'read', '" + str(datetime.datetime.now()) + "')")
    conn.commit()
    return {"status": "ok"}


@app.route("/set_as_read_receiver")
def set_as_read_receiver():
    other_user_id = request.args.get('other_user_id')
    user_id = session['user_id']
    cursor.execute("update chat set isReceiverRead= 'read' where sender_id='" + str(other_user_id) + "' and receiver_id='" + str(user_id) + "'")
    conn.commit()
    return {"status": "ok"}


@app.route("/set_as_read_sender")
def set_as_read_sender():
    other_user_id = request.args.get('other_user_id')
    user_id = session['user_id']
    cursor.execute("update chat set isSenderRead= 'read' where sender_id='" + str(user_id) + "' and receiver_id='" + str(other_user_id) + "'")
    conn.commit()
    return {"status": "ok"}


@app.route("/my_profile")
def my_profile():
    user_id = session['user_id']
    cursor.execute("select * from user where user_id = '"+str(user_id)+"'")
    users = cursor.fetchall()
    return render_template("my_profile.html", users=users)


@app.route("/edit_profile")
def edit_profile():
    user_id = request.args.get("user_id")
    cursor.execute("select * from user where user_id = '" + str(user_id) + "'")
    user = cursor.fetchall()
    return render_template("edit_profile.html", user_id=user_id, user=user)


@app.route("/edit_profile1",methods=['post'])
def edit_profile1():
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    password = request.form.get("password")
    address = request.form.get("address")
    print("update user set name= '" + str(name) + "', email= '" + str(email) + "', phone= '" + str(phone) + "', password= '" + str(password) + "', address= '" + str(address) + "' where user_id='" + str(user_id) + "'")
    cursor.execute("update user set name= '" + str(name) + "', email= '" + str(email) + "', phone= '" + str(phone) + "', password= '" + str(password) + "', address= '" + str(address) + "' where user_id='" + str(user_id) + "'")
    conn.commit()
    return render_template("umsg.html", msg="User Profile Updated", color='text-success')


@app.route("/view_transactions")
def view_transactions():
    query = ""
    if session['role'] == "admin":
        query = "select * from transaction"
    elif session['role'] == "user":
        user_id = session['user_id']
        query = "select * from transaction where buyer_id = '"+str(user_id)+"' or seller_id = '"+str(user_id)+"'"
    cursor.execute(query)
    transactions = cursor.fetchall()
    return render_template("view_transactions.html", transactions=transactions, get_seller_by_transactions=get_seller_by_transactions, get_product_by_transactions=get_product_by_transactions, get_buyer_by_transactions=get_buyer_by_transactions)


app.run(debug=True)


