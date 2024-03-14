import { html } from "../../html.js";
// import { setGameMode } from "../../utils/game.js";

export default () => {
	// setGameMode("local");
	return html`
		<div class="d-flex" style="background: #252a2f" id="mainContainer">
			<div style="width: 100%; height: 100svh">
				<div
					id="game_container"
					class="active_container cord-container">
					<game-multiplayer-container></game-multiplayer-container>
				</div>
			</div>
		</div>
	`;
};
