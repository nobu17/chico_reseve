from . import models


class ReserveDuplicateCheck:
    def __init__(self, user):
        self.__user = user

    def is_availalble_reserve(self):
        if self.__user.id:
            if not models.ReserveModel.exists_user_reserve(self.__user.id):
                return True
        return False
