"""This module helps manager account data"""
from typing import Optional
import json
from dataclasses import dataclass


@dataclass
class User:
    """A user class storing all useful login/registeration functions for quick referral.

    Instance Attributes:
        - name: A string of the name of user:
        - password: A string of the password of user
    """

    name: str
    password: str


class Accounts:
    """A manager class for user accounts"""
    _accounts: dict[str, User]

    def __init__(self, data_file: str) -> None:
        """Initialize accounts by reading data from appropriate account file"""
        self._accounts = self.load(data_file)

    @staticmethod
    def load(account_file: str) -> dict[str, User]:
        """Load account data from json data file"""

        with open(account_file, "r") as file:
            account_data = json.load(file)

        user_dict = {}

        for account in account_data:
            user_obj = User(account, account_data[account]["password"])
            user_dict[account] = user_obj

        return user_dict

    def get_account(self, name: Optional[str] = None) -> dict[str, User] | User:
        """An accessor method used to access account object"""

        if name is None:
            return self._accounts
        else:
            return self._accounts[name]

    def get_all(self) -> set:
        """Return a set of all usernames"""
        return set(self._accounts.keys())

    def exist(self, username) -> bool:
        """Check if user exists via their username"""
        return username in self.get_all()

    def login(self, name: str, password: str) -> bool:
        """Check if name and passsword entered by user is the same as account info in database"""

        if name in self._accounts and password == self._accounts[name].password:
            return True
        else:
            return False

    def register(self, name: str, password: str) -> None:
        """Register a new account into the database with initial default game data"""

        self._accounts[name] = User(name, password)

        account_data = {}
        for account in self._accounts:
            data = self._accounts[account]
            account_data[account] = {"password": data.password}

        with open("account_data.json", "w") as f:
            json.dump(account_data, f, indent=2)

    def handle_login(self, username) -> User | None:
        """A function to help manage the prompt message for user account info，
        Return user oject containing user info"""

        return self.get_account()[username]

    def error(self, username, password, re_password, get_message: Optional[bool] = None) -> bool | str:
        """Return whether error has occured, and if get_message, return the error message."""

        error_message = ""
        error = False

        if any(not item for item in [username, password, re_password]):
            error = True
            error_message = "Please fill out all boxes."

        elif len(username) < 2 or len(username) > 8:
            error = True
            error_message = "Username should be 2 to 8 characters long."

        elif len(password) < 5 or len(password) > 8:
            error = True
            error_message = "Password should be 5 to 8 characters long."

        elif any(" " in x for x in [username, password, re_password]):
            error = True
            error_message = "Empty spaces are not allowed in username or password."

        elif password != re_password:
            error = True
            error_message = "Passwords do not match."

        elif self.exist(username):
            error = True
            error_message = "Username is taken."

        if get_message:
            return error_message

        else:
            return error


if __name__ == "__main__":
    # pass
    # When you are ready to check your work with python_ta, uncomment the following lines.
    # (Delete the "#" and space before each line.)
    # IMPORTANT: keep this code indented inside the "if __name__ == '__main__'" block
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['R1705', 'E9998', 'E9999']
    })
