import { html } from "../../html.js";
import { loadPage } from "../../router.js";

export default (props) => {
	// set displayProfileMenu to "d-none" to hide the menu
	const { href, name, current, link, nummsg, status, ingame } = props;

	function getTitle(status)
	{
		if (status === "online")
			return "Online";
		else if (status === "offline")
			return "Offline";
		else if (status === "in_game")
			return "In game";
	}

	return {
		template: html`<div
			class="open_chat menu-item mb-2 ${current}"
			style="position: relative">
			<h6
				style="
				margin-bottom: 0px;
				margin-left: 10px;
				position: absolute;
			">
				<div class="d-flex justify-content-center align-items-center">
					<img
						class="rounded-circle mr-3"
						style="width: 30px; height: 30px"
						src="${href}" />${name}
				</div>
			</h6>
			<div
				data-toggle="tooltip"
				data-bss-tooltip=""
				class="status-pill status-${status}"
				title="${getTitle(status)}"
				style="${ingame}"></div>
			<span
				class="badge badge-pill badge-danger"
				style="margin-left: auto; margin-right: 10px"
				>${nummsg}</span
			>
		</div>`,
		handlers: [
			{
				selector: ".menu-item",
				event: "click",
				method: function (event) {
					// Find the closest .menu-item element from the event target
					let menuItem = event.target.closest(".menu-item");

					// If menuItem is null, the click was outside a .menu-item, so do nothing
					if (!menuItem) return;

					// Check if menuItem already has class active
					if (menuItem.classList.contains("active")) return;

					// Find current active menu item and remove its active class
					let currentActive =
						document.querySelector(".menu-item.active");
					if (currentActive) currentActive.classList.remove("active");

					// Add active class to clicked menu item
					menuItem.classList.add("active");

					// Clear text in badge of the clicked menu item
					let badge = menuItem.querySelector(".badge");
					if (badge) badge.innerHTML = "";
				},
			},
			{
				selector: ".open_chat",
				event: "click",
				method: function (event) {
					event.preventDefault();
					loadPage(link);
				},
			},
		],
	};
};
