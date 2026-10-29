import './style.css';
const API = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/$/, '');
const app = document.querySelector('#app');
app.innerHTML = `<main class="shell"><div class="eyebrow">AI MINI-CAPSTONE · ADVERSARIAL SEARCH</div><h1>Big Tic-Tac-Toe</h1><p class="subtitle">Play on a larger board against a Minimax opponent.</p><section class="toolbar"><label>BOARD<select id="size"><option>4</option><option selected>5</option><option>6</option><option>7</option></select></label><label>WIN LENGTH<select id="target"><option>3</option><option selected>4</option><option>5</option><option>6</option><option>7</option></select></label><label>AI DEPTH<select id="level"><option>Easy</option><option selected>Medium</option><option>Hard</option></select></label><button id="restart">New Game</button></section><p id="status" role="status" aria-live="polite"></p><div class="board-wrap"><div id="board" role="grid" aria-label="Tic-Tac-Toe board"></div></div><div class="stats"><span id="nodes">Positions searched: 0</span><span id="cuts">Pruned branches: 0</span></div><p class="foot">You: <strong class="x">X</strong> · AI: <strong class="o">O</strong> · Larger boards use heuristic, depth-limited search.</p></main>`;
const $ = id => document.getElementById(id);
let n, k, board, busy, finished, winning = [], generation = 0;
function lines() {
  const result = [];
  for (let r=0;r<n;r++) for(let c=0;c<n;c++) for(const [dr,dc] of [[0,1],[1,0],[1,1],[1,-1]]) {
    if(r+(k-1)*dr>=0 && r+(k-1)*dr<n && c+(k-1)*dc>=0 && c+(k-1)*dc<n)
      result.push(Array.from({length:k},(_,t)=>(r+t*dr)*n+c+t*dc));
  }
  return result;
}
function outcome() {
  for(const line of lines()) if(board[line[0]] && line.every(i=>board[i]===board[line[0]])) return {winner:board[line[0]],line};
  return {winner:null,line:[],draw:board.every(Boolean)};
}
function draw(last=-1) {
  $('board').style.setProperty('--n', n);
  $('board').replaceChildren(...board.map((mark,i)=>{
    const b=document.createElement('button'); b.className='cell'+(winning.includes(i)?' win':'')+(i===last?' pop':'');
    b.textContent=mark; b.dataset.mark=mark; b.setAttribute('role','gridcell');
    b.setAttribute('aria-label',`Row ${Math.floor(i/n)+1}, column ${i%n+1}: ${mark||'empty'}`);
    b.disabled=busy||finished||!!mark; b.onclick=()=>humanMove(i); return b;
  }));
}
function finish() {
  const state=outcome();
  if(state.winner || state.draw) {
    finished=true; winning=state.line;
    $('status').textContent=state.winner==='X'?'You win! 🎉':state.winner==='O'?'AI wins this round.':"It's a draw!";
    draw(); return true;
  }
  return false;
}
async function humanMove(i) {
  if(busy||finished||board[i]) return;
  board[i]='X'; busy=true; draw(i);
  if(finish()) return;
  $('status').textContent='AI is thinking…';
  const token=generation;
  try {
    const response=await fetch(`${API}/api/move`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({board,n,k,level:$('level').value})});
    const data=await response.json();
    if(!response.ok) throw new Error(data.error||`Server error ${response.status}`);
    if(token!==generation) return;
    board=data.board; busy=false;
    $('nodes').textContent=`Positions searched: ${data.nodes.toLocaleString()}`;
    $('cuts').textContent=`Pruned branches: ${data.cuts.toLocaleString()}`;
    if(!finish()) {$('status').textContent='Your turn.';draw(data.move);}
  } catch(error) {
    if(token!==generation) return;
    board[i]='';busy=false;
    $('status').textContent=`Connection error: ${error.message}. Check the Render backend URL and try again.`;
    draw();
  }
}
function newGame() {
  generation++; n=Number($('size').value); k=Math.min(n,Number($('target').value));
  $('target').value=String(k); board=Array(n*n).fill(''); busy=false;finished=false;winning=[];
  $('status').textContent=`Get ${k} in a row to win. Your turn.`;
  $('nodes').textContent='Positions searched: 0';$('cuts').textContent='Pruned branches: 0';draw();
}
$('restart').onclick=newGame;
$('size').onchange=()=>{const target=$('target'); for(const option of target.options) option.disabled=Number(option.value)>Number($('size').value);newGame();};
$('target').onchange=newGame;
$('level').onchange=newGame;
newGame();
