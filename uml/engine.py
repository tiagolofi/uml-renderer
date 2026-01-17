
import re
from typing import List
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

class FileReader():
    def __init__(self, filepath: str):
        self.filepath = filepath

    def read(self) -> str:
        with open(self.filepath, 'r') as file:
            return file.read()

class Action():
    def __init__(self, index: int, direction: str, to: str, text: str):
        self.index = index
        self.direction = direction
        self.to = to
        self.text = text

    def __repr__(self):
        return f'Action(index={self.index}, direction={self.direction}, to={self.to}, text={self.text})'
    
class Note():
    def __init__(self, index: int, content: str):
        self.index = index
        self.content = content

    def __repr__(self):
        return f'Note(index={self.index}, content={self.content})'
    
class Participant():
    def __init__(self, name: str):
        self.name = name
        self.events = []

    def add_event(self, event: Action|Note):
        self.events.append(event)

    def get_name(self) -> str:
        return self.name

    def get_events(self) -> List[Action|Note]:
        return self.events

    def get_event(self, index: int) -> Action|Note:
        return self.events[index]
    
    def __repr__(self):
        return f'Participant(name={self.name}, events={self.events})'

class Board():
    def __init__(self, reader: FileReader = FileReader('example.txt')):
        self.reader = reader
        self.participants = {}
        self.action_lines = []
        self.note_lines = []

    def render(self) -> List[Participant]:
        self.content = self.reader.read()
        participant_names = re.findall(r'participant\s+(\w+)', self.content)

        for name in participant_names:
            self.participants[name.strip()] = Participant(name.strip())

        for line_num, line in enumerate(self.content.splitlines(), start=1):
            self.action_lines.append((line_num, re.findall(r'(\w+)(->|<-)(\w+):(.+)', line)))
            self.note_lines.append((line_num, re.findall(r'note over (\w+):(.+)', line)))

        for i in self.action_lines:
            if not i[1]:
                continue
            sender, direction, receiver, text = i[1][0]
            action = Action(i[0], direction, receiver.strip(), text.strip())
            self.participants[sender.strip()].add_event(action)

        for i in self.note_lines:
            if not i[1]:
                continue
            participant_name, note_content = i[1][0]
            note = Note(i[0], note_content.strip())
            self.participants[participant_name.strip()].add_event(note)
    
        for participant in self.participants.values():
            participant.events.sort(key=lambda event: event.index)

        return self.participants
    
