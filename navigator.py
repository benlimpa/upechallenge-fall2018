import requests


class MazeNavigator:
    def __init__(self, token):
        self.token = token

    def update_info(self):
        print('Getting info...')
        self.info = requests.get(
            'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game',
            params={
                'token': self.token
            }).json()

    def info_item(self, item, cached=False):
        if cached:
            return self.info[item]
        else:
            self.update_info()
            return self.info_item(item, cached=True)

    def size(self, cached=False):
        return self.info_item('maze_size', cached=cached)

    def pos(self, cached=False):
        return self.info_item('current_location', cached=cached)

    def level(self, cached=False):
        return self.info_item('levels_completed', cached=cached)

    def done(self, cached=False):
        status = self.info_item('status', cached=cached)
        if status != 'PLAYING':
            return True
        else:
            return False

    def move(self, direction):
        result = requests.post(
            'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game',
            params={
                'token': self.token
            },
            data={
                'action': direction
            }).json()['result']
        if result == 'SUCCESS' or result == 'END':
            return True
        else:
            return False

    def up(self):
        return self.move('UP')

    def down(self):
        return self.move('DOWN')

    def left(self):
        return self.move('LEFT')

    def right(self):
        return self.move('RIGHT')


class MazeSimulator:
    MAZE = [
        "S**  *   ", "  * *  * ", " ** ** * ", "     *E* ", " *** *** ",
        "*      * ", "  **** * ", " *   *** ", "   *     "
    ]

    def get_info(self):
        return {
            'maze_size': [len(self.MAZE[0]), len(self.MAZE)],
            'current_location': [0, 0],
            'status': 'PLAYING'
        }
