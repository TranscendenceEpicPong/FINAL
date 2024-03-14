import { html } from "../../html.js";
import { loadPage } from "../../router.js";

export default (props) => {
	// set displayProfileMenu to "d-none" to hide the menu
	const { href, name, current, nummsg, ingame } = props;

	return {
		template: html`
		<div class="menu-item">
			<h6
				style="
			margin-bottom: 0px;
			margin-left: 10px;
		">
				<i class="fa fa-trophy"></i>&nbsp;<nav-link href="/tournament/1" style="color: #aaaaaa;">Tournaments</nav-link>
			</h6>
		</div>`,
	};
};
