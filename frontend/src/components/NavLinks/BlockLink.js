import { html } from "../../html.js";

export default (props) => {
	return {
		template: html`
		<div class="menu-item">
				<h6
					style="
			margin-bottom: 0px;
			margin-left: 10px;
		">
					<i class="fas fa-ban"></i>&nbsp;<nav-link href="/blocks" style="color: #aaaaaa;">Blocks</nav-link>
				</h6>
		</div>`,
	};
};
