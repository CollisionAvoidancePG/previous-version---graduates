from common.args import parser

parser.add_argument('--cache-disable', action='store_true',
                    help='Disable using cached data')

parser.add_argument('--cache-clear', action='store_true',
                    help='Clear all cached data')
