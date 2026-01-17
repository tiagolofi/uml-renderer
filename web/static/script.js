class DiagramEditor {
    constructor() {
        this.editor = document.getElementById('diagram-editor');
        this.updateBtn = document.getElementById('update-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.statusDiv = document.getElementById('status');
        this.diagramImage = document.getElementById('diagram-image');
        this.autoUpdateToggle = document.getElementById('auto-update-toggle');
        
        this.autoUpdateInterval = null;
        this.autoUpdateDelay = 5000; // 5 segundos
        
        this.init();
    }
    
    init() {
        this.updateBtn.addEventListener('click', () => this.updateDiagram());
        this.resetBtn.addEventListener('click', () => this.resetDiagram());
        this.autoUpdateToggle.addEventListener('change', () => this.toggleAutoUpdate());
        
        // Inicia auto-update se checkbox estiver marcado
        if (this.autoUpdateToggle.checked) {
            this.startAutoUpdate();
        }
    }
    
    async updateDiagram() {
        const content = this.editor.value;
        
        if (!content.trim()) {
            this.showStatus('Diagrama vazio', 'error');
            return;
        }
        
        this.updateBtn.disabled = true;
        this.showStatus('Atualizando...', 'info');
        
        try {
            const response = await fetch('/api/diagram', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Erro ao atualizar diagrama');
            }
            
            // Atualiza a imagem
            await this.refreshImage();
            this.showStatus('✓ Diagrama atualizado com sucesso!', 'success');
            
        } catch (error) {
            this.showStatus(`✗ ${error.message}`, 'error');
        } finally {
            this.updateBtn.disabled = false;
        }
    }
    
    async refreshImage() {
        const timestamp = Date.now();
        this.diagramImage.src = `/api/diagram/image?t=${timestamp}`;
    }
    
    async resetDiagram() {
        this.resetBtn.disabled = true;
        this.showStatus('Resetando...', 'info');
        
        try {
            const response = await fetch('/api/diagram/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Erro ao resetar diagrama');
            }
            
            const data = await response.json();
            this.editor.value = data.content;
            
            // Atualiza a imagem
            await this.refreshImage();
            this.showStatus('✓ Diagrama resetado com sucesso!', 'success');
        } catch (error) {
            this.showStatus(`✗ ${error.message}`, 'error');
        } finally {
            this.resetBtn.disabled = false;
        }
    }
    
    toggleAutoUpdate() {
        if (this.autoUpdateToggle.checked) {
            this.startAutoUpdate();
        } else {
            this.stopAutoUpdate();
        }
    }
    
    startAutoUpdate() {
        if (this.autoUpdateInterval) {
            return;
        }
        
        this.autoUpdateInterval = setInterval(() => {
            this.updateDiagram();
        }, this.autoUpdateDelay);
    }
    
    stopAutoUpdate() {
        if (this.autoUpdateInterval) {
            clearInterval(this.autoUpdateInterval);
            this.autoUpdateInterval = null;
        }
    }
    
    showStatus(message, type) {
        this.statusDiv.textContent = message;
        this.statusDiv.className = `status-message ${type}`;
    }
}

// Inicializa quando o DOM está pronto
document.addEventListener('DOMContentLoaded', () => {
    new DiagramEditor();
});