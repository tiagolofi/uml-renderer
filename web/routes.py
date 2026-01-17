
from flask import Blueprint, render_template, request, jsonify, send_file
from uml import Board, Canvas, FileReader
from pathlib import Path

bp = Blueprint('main', __name__)

# Diretório para armazenar diagramas temporários
DIAGRAMS_DIR = Path(__file__).parent / 'temp'
DIAGRAMS_DIR.mkdir(exist_ok=True)

@bp.route('/')
def index():
    """Renderiza a página principal"""
    default_content = _load_default_diagram()
    return render_template('index.html', default_content=default_content)

@bp.route('/api/diagram', methods=['POST'])
def update_diagram():
    """Atualiza o diagrama baseado no conteúdo enviado"""
    try:
        content = request.json.get('content', '')
        
        if not content.strip():
            return jsonify({'error': 'Conteúdo vazio'}), 400
        
        # Salva o conteúdo em um arquivo temporário
        temp_file = DIAGRAMS_DIR / 'temp_diagram.txt'
        with open(temp_file, 'w') as f:
            f.write(content)
        
        # Renderiza o diagrama
        reader = FileReader(str(temp_file))
        board = Board(reader)
        participants = board.render()
        
        # Gera a imagem
        canvas = Canvas(participants, figsize=(12, 8))
        fig = canvas.render()
        
        # Salva a imagem em memória
        img_path = DIAGRAMS_DIR / 'diagram.png'
        fig.savefig(img_path, dpi=150, bbox_inches='tight')
        
        import matplotlib.pyplot as plt
        plt.close(fig)
        
        return jsonify({
            'success': True,
            'message': 'Diagrama atualizado com sucesso',
            'timestamp': _get_timestamp()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/api/diagram/image')
def get_diagram_image():
    """Retorna a imagem do diagrama"""
    try:
        img_path = DIAGRAMS_DIR / 'diagram.png'
        if not img_path.exists():
            # Gera um diagrama padrão se não existir
            _generate_default_diagram()
        
        return send_file(img_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/diagram/content')
def get_diagram_content():
    """Retorna o conteúdo atual do diagrama"""
    try:
        temp_file = DIAGRAMS_DIR / 'temp_diagram.txt'
        if temp_file.exists():
            with open(temp_file, 'r') as f:
                content = f.read()
            return jsonify({'content': content})
        else:
            return jsonify({'content': _load_default_diagram()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/diagram/reset', methods=['POST'])
def reset_diagram():
    """Reseta o diagrama para o padrão"""
    try:
        default_content = _load_default_diagram()
        temp_file = DIAGRAMS_DIR / 'temp_diagram.txt'
        with open(temp_file, 'w') as f:
            f.write(default_content)
        
        # Gera o diagrama padrão
        _generate_default_diagram()
        
        return jsonify({
            'success': True,
            'content': default_content,
            'message': 'Diagrama resetado com sucesso'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

def _load_default_diagram() -> str:
    """Carrega o conteúdo padrão do diagrama"""
    default_file = Path(__file__).parent.parent / 'example.txt'
    try:
        with open(default_file, 'r') as f:
            return f.read()
    except:
        return """participant Alice
participant Bob
participant Charlie

Alice->Bob: Olá Bob

note over Bob: Bob recebeu a mensagem

Bob->Charlie: Olá Charlie

note over Charlie: Charlie recebeu a mensagem

Charlie->Alice: Olá Alice"""

def _generate_default_diagram():
    """Gera um diagrama padrão"""
    content = _load_default_diagram()
    temp_file = DIAGRAMS_DIR / 'temp_diagram.txt'
    with open(temp_file, 'w') as f:
        f.write(content)
    
    reader = FileReader(str(temp_file))
    board = Board(reader)
    participants = board.render()
    canvas = Canvas(participants, figsize=(12, 8))
    fig = canvas.render()
    
    img_path = DIAGRAMS_DIR / 'diagram.png'
    fig.savefig(img_path, dpi=150, bbox_inches='tight')
    
    import matplotlib.pyplot as plt
    plt.close(fig)

def _get_timestamp() -> float:
    """Retorna o timestamp atual"""
    import time
    return time.time()