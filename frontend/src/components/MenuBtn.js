import { html } from "../html.js";
import { getData } from "../store.js";

export default (props) => {
	return {
		template: html`
			<div
			class="d-block d-md-none pointer"
			style="
			color: white;
			font-size: 26px;
			padding-top: 25px;
			padding-right: 25px;
			padding-left: 25px;
		"
			id="menu_button">
			<i class="fa fa-bars"></i>
		</div>
		`,
		handlers: [
			{
				selector: "#menu_button",
				event: "click",
				method: function () {
					const navContainer =
						document.querySelector("#nav_container");
					if (navContainer) {
						navContainer.classList.remove("d-none");
					}
				},
			},
		],
	};
};
