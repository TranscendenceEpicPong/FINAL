import { loadPage } from "../router.js";
import {getData, setData} from "../store.js";
import {
	getSocket,
	initializeSocket,
	resetSocket,
	sendToSocket,
} from "./socket.js";

const ActionStatus = {
	CREATED: "created",
	JOINED: "joined",
	STARTED: "started",
	FINISHED: "finished",
};

const Status = {
	WAITING: 0,
	STARTED: 1,
	FINISHED: 2,
};

const Config = {
	CANVAS: {
		WIDTH: 800,
		HEIGHT: 400,
	},
	PADDLE: {
		WIDTH: 10,
		HEIGHT: 100,
		COLOR: "#131316",
	},
	BALL: {
		RADIUS: 5,
		COLOR: "#131316",
	},
};

Config["X"] = {
	PLAYER_1: 0,
	PLAYER_2: Config.CANVAS.WIDTH - Config.PADDLE.WIDTH,
};

const game = {
	is_started: false,
	context: null,
	canvas: null,
	screen: {
		width: Config.CANVAS.WIDTH,
		height: Config.CANVAS.HEIGHT,
	},
	ball: {
		x: Config.CANVAS.WIDTH / 2,
		y: Config.CANVAS.HEIGHT / 2,
	},
	player1: {
		id: 0,
		username: "",
		x: 0,
		y: Config.CANVAS.HEIGHT / 2,
		score: 0,
	},
	player2: {
		id: 0,
		username: "",
		x: Config.CANVAS.WIDTH - Config.PADDLE.WIDTH,
		y: Config.CANVAS.HEIGHT / 2,
		score: 0,
	},
	keys: {
		up: false,
		down: false,
	},
};

function initializeInput() {
	window.addEventListener("keydown", (event) => {
		if (["w", "arrowup"].includes(event.key.toLocaleLowerCase())) {
			game.keys.up = true;
		} else if (["s", "arrowdown"].includes(event.key.toLocaleLowerCase())) {
			game.keys.down = true;
		}
	});

	window.addEventListener("keyup", (event) => {
		console.log(event);
		if (["w", "arrowup"].includes(event.key.toLocaleLowerCase())) {
			game.keys.up = false;
		} else if (["s", "arrowdown"].includes(event.key.toLocaleLowerCase())) {
			game.keys.down = false;
		}
	});

	game.canvas.addEventListener("touchstart", handleTouchStart, false);
	game.canvas.addEventListener("touchmove", handleTouchMove, false);
	game.canvas.addEventListener("touchend", handleTouchEnd, false);
}

let lastTouchX = null;
const touchSensitivity = 5;

function handleTouchStart(event) {
	event.preventDefault();
	const touch = event.touches[0];
	lastTouchX = touch.clientX;
}

function handleTouchMove(event) {
	if (lastTouchX !== null) {
		event.preventDefault();
		const touch = event.touches[0];
		const deltaX = touch.clientX - lastTouchX;

		if (Math.abs(deltaX) > touchSensitivity) {
			if (deltaX > 0) {
				movePlayer("up");
			} else {
				movePlayer("down");
			}
			lastTouchX = touch.clientX;
		}
	}
}

function handleTouchEnd(event) {
	event.preventDefault();
	lastTouchX = null;
	game.keys.up = false;
	game.keys.down = false;
}

function update() {
	if (game.keys.up) {
		movePlayer("up");
	} else if (game.keys.down) {
		movePlayer("down");
	}
}

export function render(game_infos) {
	if (game_infos) {
		game.ball = game_infos.ball;
		game.player1 = game_infos.player1;
		game.player2 = game_infos.player2;
	}
	drawRect(0, 0, game.canvas.width, game.canvas.height, "#DC3545"); // Left side
	drawRect(
		game.canvas.width / 2,
		0,
		game.canvas.width / 2,
		game.canvas.height,
		"#3567DC"
	); // Right side
	drawText(
		`${game.player1.score}`,
		game.canvas.width / 4.7,
		game.canvas.height / 1.7,
		"white"
	);
	drawText(
		`${game.player2.score}`,
		(3 * game.canvas.width) / 4.2,
		game.canvas.height / 1.7,
		"white"
	);

	// check if you are player one or player two, then add "You" with drawSmallText under the score
	if (getData("auth.user.id") === game.player1.id) {
		drawSmallText(
			"You",
			game.canvas.width / 4.7,
			game.canvas.height / 1.5,
			"white"
		);
	} else if (getData("auth.user.id") === game.player2.id) {
		drawSmallText(
			"You",
			(3 * game.canvas.width) / 4.2,
			game.canvas.height / 1.5,
			"white"
		);
	}

	drawLine(
		game.player1.x,
		game.player1.y - Config.PADDLE.HEIGHT / 2,
		game.player1.x,
		game.player1.y + Config.PADDLE.HEIGHT / 2,
		Config.PADDLE.COLOR
	);
	drawLine(
		game.player2.x,
		game.player2.y - Config.PADDLE.HEIGHT / 2,
		game.player2.x,
		game.player2.y + Config.PADDLE.HEIGHT / 2,
		Config.PADDLE.COLOR
	);
	drawCircle(game.ball.x, game.ball.y, Config.BALL.RADIUS, Config.BALL.COLOR);
}

