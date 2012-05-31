from testtool.models import UserProfile

def has_user_profile(u):
    try:
        u.get_profile()
    except UserProfile.DoesNotExist:
        return False
    else:
        return True