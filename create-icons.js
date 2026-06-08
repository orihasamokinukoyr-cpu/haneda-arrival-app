// アイコン画像をPNGとして生成するスクリプト
const { createCanvas } = require('canvas');
const fs = require('fs');

function createIcon(size) {
  const canvas = createCanvas(size, size);
  const ctx = canvas.getContext('2d');

  // 背景
  ctx.fillStyle = '#003087';
  ctx.fillRect(0, 0, size, size);

  // 飛行機マーク
  ctx.fillStyle = '#ffffff';
  ctx.font = `bold ${size * 0.5}px serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('🛬', size / 2, size / 2);

  return canvas.toBuffer('image/png');
}

try {
  fs.writeFileSync('./public/icon-192.png', createIcon(192));
  fs.writeFileSync('./public/icon-512.png', createIcon(512));
  console.log('アイコン生成完了');
} catch (e) {
  console.log('canvasモジュールなし、SVGアイコンを使用します');
}
