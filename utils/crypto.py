import bcrypt


def encrypt_password(password, salt=None):
    """
    加密用户密码
    :param password: 用户密码
    :param salt: 盐值
    :return: 加密后的密码
    """
    if salt is None:
        salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt)


def verify_password(password, hashed):
    """
    验证用户密码
    :param password: 用户密码
    :param hashed: 加密后的密码
    :return: 是否匹配
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed)


if __name__ == '__main__':
    print(encrypt_password("Akkk1234"))
    print(verify_password("Akkk1234",
                          bytes("$2b$12$jIePRb50R29RxHjH6roM7uKLR/TkZ6tUYsCdm6ReSb7tauO4blJ3G", encoding="utf-8")))
