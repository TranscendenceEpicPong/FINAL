let animate = () => {};

function startGame()
{
	getSocket('game').send(JSON.stringify({"message":"hello"}))
}

const lines = [
	{
		startX: 20,
		startY: 100,
		endX: 20,
		endY: 250,
		color: 'green'
	},
	{
		startX: 580,
		startY: 100,
		endX: 580,
		endY: 250,
		color: 'green'
	}
]

function joinGame()
{
	chatsSockets['game'] = createSocket(getSocketURL('game'), gameDetails);
	chatsSockets['game'].onmessage = function(e) {
		const data = JSON.parse(e.data);
		if (['update_ball', 'game_end'].includes(data.status))
		{
			if (data.status === 'update_ball')
				animate(data.position.x, data.position.y);
			const score = data.score;
			if (score.player > 0 && score.player !== undefined && score.player !== null)
			{
				console.table({
					player_scored: score.player,
					player1: score.player1,
					player2: score.player2,
				});
				document.getElementById('username-player-1').innerText = score.player1.username;
				document.getElementById('score-player-1').innerText = score.player1.score;
				document.getElementById('username-player-2').innerText = score.player2.username;
				document.getElementById('score-player-2').innerText = score.player2.score;
			}
		}
		else if (data.status === 'update_padel')
		{
			lines[0] = data.player1;
			lines[1] = data.player2;
		}
	}
}

function gameDetails(e)
{
	const data = e.data;
	console.log('GAME DETAILS');
	// if (data.status)
	// 	alert(data)
}

const Status = {
	WAITING: 0,
	STARTED: 1,
	FINISHED: 2
};

document.addEventListener('DOMContentLoaded', () => {
	const canva = document.getElementById('canva-game');
	const ctx = canva.getContext('2d');

	function clearScreen()
	{
		ctx.clearRect(0, 0, canva.width, canva.height);
	}

	function getCircle(x, y, radius, color = 'blue')
	{
		ctx.beginPath();
		ctx.arc(x, y, radius, 0, Math.PI * 2);
		ctx.fillStyle = color;
		ctx.fill();
	}

	const LINE_WIDTH = 20;

	function getLine(startX, startY, endX, endY, color = 'green')
	{
		ctx.beginPath();
		ctx.moveTo(startX, startY);
		ctx.lineTo(endX, endY);
		ctx.strokeStyle = color;
		ctx.lineWidth = LINE_WIDTH;
		ctx.stroke();
	}

	ctx.beginPath();
	ctx.moveTo(580, 100);
	ctx.lineTo(580, 250);
	ctx.strokeStyle = 'green';
	ctx.lineWidth = 20;
	ctx.stroke();

	let is_end = false;

	function _animate(x, y)
	{
		if (is_end)
			return;
		clearScreen();
		getCircle(x, y, 15);
		for (const line of lines)
			getLine(line.startX, line.startY, line.endX, line.endY, line.color);
	}

	window.addEventListener('keydown', (e) => {
		const index = ['ArrowUp', 'ArrowDown', 'w', 's'].indexOf(e.key);
		console.log('keydown');
		if (index !== -1)
			getSocket('game').send(JSON.stringify({action: 'move', direction: e.key}));
	});

	animate = _animate;

	animate(200, 200);
});