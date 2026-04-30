from argparse import BooleanOptionalAction
from common.args import parser

parser.add_argument('--operations-evaluation', action=BooleanOptionalAction)

parser.add_argument('--operations-skip', nargs='+', default=[],
                    help='Disable operations by tags or names')