function movePlayer(direction) {
	console.log("move", direction);
	if (game.is_started)
		sendToSocket({ action: "move", direction: direction }, "game");
}

export function analyzeGameRequest(data) {
	const startBtn = document.getElementById("btn-start-game");
	const pongCanvas = document.getElementById("gamewindow");
	const gameInfo = document.getElementById("game-info");
	if (getData('route.path') !== '/games/multiplayer' && data.type !== "error")
		loadPage('/games/multiplayer');
	if (!gameInfo) return;
	setData({game: {waiting: false}}, {reload: false});
	if (data.type === "error") return showToast(data.message);
	if (data.action === ActionStatus.CREATED) {
		// startBtn change text to Partie créée and add disabled
		startBtn.textContent = "Partie créée";
		startBtn.disabled = true;
		return;
	}
	if (data.game.status === Status.WAITING) {
		// En attente de joueurs
		startBtn.textContent = "En attente de joueurs";
		startBtn.disabled = true;
		return;
	} else if (data.game.status === Status.STARTED) {
			// gameInfo hide
			gameInfo.classList.add("d-none");
			// pong canvas show
			pongCanvas.classList.remove("d-none");
		return initializePong(data.game);
	} else if (data.game.status === Status.FINISHED) {
		// pong canvas hide
		pongCanvas.classList.add("d-none");
		// gameInfo show
		gameInfo.classList.remove("d-none");
		game.is_started = false;
		startBtn.textContent = "Rejoindre / créer";
		startBtn.disabled = false;
		render(data.game);
		clearInterval(game.interval);
		return showToast(
			`Partie terminée ${
				getData("auth.user.id") == data.game.winner
					? "vous avez gagné"
					: "vous avez perdu"
			}`
		);
	}
}

export function initializePong(game_infos) {
	/* your_color.style.backgroundColor =
		game_infos.player1.id === getData("auth.user.id")
			? "#DC3545"
			: "#3567DC";
	your_color.parentElement.classList.remove("d-none"); */

	configureCanvas();
	configureContext();
	getScreenInfos();
	if (game.is_started === false) {
		game.is_started = true;
		initializeInput();
		game.interval = setInterval(() => {
			update();
		}, 1000 / 100);
	}
	game.is_started = true;
	render(game_infos);
}

function configureCanvas() {
	game.canvas = document.getElementById("canva-pong");
	game.canvas.width = Config.CANVAS.WIDTH;
	game.canvas.height = Config.CANVAS.HEIGHT;
}

function configureContext() {
	game.context = game.canvas.getContext("2d");
	game.context.clearRect(0, 0, Config.CANVAS.WIDTH, Config.CANVAS.HEIGHT);
}

function getScreenInfos() {
	game.screen.width =
		window.innerWidth >= Config.CANVAS.WIDTH
			? Config.CANVAS.WIDTH
			: Config.CANVAS.HEIGHT;
	game.screen.height =
		window.innerHeight >= Config.CANVAS.HEIGHT
			? Config.CANVAS.HEIGHT
			: Config.CANVAS.WIDTH;
}

function drawCircle(x, y, radius, color = "blue") {
	game.context.beginPath();
	game.context.arc(x, y, radius, 0, Math.PI * 2);
	game.context.fillStyle = color;
	game.context.fill();
}

const LINE_WIDTH = 10;

function drawRect(x, y, w, h, color) {
	game.context.fillStyle = color;
	game.context.fillRect(x, y, w, h);
}

function drawLine(startX, startY, endX, endY, color = "green") {
	game.context.beginPath();
	game.context.moveTo(startX, startY);
	game.context.lineTo(endX, endY);
	game.context.strokeStyle = color;
	game.context.lineWidth = LINE_WIDTH;
	game.context.stroke();
}

function drawText(text, x, y, color) {
	game.context.fillStyle = color;
	game.context.font = "108px Arial";
	game.context.fillText(text, x, y);
}

function drawSmallText(text, x, y, color) {
	game.context.fillStyle = color;
	game.context.font = "30px Arial";
	game.context.fillText(text, x, y);
}
