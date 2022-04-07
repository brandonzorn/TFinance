class User:
    def __init__(self, user_data: dict):
        self.id: int = user_data.get('id')
        self.first_name: str = user_data.get('first_name')
        self.last_name: str = user_data.get('last_name')
        self.username: str = user_data.get('username')
        self.favourites_stocks = None
        self.points: int = 0
