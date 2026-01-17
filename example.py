
from uml import Board, Canvas

b = Board()

c = Canvas(b.render())

c.render(output_file='output.png')

