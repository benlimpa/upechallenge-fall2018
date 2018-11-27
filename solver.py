import sys
import requests
from argparse import ArgumentParser
from navigator import MazeNavigator


def solve_maze(nav, verbose=False):
    if verbose:
        print('Solving Maze!')
    seen = set()
    path = []
    level = 0
    xmax, ymax = nav.size()
    while not nav.done():
        if nav.level(cached=True) > level:
            if verbose:
                print('Level {} Complete! Going on to Level {}'.format(
                    level, nav.level(cached=True)))
            seen = set()
            path = []
            xmax, ymax = nav.size()
            level = nav.level(cached=True)
        x, y = nav.pos(cached=True)
        seen.add((x, y))
        if verbose:
            print('Currently: {}, on Board {}, Level {}, Seen: {}'.format(
                (x, y), (xmax, ymax), level, seen))
        if x > 0 and (x - 1, y) not in seen:
            if verbose:
                print('Checking left!')
            if nav.left():
                path.append((x, y))
                continue
            seen.add((x - 1, y))  # Don't recheck walls
        if y > 0 and (x, y - 1) not in seen:
            if verbose:
                print('Checking up!')
            if nav.up():
                path.append((x, y))
                continue
            seen.add((x - 1, y))  # Don't recheck walls
        if x < xmax - 1 and (x + 1, y) not in seen:
            if verbose:
                print('Checking right!')
            if nav.right():
                path.append((x, y))
                continue
            seen.add((x - 1, y))  # Don't recheck walls
        if y < ymax - 1 and (x, y + 1) not in seen:
            if verbose:
                print('Checking down!')
            if nav.down():
                path.append((x, y))
                continue
            seen.add((x - 1, y))  # Don't recheck walls

        # back track
        prev = path.pop()
        if verbose:
            print('Back tracking to: {}'.format(prev))
        if x < prev[0]:
            nav.right()
        elif x > prev[0]:
            nav.left()
        elif y < prev[1]:
            nav.down()
        elif y > prev[1]:
            nav.up()


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('action', choices=('token', 'solve', 'status', 'sim'))
    parser.add_argument('--uid')
    parser.add_argument('--token')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    # get a token
    token = args.token
    if args.uid is not None:
        token_res = requests.post(
            'http://ec2-34-216-8-43.us-west-2.compute.amazonaws.com/session',
            data={'uid': args.uid})
        token = token_res.json()['token']
        print('Token: {}'.format(token))
        if args.action == 'token':
            sys.exit(0)

    if token is None:
        print('Specify a UID or a token')
        sys.exit(1)

    navigator = MazeNavigator(token)
    if args.action == 'status':
        navigator.update_info()
        print(navigator.info)
    if args.action == 'solve':
        solve_maze(navigator, args.verbose)
    elif args.action == 'sim':
        pass  # TODO simulate
