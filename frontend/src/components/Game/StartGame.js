import { html } from "../../html.js";
import { loadPage } from "../../router.js";
import { initializePong } from "../../utils/games/local.js";

export default (props) => {
	return {
		template: html`<div
			style="display: flex; justify-content: center; align-items: center;height: 100svh;"
			id="startgame">
			<div
				class="shadow-lg"
				style="background-color:#171a1d;max-width:700px;width:90%;padding:20px;border-radius:10px;color:#dfdfdf;">
				<div class="text-center">
					<h3 class="text-white" id="startgametitle">Let's play</h3>
					<h6 id="startgamesubtitle">Configure your game</h6>
				</div>
				<br />
				<div>
					<custom-input
						id="numwins"
						icon="fas fa-medal"
						type="number"
						required="yes"
						min="1"
						value="1"
						>Number of win</custom-input
					>
				</div>
				<div class="mt-3">
					<custom-input
						id="ballspeed"
						icon="fa fa-tachometer"
						type="number"
						required="yes"
						min="1"
						value="1"
						>Ball speed increase</custom-input
					>
				</div>
				<br />
				<div class="mt-3 d-flex justify-content-between">
					<button type="button" class="btn btn-light" id="backtochat">
						Back to menu
					</button>
					<button
						type="button"
						class="btn btn-primary"
						id="startgamebutton">
						Start game
					</button>
				</div>
			</div>
		</div>`,
		handlers: [
			{
				selector: "#startgamebutton",
				event: "click",
				method: (e) => {
					let numwins = document.querySelector('input[id="numwins"]');
					if (!numwins.validity.valid) {
						showToast(
							"Le nombre de victoire doit être un entier supérieur à 0."
						);
					}

					let ballspeed = document.querySelector(
						'input[id="ballspeed"]'
					);
					if (!ballspeed.validity.valid) {
						showToast(
							"La vitesse de la balle doit être un entier supérieure à 0."
						);
					}

					if (ballspeed.validity.valid && ballspeed.validity.valid) {
						document
							.getElementById("startgame")
							.classList.add("d-none");
						document
							.getElementById("gamewindow")
							.classList.remove("d-none");
						const canva = document.getElementById("canva-pong");
						const context = canva.getContext("2d");
						initializePong(
							canva,
							context,
							parseInt(numwins.value),
							parseInt(ballspeed.value)
						);
					}
				},
			},
			{
				selector: "#backtochat",
				event: "click",
				method: (e) => {
					loadPage("/games");
				},
			},
		],
	};
};
