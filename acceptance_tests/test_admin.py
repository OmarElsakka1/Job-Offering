from functions import Adapter, LoginActionTesting

BASE_URL = "http://127.0.0.1"  # "http://localhost" #


def test_add_admin():
    email = "admin2@Shaghlni.com"
    password = "1234567"
    succes_msg = "Account created!\n×"
    fail_passmatch_msg = "Passwords don't match!\n×"
    fail_pass_length_msg = "Password must be at least"
    #fail_emailformat_msg = "Email has Invalid format!\n×"
    fail_emailexist_msg = "Email already exists!\n×"
    fail_fistlength_msg = "First name must be at least"
    fail_lastlength_msg = "Last name must be at least"

    path = f"{BASE_URL}/admin/adminlogin"
    pathform = f"{BASE_URL}/admin/adminadd_admin"

    # Testing Good account
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=succes_msg,
        newemail="admin3@Shaghlni.com",
        firstname="Mahrous",
        lastname="Nour",
        pass1="1234567",
        pass2="1234567")
    # Testing not typical passwords formatting
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=fail_passmatch_msg,
        newemail="admin4@Shaghlni.com",
        firstname="Mahrous",
        lastname="Nour",
        pass1="123",
        pass2="1234567")
    # Testing Small Password formatting
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=fail_pass_length_msg,
        newemail="admin5@Shaghlni.com",
        firstname="Mahrous",
        lastname="Nour",
        pass1="123",
        pass2="123")
    # Testing Small First name formatting
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=fail_fistlength_msg,
        newemail="admin6@Shaghlni.com",
        firstname="M",
        lastname="Nour",
        pass1="1234567",
        pass2="1234567")
    # Testing Small Last name formatting
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=fail_lastlength_msg,
        newemail="admin7@Shaghlni.com",
        firstname="Mahrous",
        lastname="N",
        pass1="1234567",
        pass2="1234567")

    # Testing good account
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=succes_msg,
        newemail="admin8@Shaghlni.com",
        firstname="Omar",
        lastname="Ali",
        pass1="1234567",
        pass2="1234567")

    # Testing good account
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=succes_msg,
        newemail="admin9@Shaghlni.com",
        firstname="Hanan",
        lastname="Abdelrahman",
        pass1="sdfghjk",
        pass2="sdfghjk")

    # Testing sign up with alread existing account
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=fail_emailexist_msg,
        newemail="admin9@Shaghlni.com",
        firstname="Mahrous",
        lastname="Nour",
        pass1="sdfghjk",
        pass2="sdfghjk")

    # Testing good account
    assert Adapter(
        path,
        pathform).do_login_add_admin(
        email=email,
        password=password,
        msg=succes_msg,
        newemail="admin10@Shaghlni.com",
        firstname="abdelhamed",
        lastname="Anwar",
        pass1="sdfghjk",
        pass2="sdfghjk")


def test_change_password():
    email = "admin2@Shaghlni.com"
    password = "1234567"
    success_msg = "Password Changed Successfully!\n×"
    page = "adminchangepassword"
    button = "admin_chgpass_submit"
    path = f"{BASE_URL}/admin/adminlogin"

    assert LoginActionTesting(
        path, email, password).do_change_password_action(
        password, "sdfghjk", success_msg, page, button)
    assert LoginActionTesting(
        path, email, "sdfghjk").do_change_password_action(
        "sdfghjk", password, success_msg, page, button)
    assert LoginActionTesting(
        path,
        email,
        password).do_change_password_action(
        password,
        "1234",
        success_msg,
        page,
        button) == False
    assert LoginActionTesting(
        path,
        email,
        password).do_change_password_action(
        "1234",
        "sdfghjk",
        success_msg,
        page,
        button) == False