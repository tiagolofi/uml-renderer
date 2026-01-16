
from uml import Board, Canvas

b = Board()

print(b.render())

c = Canvas(b.render())

c.render(output_file='output.png')

