def is_instructor(user):
    return user.role == "instructor"

def is_admin(user):
    return user.role == "admin"

def is_student(user):
    return user.role == "student"