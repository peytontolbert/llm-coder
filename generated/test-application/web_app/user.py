class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def create_account(self):
        account = Account()
        account.username = self.username
        account.password = self.password
        return account