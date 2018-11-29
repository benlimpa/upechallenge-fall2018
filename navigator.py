import requests


class MazeNavigator:
    def __init__(self, token):
        self.token = token

    def update_info(self):
        # print('Getting info...')
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

    def levels(self, cached=False):
        return self.info_item('total_levels', cached=cached)

    def done(self, cached=False):
        status = self.info_item('status', cached=cached)
        if status != 'PLAYING':
            return True
        else:
            return False

    def move(self, direction):
        return requests.post(
            'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/game',
            params={
                'token': self.token
            },
            data={
                'action': direction
            }).json()['result']

    def up(self):
        return self.move('UP')

    def down(self):
        return self.move('DOWN')

    def left(self):
        return self.move('LEFT')

    def right(self):
        return self.move('RIGHT')


class SimNavigator:
    MAZE = [
        "S**  *   ", "  * *  * ", " ** ** * ", "     *E* ", " *** *** ",
        "*      * ", "  **** * ", " *   *** ", "   *     "
    ]

    def __init__(self):
        self.pos_stat = [0, 0]
        self.done_stat = False

    def size(self, cached=False):
        return [9, 9]

    def pos(self, cached=False):
        return self.pos_stat

    def level(self, cached=False):
        return 0

    def done(self, cached=False):
        return self.done_stat

    def up(self):
        self.pos_stat[1] -= 1
        if self.MAZE[self.pos_stat[1]][self.pos_stat[0]] == 'E':
            self.done_stat = True
        return self.MAZE[self.pos_stat[1]][self.pos_stat[0]] != '*'

    def down(self):
        self.pos_stat[1] += 1
        if self.MAZE[self.pos_stat[1]][self.pos_stat[0]] == 'E':
            self.done_stat = True
        return self.MAZE[self.pos_stat[1]][self.pos_stat[0]] != '*'

    def left(self):
        self.pos_stat[0] -= 1
        if self.MAZE[self.pos_stat[1]][self.pos_stat[0]] == 'E':
            self.done_stat = True
        return self.MAZE[self.pos_stat[1]][self.pos_stat[0]] != '*'

    def right(self):
        self.pos_stat[0] += 1
        if self.MAZE[self.pos_stat[1]][self.pos_stat[0]] == 'E':
            self.done_stat = True
        return self.MAZE[self.pos_stat[1]][self.pos_stat[0]] != '*'
