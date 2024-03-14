import { html } from "../../html.js";
import { loadPage } from "../../router.js";

export default (props) => {
	// set displayProfileMenu to "d-none" to hide the menu
	const { href, icon, pings, textContent } = props;

	return {
		template: html` <div class="menu-item">
			<h6
				style="
			margin-bottom: 0px;
			margin-left: 10px;
		">
				<i class="${icon}"></i>&nbsp;${textContent}
			</h6>
			<span
				class="badge badge-pill badge-danger"
				style="margin-left: auto; margin-right: 10px;"
				>${pings}</span
			>
		</div>`,
		handlers: [
			{
				selector: ".menu-item",
				event: "click",
				method: (e) => {
					loadPage(href);
				},
			},
		],
	};
};