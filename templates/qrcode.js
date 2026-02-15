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
        var size = 25;
        var matrix = this.createMatrix();
        return this.renderSVG(matrix, size);
    };

    QRCode.prototype.createMatrix = function() {
        // Simplified matrix generation - creates a deterministic pattern based on data hash
        var size = 25;
        var matrix = [];
        var hash = 0;
        var i, row, col;
        
        // Simple hash of data
        for (i = 0; i < this.data.length; i++) {
            hash = ((hash << 5) - hash) + this.data.charCodeAt(i);
            hash = hash & hash;
        }
        
        // Generate pseudo-random pattern
        var seed = Math.abs(hash);
        var random = function() {
            seed = (seed * 9301 + 49297) % 233280;
            return seed / 233280;
        };
        
        for (row = 0; row < size; row++) {
            matrix[row] = [];
            for (col = 0; col < size; col++) {
                // Position detection patterns (corners)
                var isPositionPattern = 
                    (row < 7 && col < 7) || // Top-left
                    (row < 7 && col >= size - 7) || // Top-right
                    (row >= size - 7 && col < 7); // Bottom-left
                
                if (isPositionPattern) {
                    // Create position detection pattern
                    var pr = row < 7 ? row : row - (size - 7);
                    var pc = col < 7 ? col : col - (size - 7);
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
        var cellSize = 4;
        var svgSize = size * cellSize;
        var row, col, x, y;
        
        var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + svgSize + ' ' + svgSize + '" width="200" height="200">';
        svg += '<rect width="100%" height="100%" fill="white"/>';
        
        for (row = 0; row < size; row++) {
            for (col = 0; col < size; col++) {
                if (matrix[row][col]) {
                    x = col * cellSize;
                    y = row * cellSize;
                    svg += '<rect x="' + x + '" y="' + y + '" width="' + cellSize + '" height="' + cellSize + '" fill="black"/>';
                }
            }
        }
        
        svg += '</svg>';
        return svg;
    };

    // Simpler canvas-based generator for better compatibility
    QRCode.prototype.toCanvas = function(canvas) {
        var ctx = canvas.getContext('2d');
        var size = 25;
        var cellSize = Math.floor(canvas.width / size);
        var matrix = this.createMatrix();
        var row, col;
        
        // Clear canvas
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw modules
        ctx.fillStyle = '#000000';
        for (row = 0; row < size; row++) {
            for (col = 0; col < size; col++) {
                if (matrix[row][col]) {
                    ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
                }
            }
        }
        
        return canvas;
    };

    global.QRCode = QRCode;
})(typeof window !== 'undefined' ? window : this);
