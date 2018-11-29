import sys
import requests
import numpy as np
import json
from argparse import ArgumentParser
from navigator import MazeNavigator, SimNavigator


def print_map(level_map):
    print('-' * (level_map.shape[1] + 2))
    for row in level_map:
        print('|', end='')
        for let in row:
            print(let, end='')
        print('|')
    print('-' * (level_map.shape[1] + 2))


def replay_path(nav, path, level):
    for point in path:
        if nav.level() != level:
            return
        x, y = nav.pos(cached=True)
        if x < point[0]:
            nav.right()
        elif x > point[0]:
            nav.left()
        elif y < point[1]:
            nav.down()
        elif y > point[1]:
            nav.up()


def solve_maze(nav, verbose=False, visual=False):
    if verbose:
        print('Solving Maze!')

    # initialize level params
    xmax, ymax = nav.size()
    level = nav.level(cached=True)
    old_level = level
    level_maps = [None for _ in range(nav.levels(cached=True))]
    solutions = [None for _ in range(nav.levels(cached=True))]
    level_map = np.full((ymax, xmax), ' ')
    path = []

    x, y = nav.pos(cached=True)
    done = False
    while not done:
        if old_level != level:
            # moved on to the next level
            if verbose:
                print('Level {} Complete! Going on to Level {}'.format(
                    old_level, level))

            # Save solved level
            level_maps[old_level] = level_map
            solutions[old_level] = path

            # get new level info
            xmax, ymax = nav.size()
            if xmax is None:
                # Maze finished
                break
            x, y = nav.pos(cached=True)

            level_map = np.full((ymax, xmax), ' ')
            path = []
            old_level = level

        # mark as seen
        level_map[y, x] = '.'

        if visual:
            print_map(level_map)
            print('Current Pos: {}, on Board Size {}, Level {}'.format(
                (x, y), (xmax, ymax), level))
        if verbose:
            print('Currently: {}, on Board Size {}, Level {}'.format(
                (x, y), (xmax, ymax), level))

        if x > 0 and level_map[y, x - 1] == ' ':
            if verbose:
                print('Checking left!')
            result = nav.left()
            if result == 'END':
                level += 1
                continue
            elif result == 'SUCCESS':
                path.append((x, y))
                x -= 1
                continue
            elif result == 'EXPIRED':
                done = True
                continue
            else:
                # Found a wall
                level_map[y, x - 1] = '*'
        if y > 0 and level_map[y - 1, x] == ' ':
            if verbose:
                print('Checking up!')
            result = nav.up()
            if result == 'END':
                level += 1
                continue
            elif result == 'SUCCESS':
                path.append((x, y))
                y -= 1
                continue
            elif result == 'EXPIRED':
                done = True
                continue
            else:
                # Found a wall
                level_map[y - 1, x] = '*'
        if x < xmax - 1 and level_map[y, x + 1] == ' ':
            if verbose:
                print('Checking right!')
            result = nav.right()
            if result == 'END':
                level += 1
                continue
            elif result == 'SUCCESS':
                path.append((x, y))
                x += 1
                continue
            elif result == 'EXPIRED':
                done = True
                continue
            else:
                # Found a wall
                level_map[y, x + 1] = '*'
        if y < ymax - 1 and level_map[y + 1, x] == ' ':
            if verbose:
                print('Checking down!')
            result = nav.down()
            if result == 'END':
                level += 1
                continue
            elif result == 'SUCCESS':
                path.append((x, y))
                y += 1
                continue
            elif result == 'EXPIRED':
                done = True
                continue
            else:
                # Found a wall
                level_map[y + 1, x] = '*'

        # If there is no where to go, back track
        prev = path.pop()
        if verbose:
            print('Back tracking to: {}'.format(prev))
        if x < prev[0]:
            if nav.right() == 'EXPIRED':
                done = True
            else:
                x += 1
        elif x > prev[0]:
            if nav.left() == 'EXPIRED':
                done = True
            else:
                x -= 1
        elif y < prev[1]:
            if nav.down() == 'EXPIRED':
                done = True
            else:
                y += 1
        elif y > prev[1]:
            if nav.up() == 'EXPIRED':
                done = True
            else:
                y -= 1

    return (level_maps, solutions)


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('action', choices=('token', 'solve', 'status', 'sim'))
    parser.add_argument(
        '--uid',
        help='UID to retrieve a new token; mutually exclusive with "--token"')
    parser.add_argument(
        '--token',
        help='token to use while playing; mutually exclusive with "--uid"')
    parser.add_argument(
        '--sol-save-to',
        default='solutions.json',
        help='file to save solutions to')
    parser.add_argument(
        '--level-save-to',
        default='levels.json',
        help='file to save solutions to')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='print debugging info while running')
    parser.add_argument(
        '--visual',
        action='store_true',
        help='show a live-updating map of the level')
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
        levels, solutions = solve_maze(navigator, args.verbose, args.visual)
        with open(args.level_save_to, 'w') as f:
            i = 0
            for l in levels:
                if l is not None:
                    levels[i] = l.tolist()
                i += 1
            json.dump(levels, f)
        with open(args.sol_save_to, 'w') as f:
            json.dump(solutions, f)
    elif args.action == 'sim':
        solve_maze(SimNavigator(), args.verbose, args.visual)
