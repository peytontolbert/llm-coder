from user import User

class Account:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def create_account(self):
        user = User(self.username)
        user.save_user()
        return "Account created successfully."