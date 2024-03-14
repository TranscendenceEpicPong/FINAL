import { html } from "../../html.js";

export default (props) => {
	return {
		template: html`
			<div>
				<start-game></start-game>
				<div id="gamewindow" class="d-none">
					<canvas id="canva-pong"></canvas>
				</div>
			</div>
		`,
	};
};
