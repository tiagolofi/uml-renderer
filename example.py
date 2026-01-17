
from uml import Board, Canvas
from web import UmlAppRenderer

b = Board()

c = Canvas(b.render())

c.render(output_file='output.png')

app = UmlAppRenderer()

app.run()

