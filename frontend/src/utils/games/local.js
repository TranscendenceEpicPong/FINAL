let speedIncrease = 1;
let winningScore = 1;
let gameInterval;

function setNumsWins(numwins) {
	console.log("numwins: ");
	console.log(numwins);
	winningScore = numwins;
}

function setBallspeed(ballspeed) {
	console.log("ballspeed: ");
	console.log(ballspeed);
	speedIncrease = ballspeed;
}

export function initializePong(canvas, ctx, numwins, ballspeed) {
	canvas.width = 800;
	canvas.height = 400;

	setNumsWins(numwins);
	setBallspeed(ballspeed);

	// get screen width
	let screenWidth = window.innerWidth;
	// get screen height
	let screenHeight = window.innerHeight;

	if (screenWidth < 800) {
		console.log("screenWidth: ", screenWidth);
		canvas.width = screenHeight;
	}

	if (screenHeight < 400) {
		console.log("screenHeight: ", screenHeight);
		canvas.height = screenHeight;
	}

	const ball = {
		x: canvas.width / 2,
		y: canvas.height / 2,
		radius: 10,
		velocityX: 5,
		velocityY: 5,
		speed: 7,
		color: "#131316",
	};

	const user = {
		x: 0,
		y: (canvas.height - 100) / 2,
		width: 10,
		height: 100,
		score: 0,
		color: "#131316",
		upPressed: false,
		downPressed: false,
	};

	const player2 = {
		x: canvas.width - 10,
		y: (canvas.height - 100) / 2,
		width: 10,
		height: 100,
		score: 0,
		color: "#131316",
		upPressed: false,
		downPressed: false,
	};

	function drawRect(x, y, w, h, color) {
		ctx.fillStyle = color;
		ctx.fillRect(x, y, w, h);
	}

	function drawArc(x, y, r, color) {
		ctx.fillStyle = color;
		ctx.beginPath();
		ctx.arc(x, y, r, 0, Math.PI * 2, true);
		ctx.closePath();
		ctx.fill();
	}

	document.addEventListener("keydown", (event) => {
		if (event.key === "W" || event.key === "w") {
			user.upPressed = true;
		} else if (event.key === "S" || event.key === "s") {
			user.downPressed = true;
		}
		if (event.key === "ArrowUp") {
			player2.upPressed = true;
		} else if (event.key === "ArrowDown") {
			player2.downPressed = true;
		}
	});

	document.addEventListener("keyup", (event) => {
		if (event.key === "W" || event.key === "w") {
			user.upPressed = false;
		} else if (event.key === "S" || event.key === "s") {
			user.downPressed = false;
		}
		if (event.key === "ArrowUp") {
			player2.upPressed = false;
		} else if (event.key === "ArrowDown") {
			player2.downPressed = false;
		}
	});

	function resetBall() {
		// Temporarily stop the ball's movement
		ball.velocityX = 0;
		ball.velocityY = 0;

		// Set the ball at the center of the canvas
		ball.x = canvas.width / 2;
		ball.y = canvas.height / 2;

		// Wait for a moment before restarting the ball's movement
		setTimeout(() => {
			ball.velocityX = 5 * (Math.random() > 0.5 ? 1 : -1);
			ball.velocityY = 5 * (Math.random() > 0.5 ? 1 : -1);
			ball.speed = 7;
		}, 1000);
	}

	function update() {
		if (user.upPressed && user.y > 0) {
			user.y -= 8;
		} else if (user.downPressed && user.y < canvas.height - user.height) {
			user.y += 8;
		}

		if (player2.upPressed && player2.y > 0) {
			player2.y -= 8;
		} else if (
			player2.downPressed &&
			player2.y < canvas.height - player2.height
		) {
			player2.y += 8;
		}

		ball.x += ball.velocityX;
		ball.y += ball.velocityY;

		if (ball.y + ball.radius > canvas.height || ball.y - ball.radius < 0) {
			ball.velocityY = -ball.velocityY;
			// Correcting the ball position to prevent it from getting stuck
			ball.y =
				ball.y - ball.radius < 0
					? ball.radius
					: canvas.height - ball.radius;
		}

		let player = ball.x < canvas.width / 2 ? user : player2;

		if (collision(ball, user)) {
			ball.speed += speedIncrease;
		}

		if (collision(ball, player2)) {
			ball.speed += speedIncrease;
		}

		if (ball.speed > 30) {
			ball.speed = 30;
		}

		if (collision(ball, player)) {
			let collidePoint =
				(ball.y - (player.y + player.height / 2)) / (player.height / 2);
			let angleRad = (Math.PI / 4) * collidePoint;
			let direction = ball.x < canvas.width / 2 ? 1 : -1;
			ball.velocityX = direction * ball.speed * Math.cos(angleRad);
			ball.velocityY = ball.speed * Math.sin(angleRad);
		}

		if (ball.x - ball.radius < 0) {
			player2.score++;
			resetBall();
		} else if (ball.x + ball.radius > canvas.width) {
			user.score++;
			resetBall();
		}

		if (user.score >= winningScore || player2.score >= winningScore) {
			gameOver(); // Call a function to handle the end of the game
		}
	}

	function collision(b, p) {
		p.top = p.y;
		p.bottom = p.y + p.height;
		p.left = p.x;
		p.right = p.x + p.width;

		b.top = b.y - b.radius;
		b.bottom = b.y + b.radius;
		b.left = b.x - b.radius;
		b.right = b.x + b.radius;

		// Check if ball is moving towards the player or away from them
		let ballMovingTowardsPaddle =
			(b.velocityX < 0 && p === user) ||
			(b.velocityX > 0 && p === player2);

		// Predict the ball's next position based on its velocity
		let nextBallLeft = b.left + b.velocityX;
		let nextBallRight = b.right + b.velocityX;
		let nextBallTop = b.top + b.velocityY;
		let nextBallBottom = b.bottom + b.velocityY;

		// Check collision with the paddle's predicted next position
		return (
			ballMovingTowardsPaddle &&
			p.right > nextBallLeft &&
			p.top < nextBallBottom &&
			p.bottom > nextBallTop &&
			p.left < nextBallRight
		);
	}

	function drawText(text, x, y, color) {
		ctx.fillStyle = color;
		ctx.font = "108px Arial";
		ctx.fillText(text, x, y);
	}

	function render() {
		drawRect(0, 0, canvas.width, canvas.height, "#DC3545"); // Left half
		drawRect(
			canvas.width / 2,
			0,
			canvas.width / 2,
			canvas.height,
			"#3567DC"
		); // Right half
		drawText(
			user.score.toString(),
			canvas.width / 4.7,
			canvas.height / 1.7,
			"white"
		);
		drawText(
			player2.score.toString(),
			(3 * canvas.width) / 4.2,
			canvas.height / 1.7,
			"white"
		);
		drawRect(user.x, user.y, user.width, user.height, user.color); // User paddle
		drawRect(
			player2.x,
			player2.y,
			player2.width,
			player2.height,
			player2.color
		); // Player2 paddle
		drawArc(ball.x, ball.y, ball.radius, ball.color); // Ball
	}

	function game() {
		update();
		render();
	}

	let framePerSecond = 50;
	gameInterval = setInterval(game, 1000 / framePerSecond);

	function gameOver() {
		clearInterval(gameInterval);

		const winner = user.score >= winningScore ? "P1" : "P2";

		const startgametitle = document.getElementById("startgametitle");
		if (startgametitle) startgametitle.innerText = `${winner} wins!`;

		const startgamesubtitle = document.getElementById("startgamesubtitle");
		if (startgamesubtitle) startgamesubtitle.innerText = "Play again?";

		const gamewindow= document.getElementById("gamewindow");
		if (gamewindow) gamewindow.classList.add("d-none");

		const startgame= document.getElementById("startgame");
		if (startgame) startgame.classList.remove("d-none");

		showToast(`${winner} wins!`);
	}

	let userTouchY = 0;
	let player2TouchY = 0;

	function handleTouchStart(event) {
		event.preventDefault(); // Prevents the default scrolling behavior
		for (let i = 0; i < event.touches.length; i++) {
			let touch = event.touches[i];
			if (window.innerWidth <= 800) {
				let touchX = touch.clientY - canvas.offsetTop;
				if (touchX < canvas.height / 2) {
					userTouchY = touch.clientY;
				} else {
					player2TouchY = touch.clientY;
				}
			} else {
				let touchX = touch.clientX - canvas.offsetLeft;
				if (touchX < canvas.width / 2) {
					userTouchY = touch.clientY;
				} else {
					player2TouchY = touch.clientY;
				}
			}
		}
	}

	function handleTouchMove(event) {
		event.preventDefault();
		for (let i = 0; i < event.touches.length; i++) {
			let touch = event.touches[i];
			let touchX, newTouchY;

			if (window.innerWidth <= 800) {
				touchX = touch.clientY - canvas.offsetTop;
				newTouchY = canvas.height - (touch.clientX - canvas.offsetLeft);
			} else {
				touchX = touch.clientX - canvas.offsetLeft;
				newTouchY = touch.clientY - canvas.offsetTop;
			}

			// Check which side of the screen is being touched and update accordingly
			if (touchX < canvas.height / 2) {
				if (newTouchY < userTouchY && user.y > 0) {
					user.y = Math.max(user.y - 8, 0);
				} else if (
					newTouchY > userTouchY &&
					user.y < canvas.height - user.height
				) {
					user.y = Math.min(user.y + 8, canvas.height - user.height);
				}
				userTouchY = newTouchY; // Update the last touch position for user side
			} else {
				if (newTouchY < player2TouchY && player2.y > 0) {
					player2.y = Math.max(player2.y - 8, 0);
				} else if (
					newTouchY > player2TouchY &&
					player2.y < canvas.height - player2.height
				) {
					player2.y = Math.min(
						player2.y + 8,
						canvas.height - player2.height
					);
				}
				player2TouchY = newTouchY; // Update the last touch position for player2 side
			}
		}
	}

	function handleTouchEnd(event) {
		event.preventDefault();
	}

	canvas.addEventListener("touchstart", handleTouchStart, false);
	canvas.addEventListener("touchmove", handleTouchMove, false);
	canvas.addEventListener("touchend", handleTouchEnd, false);
}

// check if url is /game. If not, return and if pong canvas exists, initialize pong
document.addEventListener("DOMContentLoaded", (event) => {
	let observer = new MutationObserver(function (mutations, obs) {
		let pongExist = document.getElementById("gamewindow");
		// check if pong has the class d-none
		if (pongExist) {
			let pongHidden = document
				.getElementById("gamewindow")
				.classList.contains("d-none");
		}

		let url = window.location.pathname;

		if (url == "/game" && pongExist && !pongHidden) {
			winningScore = parseInt(
				document.getElementsByName("numwins")[0].value
			);
			console.log("winningScore: ", winningScore);
			speedIncrease = parseInt(
				document.getElementsByName("ballspeed")[0].value
			);
			console.log("winningScore: ", winningScore);
			console.log("speedIncrease: ", speedIncrease);
			initializePong();
		}
	});

	let config = {
		childList: true,
		subtree: true,
		attributes: true,
		attributeFilter: ["class"],
	};

	observer.observe(document.body, config);
});
