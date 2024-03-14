import { html } from "../../html.js";
import { initializeSocket, resetSocket, sendToSocket } from "../../utils/socket.js";
import { loadPage } from "../../router.js";

export default (props) => {
	const { mode, textContent } = props;
	return {
		template: html`
			<div id="game-info">
				<div
					class="container d-flex justify-content-center align-items-center"
					style="height:100svh;">
					<div>
						<div class="text-center">
							<p style="color: #aaaaaa;">
								Joueur 1: w et s. Joueur 2: flèche haut, flèche
								bas
							</p>
							<small id="help-start-game" style="color: #aaaaaa;">
								Cliquez sur "Rejoindre / créer" pour commencer
							</small>
							<br />
							<div>
								<button id="backtochat" class="btn btn-light">
									Revenir au chat
								</button>
								<button
									id="btn-start-game"
									class="btn btn-primary">
									Rejoindre / créer
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
			<div id="gamewindow" class="d-none">
				<canvas
					id="canva-pong"
					width="800px"
					height="400px"
					style="background: black;"></canvas>
			</div>
		`,
		handlers: [
			{
				selector: "#btn-start-game",
				event: "click",
				method: (e) => {
					sendToSocket({ action: "join" }, "game");
				},
			},
			{
				selector: "#backtochat",
				event: "click",
				method: () => {
					loadPage("/");
					resetSocket('game');
					setTimeout(() => {
						initializeSocket('game');
					}, 100);
				},
			},
		],
	};
};
