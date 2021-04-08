import asyncio

from parser import Parser

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    parser = Parser()
    loop.create_task(parser.run())
    loop.run_forever()