class Canvas():
    def __init__(self, participants: List[Participant], figsize: tuple = (12, 8), max_text_width: int = 30):
        self.figsize = figsize
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.participants = participants
        self.participant_positions = {}
        self.y_position = 0
        self.line_height = 0.5
        self.box_height = 0.4
        self.box_width = 1.5
        self.min_spacing = 2.5
        self.max_text_width = max_text_width
    
    def _wrap_text(self, text: str, max_width: int = None) -> List[str]:
        """Quebra o texto em múltiplas linhas se necessário"""
        if max_width is None:
            max_width = self.max_text_width
        
        lines = []
        words = text.split(' ')
        current_line = ''
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += (' ' if current_line else '') + word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines if lines else ['']

    def _calculate_positions(self):
        """Calcula as posições horizontais dos participantes"""
        num_participants = len(self.participants)
        max_text_width = max(len(name) * 0.08 for name in self.participants.keys())
        spacing = max(self.min_spacing, max_text_width + 1)
        
        total_width = num_participants * spacing
        start_x = -(total_width / 2) + (spacing / 2)
        
        for i, name in enumerate(self.participants.keys()):
            x = start_x + (i * spacing)
            self.participant_positions[name] = x

    def _draw_participant_boxes(self):
        """Desenha as caixas com nomes dos participantes no topo"""
        self.y_position = 10
        
        for name, x in self.participant_positions.items():
            box = FancyBboxPatch(
                (x - self.box_width/2, self.y_position - self.box_height/2),
                self.box_width, self.box_height,
                boxstyle="round,pad=0.01", 
                edgecolor='black', 
                facecolor='white',
                linewidth=1
            )
            self.ax.add_patch(box)
            self.ax.text(x, self.y_position, name, ha='center', va='center')
            
            # Desenha linha vertical para cada participante
            self.ax.plot([x, x], [self.y_position - self.box_height/2, 0], 'k--', linewidth=0.5, alpha=0.5)

    def _draw_actions_and_notes(self):
        """Desenha as ações e notas em ordem"""
        self.y_position -= 1.5
        
        # Coleta todos os eventos únicos de todos os participantes em ordem
        event_dict = {}
        for p_name, participant in self.participants.items():
            for event in participant.get_events():
                if event.index not in event_dict:
                    event_dict[event.index] = (p_name, event)
        
        # Ordena por índice
        event_list = sorted(event_dict.items(), key=lambda x: x[0])
        
        for _, (sender_name, event) in event_list:
            if isinstance(event, Action):
                self._draw_action(sender_name, event)
            elif isinstance(event, Note):
                self._draw_note(sender_name, event)
            
            self.y_position -= self.line_height

    def _draw_action(self, sender_name: str, action: Action):
        """Desenha uma seta de ação"""
        sender_x = self.participant_positions[sender_name]
        receiver_x = self.participant_positions[action.to]
        
        # Determina direção e estilo da seta
        if action.direction == '->':
            arrow_style = '->'
            start_x, end_x = sender_x, receiver_x
        else:  # '<-'
            arrow_style = '<-'
            start_x, end_x = receiver_x, sender_x
        
        # Desenha a seta
        arrow = FancyArrowPatch(
            (start_x, self.y_position),
            (end_x, self.y_position),
            arrowstyle=arrow_style,
            mutation_scale=10,
            linewidth=1,
            color='black'
        )
        self.ax.add_patch(arrow)
        
        # Quebra o texto em múltiplas linhas se necessário
        text_lines = self._wrap_text(action.text)
        mid_x = (start_x + end_x) / 2
        
        # Desenha cada linha de texto (primeira linha acima, subsequentes abaixo)
        base_y_offset = 0.15 + ((len(text_lines) - 1) * 0.1)
        for i, line in enumerate(text_lines):
            y_offset = base_y_offset - (i * 0.2)
            self.ax.text(mid_x, self.y_position + y_offset, line, 
                        ha='center', va='bottom', fontsize=8)
        
        # Ajusta a altura da linha se houver múltiplas linhas
        if len(text_lines) > 1:
            self.y_position -= (len(text_lines) - 1) * 0.1

    def _draw_note(self, participant_name: str, note: Note):
        """Desenha uma nota sobre um participante"""
        x = self.participant_positions[participant_name]
        
        # Quebra o texto em múltiplas linhas se necessário
        text_lines = self._wrap_text(note.content)
        
        # Desenha cada linha de texto com "note: " na primeira linha
        current_y = self.y_position + (len(text_lines) - 1) * 0.1
        for i, line in enumerate(text_lines):
            display_text = ("note: " + line) if i == 0 else line
            self.ax.text(x, current_y, display_text, 
                        ha='center', va='center', fontsize=8, style='italic')
            current_y -= 0.2
        
        # Ajusta a altura da linha se houver múltiplas linhas
        if len(text_lines) > 1:
            self.y_position -= (len(text_lines) - 1) * 0.1

    def render(self, output_file: str = None):
        """Renderiza o diagrama e salva como imagem"""
        self._calculate_positions()
        self._draw_participant_boxes()
        self._draw_actions_and_notes()
        
        # Configurações do gráfico
        self.ax.set_xlim(min(self.participant_positions.values()) - 2, 
                         max(self.participant_positions.values()) + 2)
        self.ax.set_ylim(self.y_position - 1, 11)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        
        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
        else:
            plt.show()
        
        return self.fig
