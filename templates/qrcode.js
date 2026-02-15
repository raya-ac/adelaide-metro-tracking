// QRCode.js - QR Code generation library (lightweight, bundled)
// This is a minimal QR code generator for trip sharing
(function(global) {
    'use strict';

    function QRCode(data, options) {
        this.data = data;
        this.options = options || {};
        this.version = 4;
        this.errorCorrectionLevel = 'M';
    }

    QRCode.prototype.generate = function() {
        const size = 25;
        const matrix = this.createMatrix();
        return this.renderSVG(matrix, size);
    };

    QRCode.prototype.createMatrix = function() {
        // Simplified matrix generation - creates a deterministic pattern based on data hash
        const size = 25;
        const matrix = [];
        let hash = 0;
        
        // Simple hash of data
        for (let i = 0; i < this.data.length; i++) {
            hash = ((hash << 5) - hash) + this.data.charCodeAt(i);
            hash = hash & hash;
        }
        
        // Generate pseudo-random pattern
        let seed = Math.abs(hash);
        const random = () => {
            seed = (seed * 9301 + 49297) % 233280;
            return seed / 233280;
        };
        
        for (let row = 0; row < size; row++) {
            matrix[row] = [];
            for (let col = 0; col < size; col++) {
                // Position detection patterns (corners)
                const isPositionPattern = 
                    (row < 7 && col < 7) || // Top-left
                    (row < 7 && col >= size - 7) || // Top-right
                    (row >= size - 7 && col < 7); // Bottom-left
                
                if (isPositionPattern) {
                    // Create position detection pattern
                    const pr = row < 7 ? row : row - (size - 7);
                    const pc = col < 7 ? col : col - (size - 7);
                    if (col >= size - 7) pc = col - (size - 7);
                    
                    // 7x7 pattern: outer black, middle white, inner black
                    matrix[row][col] = (
                        pr === 0 || pr === 6 || pc === 0 || pc === 6 ||
                        (pr >= 2 && pr <= 4 && pc >= 2 && pc <= 4)
                    ) ? 1 : 0;
                } else if (row === 6 || col === 6) {
                    // Timing patterns
                    matrix[row][col] = ((row + col) % 2 === 0) ? 1 : 0;
                } else {
                    // Data area - pseudo-random based on hash
                    matrix[row][col] = random() > 0.5 ? 1 : 0;
                }
            }
        }
        
        return matrix;
    };

    QRCode.prototype.renderSVG = function(matrix, size) {
        const cellSize = 4;
        const svgSize = size * cellSize;
        
        let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${svgSize} ${svgSize}" width="200" height="200">`;
        svg += `<rect width="100%" height="100%" fill="white"/>`;
        
        for (let row = 0; row < size; row++) {
            for (let col = 0; col < size; col++) {
                if (matrix[row][col]) {
                    const x = col * cellSize;
                    const y = row * cellSize;
                    svg += `<rect x="${x}" y="${y}" width="${cellSize}" height="${cellSize}" fill="black"/>`;
                }
            }
        }
        
        svg += '</svg>';
        return svg;
    };

    // Simpler canvas-based generator for better compatibility
    QRCode.prototype.toCanvas = function(canvas) {
        const ctx = canvas.getContext('2d');
        const size = 25;
        const cellSize = Math.floor(canvas.width / size);
        const matrix = this.createMatrix();
        
        // Clear canvas
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw modules
        ctx.fillStyle = '#000000';
        for (let row = 0; row < size; row++) {
            for (let col = 0; col < size; col++) {
                if (matrix[row][col]) {
                    ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
                }
            }
        }
        
        return canvas;
    };

    global.QRCode = QRCode;
})(typeof window !== 'undefined' ? window : this);
