""" This is the module that handles all the utilities functions """


import random


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# Helper function to check allowed file extension
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

 
# Genrating a random number for each product item added as key
def generate_random_number():
    """ This return the generated random number """
    return random.randint(1000, 9999)


def random_string(n):
    """ This is a function a random string for extra protection """
    characters = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    for _ in range(n):
        index = random.randint(0, len(characters) - 1)
        result += characters[index]
    return result


def get_day_suffix(day):
    """ This is a function that return the suffix of the date """
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return suffix
