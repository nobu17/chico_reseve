
class ReserveCanNotSaveError(Exception):
    """When reserve can not save, this error happen (ex:already have or another user already have saved. etc)
    """
    pass


class NotExistsReserveError(Exception):
    """When not reserve target exists, this error is occured.
    """
    pass


class CancelFailedError(Exception):
    """When cancel is failed by unexpected, this errpr is occureed.
    """
    pass
